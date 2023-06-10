from typing import Union, Set, FrozenSet, AbstractSet, Callable, Dict, Any, \
    Literal

from gen._core._util import sorted_complex
from gen._core._builder import Builder, AtLayer
from gen._core._patch import Patch, Tile


def build_patch_to_patch_surface_code_transition_rounds(
        *,
        builder: Builder,
        first_layer: Patch,
        second_layer: Patch,
        style: Literal['css', 'cz', 'mpp'],
        cmp_key_prev_layer: Any,
        save_key_first_layer: Any,
        save_key_second_layer: Any,
        kept_data_qubits: Union[Set[complex], FrozenSet[complex]],
        obs_qubit_sets: Dict[int, AbstractSet[complex]],
        first_layer_data_measure_basis: Union[None, str, Callable[[complex], str]],
        second_layer_data_init_basis: Union[None, str, Callable[[complex], str]],
):
    if isinstance(first_layer_data_measure_basis, str):
        fixed_future_time_basis = first_layer_data_measure_basis
        first_layer_data_measure_basis = lambda _: fixed_future_time_basis
    if isinstance(second_layer_data_init_basis, str):
        fixed_past_time_basis = second_layer_data_init_basis
        second_layer_data_init_basis = lambda _: fixed_past_time_basis

    assert kept_data_qubits <= first_layer.data_set
    assert kept_data_qubits <= second_layer.data_set, repr(sorted_complex(kept_data_qubits - second_layer.data_set))
    lost_data = first_layer.data_set - kept_data_qubits
    gained_data = second_layer.data_set - kept_data_qubits

    def matches_1st_layer_measure_basis(tile: Tile) -> bool:
        for b, d in zip(tile.bases, tile.ordered_data_qubits):
            if d is not None and d in lost_data and b != first_layer_data_measure_basis(d):
                return False
        return True

    if first_layer.tiles:
        first_layer.measure(
            style=style,
            builder=builder,
            data_measures={q: first_layer_data_measure_basis(q) for q in lost_data},
            save_layer=save_key_first_layer,
        )

        # Detectors from comparing to previous round.
        for prev_tile in first_layer.tiles:
            m = prev_tile.measurement_qubit
            builder.detector([AtLayer(m, cmp_key_prev_layer), AtLayer(m, save_key_first_layer)], pos=m)

        # Detectors from comparing data measurements to stabilizer measurements.
        for prev_tile in first_layer.tiles:
            m = prev_tile.measurement_qubit
            if matches_1st_layer_measure_basis(prev_tile) and prev_tile.data_set.isdisjoint(kept_data_qubits):
                builder.detector([AtLayer(q, save_key_first_layer) for q in prev_tile.used_set], pos=m, t=0.5)

        for obs_index, obs_qubits in obs_qubit_sets.items():
            builder.obs_include([AtLayer(q, save_key_first_layer) for q in lost_data & obs_qubits], obs_index=obs_index)
        builder.shift_coords(dt=1)
        builder.tick()

    def matches_2nd_layer_init_basis(tile: Tile) -> bool:
        for b, d in zip(tile.bases, tile.ordered_data_qubits):
            if d is not None and d in gained_data and b != second_layer_data_init_basis(d):
                return False
        return True

    if second_layer.tiles:
        second_layer.measure(
            style=style,
            builder=builder,
            data_resets={q: second_layer_data_init_basis(q) for q in gained_data},
            save_layer=save_key_second_layer,
        )

        # Detectors from comparing to first layer and/or data resets.
        for next_tile in second_layer.tiles:
            if not matches_2nd_layer_init_basis(next_tile):
                # Anticommutes with time boundary.
                continue

            m = next_tile.measurement_qubit
            comparison = [AtLayer(m, save_key_second_layer)]
            prev_tile = first_layer.m2tile.get(m)
            if prev_tile is not None and not prev_tile.data_set.isdisjoint(kept_data_qubits):
                comparison.append(AtLayer(m, save_key_first_layer))
                for q in prev_tile.data_set:
                    if q not in kept_data_qubits:
                        comparison.append(AtLayer(q, save_key_first_layer))
            builder.detector(comparison, pos=m)

        builder.shift_coords(dt=1)
        builder.tick()
