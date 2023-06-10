from typing import Any, TextIO, Dict, List, Optional

import sinter
from sinter._printer import ThrottledProgressPrinter

from yoked.gap._collection_manager import CollectionManager
from yoked.gap._gap_worker_handler import GapWorkHandler


def collect_gap_stats(
        *,
        num_workers: int,
        tasks: List[sinter.Task],
        existing_data: Dict[Any, sinter.TaskStats],
        worker_flush_period: float,
        num_shots: int,
        out: TextIO,
        print_progress: bool,
        print_header: bool,
) -> None:
    starting = True
    printer = ThrottledProgressPrinter(outs=[out], print_progress=print_progress, min_progress_delay=0.1)
    printer.show_latest_progress(f"Starting {num_workers} workers...")

    for task in tasks:
        assert task.decoder == 'pymatching'

    total_collected = {k: v.to_anon_stats() for k, v in existing_data.items()}

    def progress_callback(stat: Optional[sinter.TaskStats]):
        if stat is not None:
            total_collected[stat.strong_id] += stat.to_anon_stats()
            printer.print_out(str(stat))
        show_progress()

    def show_progress():
        if starting:
            printer.show_latest_progress(f"Analyzed {sum(e is not None for e in m.task_strong_ids)}/{len(tasks)} circuits...")
            return

        tasks_left = 0
        lines = []
        for k, strong_id in enumerate(m.task_strong_ids):
            c = total_collected[strong_id]
            if c.shots >= num_shots:
                continue
            tasks_left += 1
            w = len(m.task_states[strong_id].workers_assigned)
            dt = None if c.shots == 0 else round(c.seconds / c.shots * (num_shots - c.shots) / 60)
            lines.append(
                f'     '
                f'workers={w} '
                f'core_mins_left={dt} '
                f'shots_left={num_shots - c.shots} '
                f'errors={c.errors} ' + ",".join(f"{k}={v}" for k, v in m.partial_tasks[k].json_metadata.items()))
        msg = f'{tasks_left} tasks left:\n' + '\n'.join(lines)
        printer.show_latest_progress(msg + '\n')

    m = CollectionManager(
        existing_data=existing_data,
        collection_options=sinter.CollectionOptions(max_shots=num_shots),
        work_handler=GapWorkHandler(),
        num_workers=num_workers,
        worker_flush_period=worker_flush_period,
        tasks=tasks,
        progress_callback=progress_callback,
    )

    m.start_workers()

    printer.show_latest_progress(f"Analyzing {len(tasks)} circuits...")
    m.start_distributing_work()
    starting = False

    for strong_id in m.task_strong_ids:
        if strong_id not in total_collected:
            total_collected[strong_id] = sinter.AnonTaskStats()
    if print_header:
        printer.print_out(sinter.CSV_HEADER)

    show_progress()
    m.run_until_done()

    printer.show_latest_progress(f'Done')
    printer.flush()
