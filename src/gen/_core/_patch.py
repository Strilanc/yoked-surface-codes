import functools
import pathlib
from typing import Iterable, FrozenSet, Callable, Union, Literal, \
    Optional, Any, Dict, List, AbstractSet

from gen._core._builder import Builder, AtLayer
from gen._core._util import sorted_complex, min_max_complex, complex_key
from gen._interaction_planner import DESIRED_Z_TO_ORIENTATION
from gen._core._tile import Tile
from gen._util import write_file


class Patch:
    """A collection of annotated stabilizers to measure simultaneously.
    """

    def __init__(self,
                 tiles: Iterable[Tile],
                 *,
                 do_not_sort: bool = False):
        if do_not_sort:
            self.tiles = tuple(tiles)
        else:
            self.tiles = tuple(sorted_complex(tiles, key=lambda e: e.measurement_qubit))

    def after_coordinate_transform(self, coord_transform: Callable[[complex], complex]) -> 'Patch':
        return Patch(
            [e.after_coordinate_transform(coord_transform) for e in self.tiles],
        )

    def after_basis_transform(self, basis_transform: Callable[[str], str]) -> 'Patch':
        return Patch(
            [e.after_basis_transform(basis_transform) for e in self.tiles],
        )

    def without_wraparound_tiles(self) -> 'Patch':
        p0, p1 = min_max_complex(self.data_set, default=0)
        def keep_tile(tile: Tile) -> bool:
            t0, t1 = min_max_complex(tile.data_set, default=0)
            if t0.real == p0.real and t1.real == p1.real:
                return False
            if t0.imag == p0.imag and t1.imag == p1.imag:
                return False
            return True
        return Patch([t for t in self.tiles if keep_tile(t)])

    @functools.cached_property
    def m2tile(self) -> Dict[complex, Tile]:
        return {e.measurement_qubit: e for e in self.tiles}

    def with_opposite_order(self) -> 'Patch':
        return Patch(tiles=[
            Tile(
                bases=tile.bases[::-1],
                measurement_qubit=tile.measurement_qubit,
                ordered_data_qubits=tile.ordered_data_qubits[::-1],
            )
            for tile in self.tiles
        ])

    def write_svg(
            self,
            path: Union[str, pathlib.Path],
            *,
            other: Union['Patch', Iterable['Patch']] = (),
            show_order: Union[bool, Literal['undirected', '3couplerspecial']] = True,
            show_measure_qubits: bool = True,
            show_data_qubits: bool = False,
            system_qubits: Iterable[complex] = (),
            opacity: float = 1,
    ) -> None:
        from gen._viz_patch_svg import patch_svg_viewer
        viewer = patch_svg_viewer(
            patches=[self] + ([other] if isinstance(other, Patch) else list(other)),
            show_measure_qubits=show_measure_qubits,
            show_data_qubits=show_data_qubits,
            show_order=show_order,
            available_qubits=system_qubits,
            opacity=opacity,
        )
        write_file(path, viewer)

    def with_xz_flipped(self) -> 'Patch':
        trans = {'X': 'Z', 'Y': 'Y', 'Z': 'X'}
        return self.after_basis_transform(trans.__getitem__)

    @functools.cached_property
    def used_set(self) -> FrozenSet[complex]:
        result = set()
        for e in self.tiles:
            result |= e.used_set
        return frozenset(result)

    @functools.cached_property
    def data_set(self) -> FrozenSet[complex]:
        result = set()
        for e in self.tiles:
            for q in e.ordered_data_qubits:
                if q is not None:
                    result.add(q)
        return frozenset(result)

    def __eq__(self, other):
        if not isinstance(other, Patch):
            return NotImplemented
        return self.tiles == other.tiles

    def __ne__(self, other):
        return not (self == other)

    @functools.cached_property
    def measure_set(self) -> FrozenSet[complex]:
        return frozenset(e.measurement_qubit for e in self.tiles)

    def __repr__(self):
        return '\n'.join([
            'gen.Patch(tiles=[',
            *[f'    {e!r},'.replace('\n', '\n    ') for e in self.tiles],
            '])',
        ])

    def _measure_css(self,
                     *,
                     data_resets: Dict[complex, str],
                     data_measures: Dict[complex, str],
                     builder: Builder,
                     tracker_key: Callable[[complex], Any],
                     tracker_layer: float) -> None:
        assert self.measure_set.isdisjoint(data_resets)
        if not self.tiles:
            return

        x_tiles = [tile for tile in self.tiles if tile.basis == 'X']
        z_tiles = [tile for tile in self.tiles if tile.basis == 'Z']
        other_tiles = [tile for tile in self.tiles if tile.basis != 'X' and tile.basis != 'Z']
        reset_bases = {
            'X': [tile.measurement_qubit for tile in x_tiles],
            'Y': [],
            'Z': [tile.measurement_qubit for tile in z_tiles + other_tiles],
        }
        for q, b in data_resets.items():
            reset_bases[b].append(q)
        for b, qs in reset_bases.items():
            if qs:
                builder.gate(f'R{b}', qs)
        builder.tick()

        num_layers, = {len(e.ordered_data_qubits) for e in self.tiles}
        for k in range(num_layers):
            pairs = []
            for tile in x_tiles:
                q = tile.ordered_data_qubits[k]
                if q is not None:
                    pairs.append((tile.measurement_qubit, q))
            for tile in z_tiles:
                q = tile.ordered_data_qubits[k]
                if q is not None:
                    pairs.append((q, tile.measurement_qubit))
            builder.gate2('CX', pairs)
            for tile in sorted(other_tiles, key=lambda tile: complex_key(tile.measurement_qubit)):
                q = tile.ordered_data_qubits[k]
                b = tile.bases[k]
                if q is not None:
                    builder.gate2(f'{b}CX', [(q, tile.measurement_qubit)])
            builder.tick()

        measure_bases = {
            'X': [tile.measurement_qubit for tile in x_tiles],
            'Y': [],
            'Z': [tile.measurement_qubit for tile in z_tiles + other_tiles],
        }
        for q, b in data_measures.items():
            measure_bases[b].append(q)
        for b, qs in measure_bases.items():
            if qs:
                builder.measure(
                    qs,
                    basis=b,
                    tracker_key=tracker_key,
                    save_layer=tracker_layer,
                )

    def _measure_cz(self,
                    *,
                    data_resets: Dict[complex, str],
                    data_measures: Dict[complex, str],
                    builder: Builder,
                    tracker_key: Callable[[complex], Any],
                    tracker_layer: float) -> None:
        assert self.measure_set.isdisjoint(data_resets)
        if not self.tiles:
            return

        builder.gate('R', data_resets.keys() | self.measure_set)
        builder.tick()

        num_layers, = {len(e.ordered_data_qubits) for e in self.tiles}
        start_orientations = {
            **{q: DESIRED_Z_TO_ORIENTATION[b] for q, b in data_resets.items()},
        }
        end_orientations = {
            **{q: DESIRED_Z_TO_ORIENTATION[b] for q, b in data_measures.items()},
        }
        with builder.plan_interactions(
                layer_count=num_layers,
                start_orientations=start_orientations,
                end_orientations=end_orientations,
        ) as planner:
            for k in range(num_layers):
                for e in self.tiles:
                    q = e.ordered_data_qubits[k]
                    if q is not None:
                        planner.pcp(e.bases[k], 'X', q, e.measurement_qubit, layer=k)

        builder.tick()
        builder.measure(data_measures.keys() | self.measure_set,
                        tracker_key=tracker_key,
                        save_layer=tracker_layer)

    def _measure_mpp(self,
                     *,
                     data_resets: Dict[complex, str],
                     data_measures: Dict[complex, str],
                     builder: Builder,
                     tracker_key: Callable[[complex], Any],
                     tracker_layer: float) -> None:
        assert self.measure_set.isdisjoint(data_resets)

        if data_resets:
            for b in 'XYZ':
                builder.gate(f'R{b}', {q for q, db in data_resets.items() if b == db})

        for v in self.tiles:
            builder.measure_pauli_product(
                q2b={q: b for q, b in zip(v.ordered_data_qubits, v.bases) if q is not None},
                key=AtLayer(tracker_key(v.measurement_qubit), tracker_layer)
            )

        if data_measures:
            for b in 'XYZ':
                builder.measure({q for q, db in data_measures.items() if b == db},
                                basis=b,
                                tracker_key=tracker_key,
                                save_layer=tracker_layer)

    def measure(self,
                *,
                data_resets: Optional[Dict[complex, str]] = None,
                data_measures: Optional[Dict[complex, str]] = None,
                builder: Builder,
                tracker_key: Callable[[complex], Any] = lambda e: e,
                save_layer: Any,
                style: Literal['css', 'cz', 'mpp'] = 'cz') -> None:
        if data_resets is None:
            data_resets = {}
        if data_measures is None:
            data_measures = {}
        if style == 'css':
            self._measure_css(
                data_resets=data_resets,
                data_measures=data_measures,
                builder=builder,
                tracker_key=tracker_key,
                tracker_layer=save_layer,
            )
        elif style == 'cz':
            self._measure_cz(
                data_resets=data_resets,
                data_measures=data_measures,
                builder=builder,
                tracker_key=tracker_key,
                tracker_layer=save_layer,
            )
        elif style == 'mpp':
            self._measure_mpp(
                data_resets=data_resets,
                data_measures=data_measures,
                builder=builder,
                tracker_key=tracker_key,
                tracker_layer=save_layer,
            )
        else:
            raise NotImplementedError(f'{style=}')

    def detect(self,
               *,
               comparison_overrides: Optional[Dict[Any, Optional[List[Any]]]] = None,
               skipped_comparisons: Iterable[Any] = (),
               singleton_detectors: Iterable[Any] = (),
               data_resets: Optional[Dict[complex, str]] = None,
               data_measures: Optional[Dict[complex, str]] = None,
               builder: Builder,
               repetitions: Optional[int] = None,
               tracker_key: Callable[[complex], Any] = lambda e: e,
               cmp_layer: Optional[Any],
               save_layer: Any,
               tracker_layer_last_rep: Optional[Any] = None,
               post_selected_positions: AbstractSet[complex] = frozenset(),
               style: Literal['css', 'cz', 'mpp'] = 'cz') -> None:
        if data_resets is None:
            data_resets = {}
        if data_measures is None:
            data_measures = {}
        assert (repetitions is not None) == (tracker_layer_last_rep is not None)
        if repetitions is not None:
            assert not data_resets
            assert not data_measures
        if repetitions == 0:
            for plaq in self.tiles:
                m = plaq.measurement_qubit
                builder.tracker.make_measurement_group([AtLayer(m, cmp_layer)], key=AtLayer(m, tracker_layer_last_rep))
            return

        child = builder.fork()
        pm = builder.tracker.next_measurement_index
        self.measure(
            data_resets=data_resets,
            data_measures=data_measures,
            builder=child,
            tracker_key=tracker_key,
            save_layer=save_layer,
            style=style,
        )
        num_measurements = builder.tracker.next_measurement_index - pm

        if comparison_overrides is None:
            comparison_overrides = {}
        assert self.measure_set.isdisjoint(data_resets)
        skipped_comparisons_set = frozenset(skipped_comparisons)
        singleton_detectors_set = frozenset(singleton_detectors)
        for e in sorted_complex(self.tiles, key=lambda e2: e2.measurement_qubit):
            if all(e is None for e in e.ordered_data_qubits):
                continue
            failed = False
            for q, b in zip(e.ordered_data_qubits, e.bases):
                if q is not None and data_resets.get(q, b) != b:
                    failed = True
            if failed:
                continue
            m = e.measurement_qubit
            if m in skipped_comparisons_set:
                continue
            if m in singleton_detectors_set:
                comparisons = []
            elif cmp_layer is not None:
                comparisons = comparison_overrides.get(m, [AtLayer(m, cmp_layer)])
            else:
                comparisons = []
            if comparisons is None:
                continue
            assert isinstance(comparisons,
                              list), f"Vs exception must be a list but got {comparisons!r} for {m!r}"
            child.detector([AtLayer(m, save_layer), *comparisons], pos=m, mark_as_post_selected=m in post_selected_positions)
        child.circuit.append("SHIFT_COORDS", [], [0, 0, 1])
        specified_reps = repetitions is not None
        if repetitions is None:
            repetitions = 1
        if specified_reps:
            child.tick()

        if repetitions > 1 or tracker_layer_last_rep is not None:
            if tracker_layer_last_rep is None:
                raise ValueError("repetitions > 1 and tracker_layer_last_rep is None")
            offset = num_measurements * (repetitions - 1)
            builder.tracker.next_measurement_index += offset
            for m in data_measures.keys() | self.measure_set:
                builder.tracker.recorded[AtLayer(m, tracker_layer_last_rep)] = [e + offset for e in builder.tracker.recorded[AtLayer(m, save_layer)]]
        builder.circuit += child.circuit * repetitions

    def with_reverse_order(self) -> 'Patch':
        return Patch(
            tiles=[
                Tile(
                    bases=plaq.bases[::-1],
                    measurement_qubit=plaq.measurement_qubit,
                    ordered_data_qubits=plaq.ordered_data_qubits[::-1],
                )
                for plaq in self.tiles
            ],
        )
