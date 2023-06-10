import collections
import multiprocessing
import time
from typing import Any, List

import numpy as np
import sinter
import stim

from yoked.gap._collection_work_handler import CollectionWorkHandler
from yoked.gap._collection_worker_state import CollectionWorkerState


class MockWorkHandler(CollectionWorkHandler):
    def __init__(self):
        self.expected = collections.deque()

    def do_some_work(self, request: sinter.Task, max_shots: int) -> sinter.AnonTaskStats:
        assert self.expected
        expected_request, expected_shots, response = self.expected.popleft()
        assert request == expected_request
        assert max_shots == expected_shots
        return response


def _assert_drain_queue(q: multiprocessing.Queue, expected_contents: List[Any]):
    for v in expected_contents:
        assert q.get(timeout=0.1) == v
    assert q.empty()


def _put_wait_not_empty(q: multiprocessing.Queue, item: Any):
    q.put(item)
    while q.empty():
        time.sleep(0.0001)


def test_worker_stop():
    handler = MockWorkHandler()

    inp = multiprocessing.Queue()
    out = multiprocessing.Queue()
    inp.cancel_join_thread()
    out.cancel_join_thread()

    worker = CollectionWorkerState(
        flush_period=-1,
        worker_id=5,
        work_handler=handler,
        inp=inp,
        out=out,
    )

    assert worker.process_messages() == 0
    _assert_drain_queue(out, [])

    t0 = sinter.Task(
        circuit=stim.Circuit('H 0'),
        detector_error_model=stim.DetectorErrorModel(),
        decoder='fusion_blossom',
        collection_options=sinter.CollectionOptions(max_shots=100_000_000),
        json_metadata={'a': 3},
    )

    _put_wait_not_empty(inp, ('change_job', (t0, 0)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [('changed_job', 5, (t0.strong_id(), 0))])

    _put_wait_not_empty(inp, ('stop', None))
    assert worker.process_messages() == -1


def test_worker_skip_work():
    handler = MockWorkHandler()

    inp = multiprocessing.Queue()
    out = multiprocessing.Queue()
    inp.cancel_join_thread()
    out.cancel_join_thread()

    worker = CollectionWorkerState(
        flush_period=-1,
        worker_id=5,
        work_handler=handler,
        inp=inp,
        out=out,
    )

    assert worker.process_messages() == 0
    _assert_drain_queue(out, [])

    t0 = sinter.Task(
        circuit=stim.Circuit('H 0'),
        detector_error_model=stim.DetectorErrorModel(),
        decoder='fusion_blossom',
        collection_options=sinter.CollectionOptions(max_shots=100_000_000),
        json_metadata={'a': 3},
    )
    _put_wait_not_empty(inp, ('change_job', (t0, 0)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [('changed_job', 5, (t0.strong_id(), 0))])

    _put_wait_not_empty(inp, ('accept_shots', (t0.strong_id(), 10000)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [('accepted_shots', 5, (t0.strong_id(), 10000))])

    assert worker.current_task == t0
    assert worker.current_task_shots_left == 10000
    assert worker.process_messages() == 0
    _assert_drain_queue(out, [])

    _put_wait_not_empty(inp, ('return_shots', (t0.strong_id(), 2000)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [
        ('returned_shots', 5, (t0.strong_id(), 2000)),
    ])

    _put_wait_not_empty(inp, ('return_shots', (t0.strong_id(), 20000000)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [
        ('returned_shots', 5, (t0.strong_id(), 8000)),
    ])

    assert not worker.do_some_work()


def test_worker_finish_work():
    handler = MockWorkHandler()

    inp = multiprocessing.Queue()
    out = multiprocessing.Queue()
    inp.cancel_join_thread()
    out.cancel_join_thread()

    worker = CollectionWorkerState(
        flush_period=-1,
        worker_id=5,
        work_handler=handler,
        inp=inp,
        out=out,
    )

    assert worker.process_messages() == 0
    _assert_drain_queue(out, [])

    ta = sinter.Task(
        circuit=stim.Circuit('H 0'),
        detector_error_model=stim.DetectorErrorModel(),
        decoder='fusion_blossom',
        collection_options=sinter.CollectionOptions(max_shots=100_000_000),
        json_metadata={'a': 3},
    )
    _put_wait_not_empty(inp, ('change_job', (ta, 10000)))
    assert worker.process_messages() == 1
    _assert_drain_queue(out, [('changed_job', 5, (ta.strong_id(), 10000))])

    assert worker.current_task == ta
    assert worker.current_task_shots_left == 10000
    assert worker.process_messages() == 0
    _assert_drain_queue(out, [])

    handler.expected.append((
        ta,
        10000,
        sinter.AnonTaskStats(
            shots=1000,
            errors=23,
            discards=0,
            seconds=1,
        ),
    ))
    assert worker.do_some_work()
    _assert_drain_queue(out, [
        ('flushed_results', 5, (ta.strong_id(), sinter.AnonTaskStats(shots=1000, errors=23, discards=0, seconds=1)))])

    handler.expected.append((
        ta,
        9000,
        sinter.AnonTaskStats(
            shots=9000,
            errors=13,
            discards=0,
            seconds=1,
        ),
    ))

    assert worker.do_some_work()
    _assert_drain_queue(out, [
        ('flushed_results', 5, (ta.strong_id(), sinter.AnonTaskStats(
            shots=9000,
            errors=13,
            discards=0,
            seconds=1,
        ))),
    ])
    assert not worker.do_some_work()
    _assert_drain_queue(out, [])
