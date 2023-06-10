import collections
from typing import Union, Literal, Tuple, List, FrozenSet, Set, Counter, Optional

import stim

from gen._core._builder import Builder
from gen._flows._flow import PauliString
from gen._core._noise import NoiseModel, NoiseRule, OP_TYPES, CLIFFORD_2Q, ANNOTATION
from gen._core._patch import Patch
from gen._core._util import sorted_complex


def _commune_with_the_observables(
    *,
    patch: Patch,
    obs_x: Optional[List[PauliString]],
    obs_z: Optional[List[PauliString]],
    suggested_ancilla_qubits: Optional[List[complex]],
) -> Tuple[List[PauliString], FrozenSet[complex]]:
    if obs_z is None and obs_x is None:
        raise ValueError('No observables specified')
    if obs_x is not None and obs_z is not None:
        assert len(obs_x) == len(obs_z)
    n = len(obs_x) if obs_x is not None else len(obs_z)
    for i in range(n):
        if obs_x is not None:
            assert isinstance(obs_x[i], PauliString)
        if obs_z is not None:
            assert isinstance(obs_z[i], PauliString)
        if obs_x is not None and obs_z is not None:
            assert not obs_x[i].commutes(obs_z[i])
        for j in range(i + 1, n):
            if obs_x is not None:
                assert obs_x[i].commutes(obs_x[j])
            if obs_z is not None:
                assert obs_z[i].commutes(obs_z[j])
            if obs_x is not None and obs_z is not None:
                assert obs_x[i].commutes(obs_z[j])
                assert obs_z[i].commutes(obs_x[j])

    if obs_z is None:
        return obs_x, frozenset()
    if obs_x is None:
        return obs_z, frozenset()

    ancilla_qubits = []
    epr_observables = []
    a = min(q.real for q in patch.data_set) + min(q.imag for q in patch.data_set)*1j - 1j
    for k in range(n):
        if suggested_ancilla_qubits is not None:
            assert len(suggested_ancilla_qubits) == n
            a = suggested_ancilla_qubits[k]
        ancilla_qubits.append(a)
        epr_observables.append(obs_x[k] * PauliString({a: 'X'}))
        epr_observables.append(obs_z[k] * PauliString({a: 'Z'}))
        a += 1
    return epr_observables, frozenset(ancilla_qubits)


def make_phenomenological_circuit_for_stabilizer_code(
        *,
        patch: Patch,
        noise: NoiseRule,
        observables_x: Optional[List[PauliString]] = None,
        observables_z: Optional[List[PauliString]] = None,
        suggested_ancilla_qubits: Optional[List[complex]] = None,
        rounds: int,
) -> stim.Circuit:
    observables, immune = _commune_with_the_observables(
        patch=patch,
        obs_x=observables_x,
        obs_z=observables_z,
        suggested_ancilla_qubits=suggested_ancilla_qubits,
    )
    builder = Builder.for_qubits(patch.data_set | immune)

    for k, obs in enumerate(observables):
        builder.measure_pauli_product(q2b=obs.qubits, key=f'OBS_START{k}')
        builder.obs_include([f'OBS_START{k}'], obs_index=k)
    builder.measure_patch(patch, save_layer='init')
    builder.tick()

    loop = builder.fork()
    loop.measure_patch(patch, save_layer='loop', cmp_layer='init')
    loop.shift_coords(dt=1)
    loop.tick()
    noise_model = NoiseModel(
        tick_noise=NoiseRule(after=noise.after),
        any_measurement_rule=NoiseRule(flip_result=noise.flip_result, after={}),
        any_clifford_1q_rule=NoiseRule(after={}),
        any_clifford_2q_rule=NoiseRule(after={}),
        allow_multiple_uses_of_a_qubit_in_one_tick=True,
    )
    noisy_loop = noise_model.noisy_circuit(
        loop.circuit,
        immune_qubits={builder.q2i[q] for q in immune},
    )
    if len(noisy_loop) == 0 or (isinstance(noisy_loop[-1], stim.CircuitInstruction) and noisy_loop[-1].name != 'TICK'):
        noisy_loop.append('TICK')
    builder.circuit += noisy_loop * rounds

    builder.measure_patch(patch, save_layer='end', cmp_layer='loop')
    for k, obs in enumerate(observables):
        builder.measure_pauli_product(q2b=obs.qubits, key=f'OBS_END{k}')
        builder.obs_include([f'OBS_END{k}'], obs_index=k)

    return builder.circuit


def make_code_capacity_circuit_for_stabilizer_code(
        *,
        patch: Patch,
        noise: NoiseRule,
        observables_x: Optional[List[PauliString]] = None,
        observables_z: Optional[List[PauliString]] = None,
        suggested_ancilla_qubits: Optional[List[complex]] = None,
) -> stim.Circuit:
    assert noise.flip_result == 0
    observables, immune = _commune_with_the_observables(
        patch=patch,
        obs_x=observables_x,
        obs_z=observables_z,
        suggested_ancilla_qubits=suggested_ancilla_qubits,
    )
    builder = Builder.for_qubits(patch.data_set | immune)

    for k, obs in enumerate(observables):
        builder.measure_pauli_product(q2b=obs.qubits, key=f'OBS_START{k}')
        builder.obs_include([f'OBS_START{k}'], obs_index=k)
    builder.measure_patch(patch, save_layer='init')
    builder.tick()

    for k, p in noise.after.items():
        builder.circuit.append(k, [builder.q2i[q] for q in sorted_complex(patch.data_set - immune)], p)
    builder.tick()

    builder.measure_patch(patch, save_layer='end', cmp_layer='init')
    for k, obs in enumerate(observables):
        builder.measure_pauli_product(q2b=obs.qubits, key=f'OBS_END{k}')
        builder.obs_include([f'OBS_END{k}'], obs_index=k)

    return builder.circuit


def gate_counts_for_circuit(circuit: stim.Circuit) -> Counter[str]:
    """Determines gates used by a circuit, disambiguating MPP/feedback cases.

    MPP instructions are expanded into what they actually measure, such as
    "MXX" for MPP X1*X2 and "MXYZ" for MPP X4*Y5*Z7.

    Feedback instructions like `CX rec[-1] 0` become the gate "feedback".

    Sweep instructions like `CX sweep[2] 0` become the gate "sweep".
    """
    out = collections.Counter()
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            for k, v in gate_counts_for_circuit(instruction.body_copy()).items():
                out[k] += v * instruction.repeat_count

        elif instruction.name in ['CX', 'CY', 'CZ', 'XCZ', 'YCZ']:
            targets = instruction.targets_copy()
            for k in range(0, len(targets), 2):
                if targets[k].is_measurement_record_target or targets[k + 1].is_measurement_record_target:
                    out['feedback'] += 1
                elif targets[k].is_sweep_bit_target or targets[k + 1].is_sweep_bit_target:
                    out['sweep'] += 1
                else:
                    out[instruction.name] += 1

        elif instruction.name == 'MPP':
            op = 'M'
            targets = instruction.targets_copy()
            is_continuing = True
            for t in targets:
                if t.is_combiner:
                    is_continuing = True
                    continue
                p = 'X' if t.is_x_target else 'Y' if t.is_y_target else 'Z' if t.is_z_target else '?'
                if is_continuing:
                    op += p
                    is_continuing = False
                else:
                    if op == 'MZ':
                        op = 'M'
                    out[op] += 1
                    op = 'M' + p
            if op:
                if op == 'MZ':
                    op = 'M'
                out[op] += 1

        elif OP_TYPES[instruction.name] == CLIFFORD_2Q or instruction.name in ['PAULI_CHANNEL_2', 'DEPOLARIZE2']:
            out[instruction.name] += len(instruction.targets_copy()) // 2
        elif OP_TYPES[instruction.name] == ANNOTATION or instruction.name in ['E', 'ELSE_CORRELATED_ERROR']:
            out[instruction.name] += 1
        else:
            out[instruction.name] += len(instruction.targets_copy())

    return out


def gates_used_by_circuit(circuit: stim.Circuit) -> Set[str]:
    """Determines gates used by a circuit, disambiguating MPP/feedback cases.

    MPP instructions are expanded into what they actually measure, such as
    "MXX" for MPP X1*X2 and "MXYZ" for MPP X4*Y5*Z7.

    Feedback instructions like `CX rec[-1] 0` become the gate "feedback".

    Sweep instructions like `CX sweep[2] 0` become the gate "sweep".
    """
    out = set()
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            out |= gates_used_by_circuit(instruction.body_copy())

        elif instruction.name in ['CX', 'CY', 'CZ', 'XCZ', 'YCZ']:
            targets = instruction.targets_copy()
            for k in range(0, len(targets), 2):
                if targets[k].is_measurement_record_target or targets[k + 1].is_measurement_record_target:
                    out.add('feedback')
                elif targets[k].is_sweep_bit_target or targets[k + 1].is_sweep_bit_target:
                    out.add('sweep')
                else:
                    out.add(instruction.name)

        elif instruction.name == 'MPP':
            op = 'M'
            targets = instruction.targets_copy()
            is_continuing = True
            for t in targets:
                if t.is_combiner:
                    is_continuing = True
                    continue
                p = 'X' if t.is_x_target else 'Y' if t.is_y_target else 'Z' if t.is_z_target else '?'
                if is_continuing:
                    op += p
                    is_continuing = False
                else:
                    if op == 'MZ':
                        op = 'M'
                    out.add(op)
                    op = 'M' + p
            if op:
                if op == 'MZ':
                    op = 'M'
                out.add(op)

        else:
            out.add(instruction.name)

    return out
