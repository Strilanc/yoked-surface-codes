import queue
import sys
import time
from typing import Optional, TYPE_CHECKING

import sinter
import stim

from yoked.gap._collection_work_handler import CollectionWorkHandler

if TYPE_CHECKING:
    import multiprocessing


def _fill_in_task(task: sinter.Task) -> sinter.Task:
    changed = False
    circuit = task.circuit
    if circuit is None:
        circuit = stim.Circuit.from_file(task.circuit_path)
        changed = True
    dem = task.detector_error_model
    if dem is None:
        dem = circuit.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True)
        changed = True
    if not changed:
        return task
    return sinter.Task(
        circuit=circuit,
        decoder=task.decoder,
        detector_error_model=dem,
        postselection_mask=task.postselection_mask,
        postselected_observables_mask=task.postselected_observables_mask,
        json_metadata=task.json_metadata,
        collection_options=task.collection_options,
    )


class CollectionWorkerState:
    def __init__(
            self,
            *,
            flush_period: float,
            worker_id: int,
            work_handler: CollectionWorkHandler,
            inp: 'multiprocessing.Queue',
            out: 'multiprocessing.Queue'
    ):
        self.flush_period = flush_period
        self.inp = inp
        self.out = out
        self.work_handler = work_handler
        self.worker_id = worker_id

        self.current_task: Optional[sinter.Task] = None
        self.current_task_shots_left: int = 0
        self.unflushed_results: sinter.AnonTaskStats = sinter.AnonTaskStats()
        self.last_flush_message_time = time.monotonic()

    def flush_results(self):
        if self.unflushed_results.shots > 0:
            self.last_flush_message_time = time.monotonic()
            self.out.put((
                'flushed_results',
                self.worker_id,
                (self.current_task.strong_id(), self.unflushed_results),
            ))
            self.unflushed_results = sinter.AnonTaskStats()

    def accept_shots(self, *, shots_delta: int):
        self.current_task_shots_left += shots_delta
        self.out.put((
            'accepted_shots',
            self.worker_id,
            (self.current_task.strong_id(), shots_delta),
        ))

    def return_shots(self, *, requested_shots: int):
        returned_shots = min(requested_shots, self.current_task_shots_left)
        self.current_task_shots_left -= returned_shots
        self.out.put((
            'returned_shots',
            self.worker_id,
            (self.current_task.strong_id(), returned_shots),
        ))

    def compute_strong_id(self, *, new_task: sinter.Task):
        strong_id = _fill_in_task(new_task).strong_id()
        self.out.put((
            'computed_strong_id',
            self.worker_id,
            strong_id,
        ))

    def change_job(self, *, new_task: sinter.Task, new_shots: int):
        self.flush_results()

        self.current_task = _fill_in_task(new_task)
        assert self.current_task.strong_id() is not None
        self.current_task_shots_left = new_shots
        self.last_flush_message_time = time.monotonic()

        self.out.put((
            'changed_job',
            self.worker_id,
            (self.current_task.strong_id(), self.current_task_shots_left),
        ))

    def process_messages(self) -> int:
        num_processed = 0
        while True:
            try:
                message = self.inp.get_nowait()
            except queue.Empty:
                return num_processed

            num_processed += 1
            message_type, message_body = message

            if message_type == 'stop':
                return -1

            elif message_type == 'flush_results':
                self.flush_results()

            elif message_type == 'compute_strong_id':
                assert isinstance(message_body, sinter.Task)
                self.compute_strong_id(new_task=message_body)

            elif message_type == 'change_job':
                new_task, new_shots = message_body
                assert isinstance(new_task, sinter.Task)
                assert isinstance(new_shots, int)
                self.change_job(new_task=new_task, new_shots=new_shots)

            elif message_type == 'accept_shots':
                job_key, shift = message_body
                assert isinstance(shift, int)
                assert job_key == self.current_task.strong_id()
                self.accept_shots(shots_delta=shift)

            elif message_type == 'return_shots':
                job_key, requested_shots = message_body
                assert isinstance(requested_shots, int)
                assert job_key == self.current_task.strong_id()
                self.return_shots(requested_shots=requested_shots)

            else:
                raise NotImplementedError(f'{message_type=}')

    def do_some_work(self) -> bool:
        did_some_work = False

        if self.current_task_shots_left > 0:
            some_work_done = self.work_handler.do_some_work(self.current_task, self.current_task_shots_left)
            assert isinstance(some_work_done, sinter.AnonTaskStats)
            assert some_work_done.shots <= self.current_task_shots_left
            self.current_task_shots_left -= some_work_done.shots
            self.unflushed_results += some_work_done
            did_some_work = True

        if self.unflushed_results.shots > 0 and (self.current_task_shots_left == 0 or self.last_flush_message_time + self.flush_period < time.monotonic()):
            self.flush_results()
            did_some_work = True

        return did_some_work

    def run_message_loop(self):
        try:
            while True:
                num_messages_processed = self.process_messages()
                if num_messages_processed == -1:
                    break
                did_some_work = self.do_some_work()
                if not did_some_work and num_messages_processed == 0:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            pass

        except BaseException as ex:
            import traceback
            self.out.put((
                'stopped_due_to_exception',
                self.worker_id,
                (None if self.current_task is None else self.current_task.strong_id(), self.current_task_shots_left, self.unflushed_results, traceback.format_exc(), ex),
            ))
