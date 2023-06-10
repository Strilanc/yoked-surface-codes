import math
from typing import Literal, Optional, Tuple, Union, Sequence

import sinter

import gen


from typing import List

import stim


def stabilizers_from_bit_group_mask(*, b: str, n: int, bit_group_mask: int, sign: int) -> List[stim.PauliString]:
    result = []
    groups = sinter.group_by(range(n), key=lambda k: k & bit_group_mask)
    for k, group in groups.items():
        stabilizer = stim.PauliString(n)
        for g in group:
            stabilizer[g] = b
        stabilizer *= sign
        result.append(stabilizer)
    return result


def make_squareberg_stabilizers(w: int) -> List[stim.PauliString]:
    """Returns stabilizers of the squareberg code.

    The sign of the stabilizer is used to hint at how to group them
    when measuring using lattice surgery.
    """
    m = w - 1
    h = m.bit_length()
    stabilizers = [
        *stabilizers_from_bit_group_mask(
            b='X',
            n=w * w,
            bit_group_mask=m,
            sign=+1,
        ),
        *stabilizers_from_bit_group_mask(
            b='X',
            n=w * w,
            bit_group_mask=m << h,
            sign=-1,
        ),
        *stabilizers_from_bit_group_mask(
            b='Z',
            n=w * w,
            bit_group_mask=m << 1,
            sign=+1,
        ),
        *stabilizers_from_bit_group_mask(
            b='Z',
            n=w * w,
            bit_group_mask=1 | (m << (h + 1)),
            sign=-1,
        ),
    ]
    return stabilizers


def make_observables(w: int) -> List[Tuple[stim.PauliString, stim.PauliString, int]]:
    stabilizers = make_squareberg_stabilizers(w)
    observables = []
    h = (w - 1).bit_length()
    m = (1 << h) - 1
    mx1 = m << h
    mx2 = m
    mz1 = m << 1
    mz2 = (m << (h + 1)) ^ 1 ^ (w * w)
    for k in range(w * w):
        z0 = k & mx1
        z1 = k & mx2
        z2 = k & mx1 & mx2
        x0 = k | mz1
        x1 = k | mz2
        x2 = k | mz1 | mz2
        if k in [x0, x1, x2, z0, z1, z2]:
            continue
        xs = stim.PauliString(w * w)
        zs = stim.PauliString(w * w)
        xs[k] = 'X'
        xs[x0] = 'X'
        xs[x1] = 'X'
        xs[x2] = 'X'
        zs[k] = 'Z'
        zs[z0] = 'Z'
        zs[z1] = 'Z'
        zs[z2] = 'Z'
        observables.append((xs, zs, k))
        assert not xs.commutes(zs)
        assert all(s.commutes(xs) for s in stabilizers)
        assert all(s.commutes(zs) for s in stabilizers)
    assert len(observables) == w*w - w*4 + 2
    return observables


def make_pauli_string_latex_array(s: Union[stim.PauliString, Sequence[int]]) -> str:
    w = round(math.sqrt(len(s)))
    out = [r'\begin{tabular}{c}' + '\n']
    for y in range(w):
        out.append(r'    \texttt{')
        for x in range(w):
            c = x + y*w
            out.append(['\\_', 'X', 'Y', 'Z', '@'][s[c]])
        out.append(r'}\\' + '\n')
    out.append(r'\end{tabular}')
    return ''.join(out)


def make_squareberg_latex_table(w: int) -> str:
    stabilizers = make_squareberg_stabilizers(w)
    observables = make_observables(w)
    obs_map = {}
    for x, z, _ in observables:
        y = x * z
        y_index, = [q for q, p in enumerate(y) if p == 2]
        assert y_index not in obs_map
        obs_map[y_index] = y

    out = [r'''\begin{tabular}{|c|c|c|c||c|c|c|c|c|c|c|c|}
\hline
\multicolumn{12}{|c|}{[[64, 34, 4]] Squareberg Code}
\\\hline
{\small X Col Checks} & {\small X Row Checks} & {\small Z Bi-Col Checks} & {\small Z Bi-Row Checks} & \multicolumn{8}{|c|}{Y Observables (positioned by location of Y term)}
\\\hline
''']
    m = len(stabilizers) // 4
    for y in range(m):
        for x in range(12):
            if x < 4:
                k = y + x*m
                s = stabilizers[k]
            else:
                k = y * 8 + (x - 4)
                if k in obs_map:
                    s = obs_map[k]
                else:
                    s = None
            if s is not None:
                out.append(make_pauli_string_latex_array(s))
            else:
                out.append(r'\texttt{{\kern 5em}}')
            out.append('&' if x < 11 else r'\\\hline' + '\n')
    out.append(r'\end{tabular}')
    return ''.join(out)


def squareberg_magic_memory_circuit(
        *,
        patch_diameter: int,
        rounds: int,
        noise: Optional[gen.NoiseModel],
        style: Literal['cz', 'css'],
        num_patches: int,
) -> stim.Circuit:
    assert rounds >= 2
    w = round(math.sqrt(num_patches)) // 2 * 2
    if w * w != num_patches:
        raise ValueError("num_patches must be square and a multiple of 16")
    g = patch_diameter - 1
    rel_order_func = lambda q: gen.Order_Z if gen.checkerboard_basis(q) == 'X' else gen.Order_ᴎ
    base_patch = gen.ClosedCurve.from_cycle(
        [0, 'X', g, 'Z', (1 + 1j) * g, 'X', 1j * g, 'Z', 0],
    ).to_patch(rel_order_func=rel_order_func)
    base_obs_x_1 = gen.PauliString({q: 'X' for q in base_patch.data_set if q.real == 0})
    base_obs_z_1 = gen.PauliString({q: 'Z' for q in base_patch.data_set if q.imag == 0})
    base_obs_x_2 = gen.PauliString({q: 'X' for q in base_patch.data_set if q.real == patch_diameter - 1})
    base_obs_z_2 = gen.PauliString({q: 'Z' for q in base_patch.data_set if q.imag == patch_diameter - 1})
    assert base_obs_x_1.anticommutes(base_obs_z_1)
    assert base_obs_x_1.anticommutes(base_obs_z_2)
    assert base_obs_x_2.anticommutes(base_obs_z_1)
    assert base_obs_x_2.anticommutes(base_obs_z_2)
    assert base_obs_x_1.commutes(base_obs_x_2)
    assert base_obs_z_1.commutes(base_obs_z_2)
    pitch = patch_diameter + 1

    epr_ancilla_qubits = []
    observables = {}
    patches = []
    for kx in range(w):
        for ky in range(w):
            trans = lambda q: q + kx * pitch + ky*pitch*1j
            k = len(epr_ancilla_qubits)
            e = trans(-0.25j - 0.25)
            epr_ancilla_qubits.append(e)
            observables[f'X{k}a'] = base_obs_x_1.with_transformed_coords(trans) * gen.PauliString({e: 'X'})
            observables[f'X{k}b'] = base_obs_x_2.with_transformed_coords(trans) * gen.PauliString({e: 'X'})
            observables[f'Z{k}a'] = base_obs_z_1.with_transformed_coords(trans) * gen.PauliString({e: 'Z'})
            observables[f'Z{k}b'] = base_obs_z_2.with_transformed_coords(trans) * gen.PauliString({e: 'Z'})
            patches.append(base_patch.after_coordinate_transform(trans))
    full_patch = gen.Patch([tile for patch in patches for tile in patch.tiles])

    builder = gen.Builder.for_qubits(full_patch.used_set | set(epr_ancilla_qubits))
    for key, obs in observables.items():
        builder.measure_pauli_product(q2b=obs.qubits, key=f'obs_{key}_init')
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
    ) if noise is not None else noisy_body.circuit

    builder.measure_patch(full_patch, save_layer='magic_end', cmp_layer='loop')
    for key, obs in observables.items():
        builder.measure_pauli_product(q2b=obs.qubits, key=f'obs_{key}_end')
    obs_index = 0
    for key, obs in observables.items():
        if key.endswith('a'):
            builder.obs_include([f'obs_{key}_init', f'obs_{key}_end'], obs_index=obs_index)
            obs_index += 1

    for dk, stabilizer in enumerate(make_squareberg_stabilizers(w)):
        keys = []
        suffix = 'a' if stabilizer.sign == -1 else 'b'
        for q, p in enumerate(stabilizer):
            if p:
                b = '_XYZ'[p]
                keys.append(f'{b}{q}{suffix}')
        builder.detector([f'obs_{key}_{phase}' for key in keys for phase in ['init', 'end']], pos=-1 - dk)

    return builder.circuit


def squareberg_phenomenological_circuit(
        *,
        rounds: int,
        noise: gen.NoiseRule,
        num_patches: int,
) -> stim.Circuit:
    assert rounds >= 2
    w = round(math.sqrt(num_patches)) // 2 * 2
    if w * w != num_patches:
        raise ValueError("num_patches must be square and a multiple of 16")

    s2q = [
        x + 1j*y
        for x in range(w)
        for y in range(w)
    ]
    a2q = [
        x + 1j*y + 0.25 + 0.125j
        for x in range(w)
        for y in range(w)
    ]
    tiles_x1 = []
    tiles_x2 = []
    tiles_z1 = []
    tiles_z2 = []
    next_id = 0
    for stabilizer in make_squareberg_stabilizers(w=w):
        p, = set(stabilizer) - {0}
        qs = [s2q[s] for s in range(len(stabilizer)) if stabilizer[s]]
        if p == 1:
            if stabilizer.sign == -1:
                tiles = tiles_x2
            else:
                tiles = tiles_x1
        else:
            if stabilizer.sign == -1:
                tiles = tiles_z2
            else:
                tiles = tiles_z1
        tiles.append(gen.Tile(
            bases='_XYZ'[p] * len(qs),
            measurement_qubit=next_id,
            ordered_data_qubits=qs,
        ))
        next_id += 1
    patch = gen.Patch(tiles_x1 + tiles_x2 + tiles_z1 + tiles_z2)
    stim_obs = make_observables(w=w)

    observables_x = []
    observables_z = []
    ancilla_qubits = []
    for k, (xs, zs, ak) in enumerate(stim_obs):
        ancilla_qubits.append(a2q[ak])
        observables_x.append(gen.PauliString({s2q[s]: 'X' for s, p in enumerate(xs) if p}))
        observables_z.append(gen.PauliString({s2q[s]: 'Z' for s, p in enumerate(zs) if p}))
    return gen.make_phenomenological_circuit_for_stabilizer_code(
        patch=patch,
        noise=noise,
        observables_x=observables_x,
        observables_z=observables_z,
        suggested_ancilla_qubits=ancilla_qubits,
        rounds=rounds,
    )
