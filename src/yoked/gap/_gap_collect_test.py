import io

import sinter

import gen
from yoked._yoked_memory_circuits import yoked_magic_memory_circuit
from yoked.gap._gap_collect import collect_gap_stats


def test_collect():
    task = sinter.Task(
        circuit=yoked_magic_memory_circuit(
            patch_diameter=5,
            rounds=25,
            noise=gen.NoiseModel.uniform_depolarizing(1e-2),
            yokes=True,
            style='cz',
            num_patches=1,
        ),
        decoder='pymatching',
        json_metadata={'d': 5, 'r': 25, 'p': 1e-3},
    )
    out = io.StringIO()
    collect_gap_stats(
        num_workers=2,
        tasks=[task],
        num_shots=1000,
        out=out,
        print_progress=False,
        print_header=True,
        existing_data={},
        worker_flush_period=5,
    )

    out.seek(0)
    data = out.read()
    assert data.startswith(sinter.CSV_HEADER)
    assert ''',""C''' in data and ''',""E''' in data
