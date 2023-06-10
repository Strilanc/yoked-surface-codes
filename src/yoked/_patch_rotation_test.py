import itertools
from typing import Literal

import pytest
import stim

import gen
from yoked._patch_rotation import patch_rotation_circuit


def assert_observables_hug_boundaries(dem: stim.DetectorErrorModel):
    for instruction in dem:
        if isinstance(instruction, stim.DemRepeatBlock):
            assert_observables_hug_boundaries(instruction.body_copy())
        elif isinstance(instruction, stim.DemInstruction):
            if instruction.type == 'error':
                no = 0
                nd = 0
                for t in instruction.targets_copy() + [stim.target_separator()]:
                    if t.is_separator():
                        if no:
                            assert nd == 1, instruction
                        no = 0
                        nd = 0
                    elif t.is_logical_observable_id():
                        no += 1
                    elif t.is_relative_detector_id():
                        nd += 1
        else:
            raise NotImplementedError(f'{instruction}')


@pytest.mark.parametrize('d,b,opp,style', itertools.product(
    [3, 4, 5],
    ['X', 'Z', 'magic'],
    [False, True],
    ['cz', 'css'],
))
def test_patch_rotation_circuit(d: int, b: Literal['X', 'Z'], opp: bool, style: Literal['cz', 'css']):
    noisy_circuit = patch_rotation_circuit(
        patch_diameter=d,
        pad_rounds=2,
        step_rounds=d,
        time_boundaries=b,
        test_opposite_sides=opp,
    ).with_noise(noise=gen.NoiseModel.uniform_depolarizing(1e-3), style=style)
    assert noisy_circuit.num_observables == 2 if b == 'magic' else 1
    assert_observables_hug_boundaries(noisy_circuit.detector_error_model(decompose_errors=True))
    actual_distance = len(noisy_circuit.shortest_graphlike_error())
    expected_distance = d - 1
    assert actual_distance == expected_distance
