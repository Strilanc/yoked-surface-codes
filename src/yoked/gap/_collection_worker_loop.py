import os
import sys
from typing import Optional, TYPE_CHECKING

from yoked.gap._collection_work_handler import CollectionWorkHandler
from yoked.gap._collection_worker_state import CollectionWorkerState

if TYPE_CHECKING:
    import multiprocessing


def collection_worker_loop(flush_period: float,
                           worker_id: int,
                           work_handler: CollectionWorkHandler,
                           inp: 'multiprocessing.Queue',
                           out: 'multiprocessing.Queue',
                           core_affinity: Optional[int]) -> None:
    try:
        if core_affinity is not None and hasattr(os, 'sched_setaffinity'):
            os.sched_setaffinity(0, {core_affinity})
    except:
        # If setting the core affinity fails, we keep going regardless.
        pass

    worker = CollectionWorkerState(
        flush_period=flush_period,
        worker_id=worker_id,
        work_handler=work_handler,
        inp=inp,
        out=out,
    )
    worker.run_message_loop()
