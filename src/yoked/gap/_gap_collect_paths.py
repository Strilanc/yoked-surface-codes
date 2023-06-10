import contextlib
import pathlib
import sys
from typing import Optional, List

import sinter

from yoked.gap import collect_gap_stats


def collect_circuit_paths(
        circuit_paths: List[str],
        existing_data: List[str],
        max_shots: int,
        out_path: Optional[str],
        save_resume_filepath: Optional[str],
        processes: int,
        flush_period: float,
):
    with contextlib.ExitStack() as ctx:
        existing_data_dict = None
        print_header = True
        if save_resume_filepath is not None:
            assert out_path is None
            if pathlib.Path(save_resume_filepath).exists():
                msg = f"Reading existing data at {save_resume_filepath}..."
                print('\033[31m' + msg + '\033[0m', file=sys.stderr, flush=True)
                existing_data_dict = {
                    stat.strong_id: stat
                    for stat in sinter.read_stats_from_csv_files(save_resume_filepath, *existing_data)
                }
                print_header = False
                out = ctx.enter_context(open(save_resume_filepath, 'a'))
            else:
                out = ctx.enter_context(open(save_resume_filepath, 'w'))
        elif out_path is None:
            out = sys.stdout
        else:
            out = ctx.enter_context(open(out_path, 'w'))
        if existing_data_dict is None:
            existing_data_dict = {
                stat.strong_id: stat
                for stat in sinter.read_stats_from_csv_files(*existing_data)
            }

        tasks = [
            sinter.Task(
                circuit_path=pathlib.Path(circuit_path).absolute(),
                json_metadata=sinter.comma_separated_key_values(circuit_path),
                decoder='pymatching',
            )
            for circuit_path in circuit_paths
        ]

        collect_gap_stats(
            num_workers=processes,
            tasks=tasks,
            num_shots=max_shots,
            out=out,
            print_header=print_header,
            existing_data=existing_data_dict,
            print_progress=True,
            worker_flush_period=flush_period,
        )
