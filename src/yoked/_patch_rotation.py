import dataclasses
from typing import Literal, Iterable, Optional

import stim

import gen


class MagicableCircuit:
    def __init__(
            self,
            *,
            noiseless_qubit_indices: Iterable[int] = (),
            noiseless_start: Optional[stim.Circuit] = None,
            noisy_body: stim.Circuit,
            noiseless_end: Optional[stim.Circuit] = None,
            steps: gen.StepSequenceOutline,
    ):
        self.noiseless_qubit_indices = frozenset(noiseless_qubit_indices)
        self.noiseless_start = noiseless_start
        self.noiseless_end = noiseless_end
        self.noisy_body = noisy_body
        self.steps = steps

    def is_magic(self) -> bool:
        return len(self.noiseless_qubit_indices) > 0 or self.noiseless_start is not None or self.noiseless_end is not None

    def with_noise(self, *, style: Literal['css', 'cz'], noise: Optional[gen.NoiseModel]) -> stim.Circuit:
        if style == 'cz':
            body = gen.transpile_to_z_basis_interaction_circuit(self.noisy_body, is_entire_circuit=not self.is_magic())
        elif style == 'css':
            body = self.noisy_body
        else:
            raise NotImplementedError(f'{style=}')
        if noise is not None:
            body = noise.noisy_circuit(body, immune_qubits=self.noiseless_qubit_indices)
        if self.noiseless_start is not None:
            body = self.noiseless_start + body
        if self.noiseless_end is not None:
            body = body + self.noiseless_end
        return body


def patch_rotation_circuit(
        *,
        patch_diameter: int,
        pad_rounds: int,
        step_rounds: int,
        time_boundaries: Literal['X', 'Z', 'magic'],
        test_opposite_sides: bool = False,
) -> MagicableCircuit:
    g = patch_diameter - 1
    left_tl = 0
    left_tr = g
    left_br = g + g*1j
    left_bl = g*1j
    right_tl = left_tl + g
    right_tr = left_tr + g
    right_br = left_br + g
    right_bl = left_bl + g

    ancillas = {-2 - 2j} if time_boundaries == 'magic' else set()
    step0_in = gen.StepOutline(
        start=gen.PatchTransitionOutline(
            observable_deltas={
                'ObsX:top->right': gen.PathOutline.from_stops('X', [left_tl, left_tr], extra=ancillas),
                'ObsX:bottom->left': gen.PathOutline.from_stops('X', [left_bl, left_br], extra=ancillas),
                'ObsZ:right->bottom': gen.PathOutline.from_stops('Z', [left_tr, left_br], extra=ancillas),
                'ObsZ:left->top': gen.PathOutline.from_stops('Z', [left_tl, left_bl], extra=ancillas),
            },
            data_boundary_planes=[gen.ClosedCurve.from_cycle([
                time_boundaries,
                left_tl,
                left_tr,
                left_br,
                left_bl,
            ])] if time_boundaries != 'magic' else [],
        ),
        body=gen.PatchOutline([
            gen.ClosedCurve.from_cycle([
                left_tl,
                'Z',
                left_tr,
                'X',
                left_br,
                'Z',
                left_bl,
                'X',
            ])
        ]),
        rounds=pad_rounds,
    )
    step1_lz = gen.StepOutline(
        start=gen.PatchTransitionOutline(
            observable_deltas={
                'ObsX:top->right': gen.PathOutline.from_stops('X', [left_tr + 1, right_tr, right_br]),
            },
            data_boundary_planes=[
                gen.ClosedCurve.from_cycle([
                    'X',
                    left_tr + 1,
                    right_tr,
                    right_br,
                    left_br + 1,
                ])
            ]
        ),
        obs_delta_body_start={
            'ObsZ:right->bottom': gen.ClosedCurve.from_cycle([
                'Z',
                left_tr,
                right_tr,
                right_br,
                left_br,
            ]),
        },
        obs_delta_body_end={
            'ObsZ:left->top': gen.ClosedCurve.from_cycle([
                'Z',
                left_tl,
                right_tr,
            ]),
        },
        body=gen.PatchOutline([
            gen.ClosedCurve.from_cycle([
                left_tl,
                'Z',
                right_tr,
                'Z',
                right_br,
                'X',
                left_br,
                'Z',
                left_bl,
                'X',
            ])
        ]),
        rounds=step_rounds,
    )
    step2_lx = gen.StepOutline(
        body=gen.PatchOutline(
            region_curves=[
                gen.ClosedCurve.from_cycle([
                    left_tl,
                    'X',
                    right_tr,
                    'Z',
                    right_br,
                    'X',
                    left_br,
                    'Z',
                    left_bl,
                    'X',
                ])
            ],
        ),
        obs_delta_body_start={
            'ObsX:top->right': gen.ClosedCurve.from_cycle([
                'X', left_tl, right_tr,
            ]),
        },
        obs_delta_body_end={
            'ObsX:bottom->left': gen.ClosedCurve.from_cycle([
                'X',
                left_tl,
                right_tl,
                right_bl,
                left_bl,
            ]),
        },
        end=gen.PatchTransitionOutline(
            observable_deltas={
                'ObsZ:left->top': gen.PathOutline.from_stops('Z', [right_tl - 1, left_tl, left_bl]),
            },
            data_boundary_planes=[
                gen.ClosedCurve.from_cycle([
                    'Z',
                    left_tl,
                    right_tl - 1,
                    right_bl - 1,
                    left_bl,
                ])
            ]
        ),
        rounds=step_rounds,
    )
    step3_out = gen.StepOutline(
        body=gen.PatchOutline([
            gen.ClosedCurve.from_cycle([
                right_tl,
                'X',
                right_tr,
                'Z',
                right_br,
                'X',
                right_bl,
                'Z',
            ])
        ]),
        end=gen.PatchTransitionOutline(
            observable_deltas={
                'ObsX:top->right': gen.PathOutline.from_stops('X', [right_tr, right_br], extra=ancillas),
                'ObsX:bottom->left': gen.PathOutline.from_stops('X', [right_tl, right_bl], extra=ancillas),
                'ObsZ:right->bottom': gen.PathOutline.from_stops('Z', [right_bl, right_br], extra=ancillas),
                'ObsZ:left->top': gen.PathOutline.from_stops('Z', [right_tl, right_tr], extra=ancillas),
            },
            data_boundary_planes=[gen.ClosedCurve.from_cycle([
                time_boundaries,
                right_tl,
                right_tr,
                right_br,
                right_bl,
            ])] if time_boundaries != 'magic' else [],
        ),
        rounds=pad_rounds,
    )

    normal_steps = [
        step0_in,
        step1_lz,
        step2_lx,
        step3_out,
    ]

    rel_order_func_start = lambda m: gen.Order_Z if gen.checkerboard_basis(m) == 'Z' else gen.Order_ᴎ
    rel_order_func_end = lambda m: gen.Order_ᴎ if gen.checkerboard_basis(m) == 'Z' else gen.Order_Z
    builder = gen.Builder.for_qubits({q for step in normal_steps for q in step.used_set} | ancillas)
    round_index = 0
    cur_obs = {
        'ObsX:top->right': set(),
        'ObsZ:right->bottom': set(),
        'ObsX:bottom->left': set(),
        'ObsZ:left->top': set(),
    }
    o2i = {
        'ObsX:top->right': {'X': 0, 'Z': None, 'magic': 0}[time_boundaries] if test_opposite_sides else None,
        'ObsX:bottom->left': {'X': 0, 'Z': None, 'magic': 0}[time_boundaries] if not test_opposite_sides else None,
        'ObsZ:right->bottom': {'X': None, 'Z': 0, 'magic': 1}[time_boundaries] if test_opposite_sides else None,
        'ObsZ:left->top': {'X': None, 'Z': 0, 'magic': 1}[time_boundaries] if not test_opposite_sides else None,
    }
    if time_boundaries == 'magic':
        steps = [
            step0_in.to_magic_init_step(),
            step0_in.without_start_transition(),
            step1_lz,
            step2_lx,
            step3_out.without_end_transition(),
            step3_out.to_magic_end_step(),
        ]
    else:
        steps = normal_steps

    builders = [builder]
    for k, step in enumerate(steps):
        if time_boundaries == 'magic' and (k == 1 or k == len(steps) - 1):
            builders.append(builders[-1].fork())
        step.build_rounds(
            builder=builders[-1],
            rel_order_func=rel_order_func_start if k < len(steps) // 2 else rel_order_func_end,
            alternate_ordering_with_round_parity=True,
            edit_cur_obs=cur_obs,
            start_round_index=round_index,
            cmp_layer=f'step{k-1}' if k > 0 else None,
            save_layer=f'step{k}',
            o2i=o2i,
        )
        round_index += step.rounds

    if time_boundaries == 'magic':
        assert len(builders) == 3
        return MagicableCircuit(
            noiseless_start=builders[0].circuit,
            noisy_body=builders[1].circuit,
            noiseless_end=builders[2].circuit,
            noiseless_qubit_indices=[builder.q2i[q] for q in ancillas],
            steps=gen.StepSequenceOutline(normal_steps),
        )
    assert len(builders) == 1
    return MagicableCircuit(
        noiseless_start=None,
        noisy_body=builder.circuit,
        noiseless_end=None,
        noiseless_qubit_indices=[builder.q2i[q] for q in ancillas],
        steps=gen.StepSequenceOutline(normal_steps),
    )
