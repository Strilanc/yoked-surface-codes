from typing import Literal

import stim

import gen


def yoked_magic_memory_circuit(
        *,
        patch_diameter: int,
        rounds: int,
        noise: gen.NoiseModel,
        style: Literal['cz', 'css'],
        yokes: int,
        num_patches: int,
        remove_x_yoke: bool = False,
) -> stim.Circuit:
    """Generates a multi-qubit memory circuit with configurable number of yokes.

    The circuits use magical time boundaries and magical ancillas to prepare the
    states and the beginning, and measure the states at the end, so that all
    observables can be tested simultaneously. And also because the initialization
    is complicated to implement.

    Args:
        patch_diameter: The width and height of each surface code patch.
        rounds: The number of times to measure each local stabilizer while
            applying circuit noise. The yoke stabilizers and logical observables
            are magically measured before the first round and after the last
            round.
        noise: The noise model to apply to the circuit (except at the magical
            time boundaries preparing the observables and the yokes, and on the
            magical ancilla qubits used to allow tracking X and Z observables
            simultaneously).
        style: Determines the gateset used.
        yokes: Can be set to 0, 1, or 2. The values mean the following.
            0: No yoking. Just independent logical qubit patches.
            1: YBerg code. Single YYY...Y yoke.
            2: Iceberg code. Both XXX...X yoke and ZZZ...Z yoke.
        num_patches: Total number of surface code patches.
        remove_x_yoke: If true, removes the X-type yoke check.

    Returns:
        The generated circuit.
    """
    assert yokes in [0, 1, 2]
    assert rounds >= 2
    g = patch_diameter - 1
    rel_order_func = lambda q: gen.Order_Z if gen.checkerboard_basis(q) == 'X' else gen.Order_ᴎ
    base_patch = gen.ClosedCurve.from_cycle(
        [0, 'X', g, 'Z', (1 + 1j) * g, 'X', 1j * g, 'Z', 0],
    ).to_patch(rel_order_func=rel_order_func)
    base_obs_x = gen.PauliString({q: 'X' for q in base_patch.data_set if q.real == 0})
    base_obs_z = gen.PauliString({q: 'Z' for q in base_patch.data_set if q.imag == 0})
    assert base_obs_x.anticommutes(base_obs_z)
    pitch = patch_diameter + 1

    epr_ancilla_qubits = []
    x_observables = []
    z_observables = []
    patches = []
    for k in range(num_patches):
        epr_ancilla_qubits.append(-2j + k * pitch)
        trans = lambda q: q + k * pitch
        x_observables.append(base_obs_x.with_transformed_coords(trans))
        z_observables.append(base_obs_z.with_transformed_coords(trans))
        patches.append(base_patch.after_coordinate_transform(trans))
    full_patch = gen.Patch([tile for patch in patches for tile in patch.tiles])

    x_protected_observables = {}
    z_protected_observables = {}
    next_obs_index = 0
    for x, z, e in zip(x_observables, z_observables, epr_ancilla_qubits):
        if not remove_x_yoke:
            x_protected_observables[next_obs_index] = x * gen.PauliString({e: 'X'})
            next_obs_index += 1
        z_protected_observables[next_obs_index] = z * gen.PauliString({e: 'Z'})
        next_obs_index += 1
    all_protected_observables = {**x_protected_observables, **z_protected_observables}
    if remove_x_yoke:
        all_protected_observables = z_protected_observables
    builder = gen.Builder.for_qubits(full_patch.used_set | set(epr_ancilla_qubits))
    for obs_index, obs in all_protected_observables.items():
        builder.measure_pauli_product(q2b=obs.qubits, key=f'obs{obs_index}_init')
        builder.obs_include([f'obs{obs_index}_init'], obs_index=obs_index)
    builder.measure_patch(full_patch, save_layer='magic_init')
    builder.tick()

    noisy_body = builder.fork()
    full_patch.detect(
        builder=noisy_body,
        style=style,
        save_layer='loop_inner',
        tracker_layer_last_rep='loop',
        cmp_layer='magic_init',
        repetitions=rounds,
    )
    builder.circuit += noise.noisy_circuit(
        noisy_body.circuit,
        immune_qubits={builder.q2i[e] for e in epr_ancilla_qubits},
        system_qubits=set(builder.q2i.values()),
    )

    builder.measure_patch(full_patch, save_layer='magic_end', cmp_layer='loop')
    for obs_index, obs in all_protected_observables.items():
        builder.measure_pauli_product(q2b=obs.qubits, key=f'obs{obs_index}_end')
        builder.obs_include([f'obs{obs_index}_end'], obs_index=obs_index)
    if yokes == 2:
        if not remove_x_yoke:
            builder.detector([f'obs{obs_index}_{phase}' for obs_index in x_protected_observables.keys() for phase in ['init', 'end']], pos=epr_ancilla_qubits[0])
        builder.detector([f'obs{obs_index}_{phase}' for obs_index in z_protected_observables.keys() for phase in ['init', 'end']], pos=epr_ancilla_qubits[0])
    elif yokes == 1:
        builder.detector([f'obs{obs_index}_{phase}' for obs_index in all_protected_observables.keys() for phase in ['init', 'end']], pos=epr_ancilla_qubits[0])
    elif yokes == 0:
        builder.detector([], pos=epr_ancilla_qubits[0])
    else:
        raise ValueError(f'{yokes=}')

    return builder.circuit
