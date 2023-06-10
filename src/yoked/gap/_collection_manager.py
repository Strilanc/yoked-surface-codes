import collections
import multiprocessing
import os
import queue
from typing import Any, Optional, List, Dict, Iterable, Callable, Tuple

import sinter

from yoked.gap._collection_work_handler import CollectionWorkHandler
from yoked.gap._collection_worker_loop import collection_worker_loop


class _ManagedWorkerState:
    def __init__(self, worker_id: int):
        self.worker_id: int = worker_id
        self.process: Optional[multiprocessing.Process] = None
        self.input_queue: Optional[multiprocessing.Queue[Tuple[str, Any]]] = None
        self.assigned_work_key: Any = None
        self.assigned_shots: int = 0
        self.asked_to_drop_shots: int = 0


class _ManagedTaskState:
    def __init__(self, *, partial_task: sinter.Task, strong_id: str, shots_left: int):
        self.partial_task = partial_task
        self.strong_id = strong_id
        self.shots_left = shots_left
        self.shots_unassigned = shots_left
        self.shot_return_requests = 0
        self.workers_assigned = []


class CollectionManager:
    def __init__(
            self,
            *,
            existing_data: Dict[Any, sinter.TaskStats],
            collection_options: sinter.CollectionOptions,
            work_handler: CollectionWorkHandler,
            num_workers: int,
            worker_flush_period: float,
            tasks: Iterable[sinter.Task],
            progress_callback: Callable[[Optional[sinter.TaskStats]], None],
    ):
        self.existing_data = existing_data
        self.num_workers: int = num_workers
        self.work_handler: CollectionWorkHandler = work_handler
        self.worker_flush_period: float = worker_flush_period
        self.progress_callback = progress_callback
        self.collection_options = collection_options
        self.partial_tasks = list(tasks)
        self.task_strong_ids: List[Optional[str]] = [None] * len(self.partial_tasks)

        self.started: bool = False
        self.shared_worker_output_queue: Optional[multiprocessing.SimpleQueue[Tuple[str, int, Any]]] = None
        self.worker_states: List[_ManagedWorkerState] = [_ManagedWorkerState(k) for k in range(self.num_workers)]
        self.task_states: Dict[Any, _ManagedTaskState] = {}

    def start_workers(self, *, actually_start_worker_processes: bool = True):
        assert not self.started
        self.started = True
        current_method = multiprocessing.get_start_method()
        try:
            # To ensure the child processes do not accidentally share ANY state
            # related to, we use 'spawn' instead of 'fork'.
            multiprocessing.set_start_method('spawn', force=True)
            # Create queues after setting start method to work around a deadlock
            # bug that occurs otherwise.
            self.shared_worker_output_queue = multiprocessing.SimpleQueue()

            num_cpus = os.cpu_count()
            for worker_id in range(self.num_workers):
                worker_state = self.worker_states[worker_id]
                worker_state.input_queue = multiprocessing.Queue()
                worker_state.input_queue.cancel_join_thread()
                worker_state.assigned_work_key = None
                worker_state.process = multiprocessing.Process(
                    target=collection_worker_loop,
                    args=(
                        self.worker_flush_period,
                        worker_id,
                        self.work_handler,
                        worker_state.input_queue,
                        self.shared_worker_output_queue,
                        worker_id % num_cpus,
                    ),
                )

                if actually_start_worker_processes:
                    worker_state.process.start()
        finally:
            multiprocessing.set_start_method(current_method, force=True)

    def start_distributing_work(self):
        self._compute_task_ids()
        self._distribute_work()

    def _compute_task_ids(self):
        idle_worker_ids = list(range(self.num_workers))
        unknown_task_ids = list(range(len(self.partial_tasks)))
        worker_to_task_map = {}
        while worker_to_task_map or unknown_task_ids:
            while idle_worker_ids and unknown_task_ids:
                worker_id = idle_worker_ids.pop()
                unknown_task_id = unknown_task_ids.pop()
                worker_to_task_map[worker_id] = unknown_task_id
                self.worker_states[worker_id].input_queue.put(('compute_strong_id', self.partial_tasks[unknown_task_id]))

            try:
                message = self.shared_worker_output_queue.get()
                message_type, worker_id, message_body = message
                if message_type == 'computed_strong_id':
                    assert worker_id in worker_to_task_map
                    assert isinstance(message_body, str)
                    self.task_strong_ids[worker_to_task_map.pop(worker_id)] = message_body
                    idle_worker_ids.append(worker_id)
                elif message_type == 'stopped_due_to_exception':
                    cur_task, cur_shots_left, unflushed_work_done, traceback, ex = message_body
                    raise ValueError(f'Worker failed: traceback={traceback}') from ex
                else:
                    raise NotImplementedError(f'{message_type=}')
                self.progress_callback(None)
            except queue.Empty:
                pass

        assert len(idle_worker_ids) == self.num_workers
        seen = set()
        for k in range(len(self.partial_tasks)):
            options = self.partial_tasks[k].collection_options.combine(self.collection_options)
            key: str = self.task_strong_ids[k]
            if key in seen:
                raise ValueError(f'Same task given twice: {self.partial_tasks[k]!r}')
            seen.add(key)

            shots_left = options.max_shots
            if key in self.existing_data:
                shots_left -= self.existing_data[key].shots
            if shots_left <= 0:
                continue
            self.task_states[key] = _ManagedTaskState(partial_task=self.partial_tasks[k], strong_id=key, shots_left=shots_left)

    def hard_stop(self):
        if not self.started:
            return

        removed_workers = [state.process for state in self.worker_states]
        for state in self.worker_states:
            state.process = None
            state.assigned_work_key = None
            state.input_queue = None
        self.shared_worker_output_queue = None
        self.started = False
        self.task_states.clear()

        # SIGKILL everything.
        for w in removed_workers:
            w.kill()
        # Wait for them to be done.
        for w in removed_workers:
            w.join()

    def _try_del_task(self, task_id: Any):
        task_state = self.task_states[task_id]
        if task_state.shots_left > 0 or task_state.shot_return_requests > 0:
            self._distribute_work_within_a_job(task_state)
            return
        for worker_id in task_state.workers_assigned:
            worker_state = self.worker_states[worker_id]
            assert worker_state.assigned_work_key == task_id
            assert worker_state.assigned_shots == 0
            assert not worker_state.asked_to_drop_shots
            worker_state.assigned_work_key = None
        del self.task_states[task_id]
        self._distribute_work()

    def state_summary(self) -> str:
        lines = []
        for worker_id, worker in enumerate(self.worker_states):
            lines.append(f'worker {worker_id}:'
                         f' asked_to_drop_shots={worker.asked_to_drop_shots}'
                         f' assigned_shots={worker.assigned_shots}'
                         f' assigned_work_key={worker.assigned_work_key}')
        for task in self.task_states.values():
            lines.append(f'task {task.strong_id=}:\n'
                         f'    workers_assigned={task.workers_assigned}\n'
                         f'    shot_return_requests={task.shot_return_requests}\n'
                         f'    shots_left={task.shots_left}\n'
                         f'    shots_unassigned={task.shots_unassigned}')
        return '\n' + '\n'.join(lines) + '\n'

    def process_message(self) -> bool:
        try:
            message = self.shared_worker_output_queue.get()
        except queue.Empty:
            return False

        message_type, worker_id, message_body = message
        worker_state = self.worker_states[worker_id]

        if message_type == 'flushed_results':
            task_strong_id, anon_stat = message_body
            assert isinstance(anon_stat, sinter.AnonTaskStats)
            assert worker_state.assigned_work_key == task_strong_id
            task_state = self.task_states[task_strong_id]
            assert worker_state.assigned_shots >= anon_stat.shots
            worker_state.assigned_shots -= anon_stat.shots
            task_state.shots_left -= anon_stat.shots

            stat = sinter.TaskStats(
                strong_id=task_state.strong_id,
                decoder=task_state.partial_task.decoder,
                json_metadata=task_state.partial_task.json_metadata,
                shots=anon_stat.shots,
                discards=anon_stat.discards,
                seconds=anon_stat.seconds,
                errors=anon_stat.errors,
                custom_counts=anon_stat.custom_counts,
            )

            self._try_del_task(task_strong_id)

            self.progress_callback(stat)

        elif message_type == 'changed_job':
            pass

        elif message_type == 'accepted_shots':
            pass

        elif message_type == 'returned_shots':
            task_key, shots_returned = message_body
            assert isinstance(shots_returned, int)
            assert worker_state.assigned_work_key == task_key
            assert worker_state.asked_to_drop_shots
            task_state = self.task_states[task_key]
            task_state.shot_return_requests -= 1
            worker_state.asked_to_drop_shots = 0
            task_state.shots_unassigned += shots_returned
            worker_state.assigned_shots -= shots_returned
            self._try_del_task(task_key)

        elif message_type == 'stopped_due_to_exception':
            cur_task, cur_shots_left, unflushed_work_done, traceback, ex = message_body
            raise ValueError(f'Worker failed: traceback={traceback}') from ex

        else:
            raise NotImplementedError(f'{message_type=}')

        return True

    def run_until_done(self):
        try:
            while self.task_states:
                self.process_message()

        except KeyboardInterrupt:
            pass

        finally:
            self.hard_stop()

    def _distribute_idle_workers_to_jobs(self):
        idle_workers = [
            w
            for w in range(self.num_workers)[::-1]
            if self.worker_states[w].assigned_work_key is None and not self.worker_states[w].asked_to_drop_shots
        ]
        if not idle_workers or not self.started:
            return

        groups = collections.defaultdict(list)
        for work_state in self.task_states.values():
            if work_state.shots_left > 0:
                groups[len(work_state.workers_assigned)].append(work_state)
        for k in groups.keys():
            groups[k] = groups[k][::-1]
        if not groups:
            return
        min_assigned = min(groups.keys(), default=0)

        # Distribute workers to unfinished jobs with the fewest workers.
        while idle_workers:
            task_state: _ManagedTaskState = groups[min_assigned].pop()
            groups[min_assigned + 1].append(task_state)
            if not groups[min_assigned]:
                min_assigned += 1

            worker_id = idle_workers.pop()
            task_state.workers_assigned.append(worker_id)
            worker_state = self.worker_states[worker_id]
            worker_state.assigned_work_key = task_state.strong_id
            worker_state.input_queue.put((
                'change_job',
                (task_state.partial_task, 0),
            ))

    def _distribute_unassigned_work_to_workers_within_a_job(self, task_state: _ManagedTaskState):
        if not self.started or not task_state.workers_assigned or task_state.shots_left <= 0:
            return

        w = len(task_state.workers_assigned)
        expected_work_per_worker = (task_state.shots_left + w - 1) // w

        # Give unassigned shots to idle workers.
        for worker_id in sorted(task_state.workers_assigned, key=lambda w: self.worker_states[w].assigned_shots):
            worker_state = self.worker_states[worker_id]
            if worker_state.assigned_shots < expected_work_per_worker:
                shots_to_assign = min(expected_work_per_worker - worker_state.assigned_shots,
                                      task_state.shots_unassigned)
                if shots_to_assign > 0:
                    task_state.shots_unassigned -= shots_to_assign
                    worker_state.assigned_shots += shots_to_assign
                    worker_state.input_queue.put((
                        'accept_shots',
                        (task_state.strong_id, shots_to_assign),
                    ))

    def _take_work_if_unsatisfied_workers_within_a_job(self, task_state: _ManagedTaskState):
        if not self.started or not task_state.workers_assigned or task_state.shots_left <= 0:
            return

        if all(self.worker_states[w].assigned_shots for w in task_state.workers_assigned):
            return

        w = len(task_state.workers_assigned)
        expected_work_per_worker = (task_state.shots_left + w - 1) // w

        # There are idle workers that couldn't be given any shots. Take shots from other workers.
        for worker_id in sorted(task_state.workers_assigned, key=lambda w: self.worker_states[w].assigned_shots, reverse=True):
            worker_state = self.worker_states[worker_id]
            if worker_state.asked_to_drop_shots or worker_state.assigned_shots <= expected_work_per_worker + 128:
                continue
            shots_to_take = worker_state.assigned_shots - expected_work_per_worker
            assert shots_to_take > 0
            worker_state.asked_to_drop_shots = shots_to_take
            task_state.shot_return_requests += 1
            worker_state.input_queue.put((
                'return_shots',
                (task_state.strong_id, shots_to_take),
            ))

    def _distribute_work_within_a_job(self, w: _ManagedTaskState):
        self._distribute_unassigned_work_to_workers_within_a_job(w)
        self._take_work_if_unsatisfied_workers_within_a_job(w)

    def _distribute_work(self):
        self._distribute_idle_workers_to_jobs()
        for w in self.task_states.values():
            self._distribute_work_within_a_job(w)
