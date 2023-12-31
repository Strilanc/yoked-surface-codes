from typing import Iterable, Dict, Callable, Any, Optional, List, Tuple, TYPE_CHECKING

import stim

from gen._core._util import complex_key, sorted_complex
from gen._core._measurement_tracker import MeasurementTracker, AtLayer

if TYPE_CHECKING:
    from gen._core._patch import Patch
    from gen._flows._pauli_string import PauliString
    from gen._interaction_planner import InteractionPlanner
    from gen._interaction_planner import SingleQubitGatesPlanner


SYMMETRIC_GATES = {
    'CZ',
    'XCX',
    'YCY',
    'ZCZ',
    'SWAP',
    'ISWAP',
    'ISWAP_DAG',
    'SQRT_XX',
    'SQRT_YY',
    'SQRT_ZZ',
    'SQRT_XX_DAG',
    'SQRT_YY_DAG',
    'SQRT_ZZ_DAG',
}


class Builder:
    """Helper class for building stim circuits.

    Handles qubit indexing (complex -> int conversion).
    Handles measurement tracking (naming results and referring to them by name).
    """

    def __init__(self,
                 *,
                 q2i: Dict[complex, int],
                 circuit: stim.Circuit,
                 tracker: MeasurementTracker):
        self.q2i = q2i
        self.circuit = circuit
        self.tracker = tracker

    def copy(self) -> 'Builder':
        """Returns a Builder with independent copies of this builder's circuit and tracking data."""
        return Builder(q2i=dict(self.q2i), circuit=self.circuit.copy(), tracker=self.tracker.copy())

    def fork(self) -> 'Builder':
        """Returns a Builder with the same underlying tracking but which appends into a different circuit.
        """
        return Builder(q2i=self.q2i, circuit=stim.Circuit(), tracker=self.tracker)

    @staticmethod
    def for_qubits(
            qubits: Iterable[complex],
            *,
            to_circuit_coord_data: Callable[[complex], complex] = lambda e: e) -> 'Builder':
        q2i = {q: i for i, q in enumerate(sorted_complex(set(qubits)))}
        circuit = stim.Circuit()
        for q, i in q2i.items():
            c = to_circuit_coord_data(q)
            circuit.append("QUBIT_COORDS", [i], [c.real, c.imag])
        return Builder(
            q2i=q2i,
            circuit=circuit,
            tracker=MeasurementTracker(),
        )

    def gate(self,
             name: str,
             qubits: Iterable[complex],
             arg: Any = None) -> None:
        assert name not in ['CZ', 'ZCZ', 'XCX', 'YCY', 'ISWAP', 'ISWAP_DAG', 'SWAP', 'M', 'MX', 'MY']
        qubits = sorted_complex(qubits)
        if not qubits:
            return
        self.circuit.append(name, [self.q2i[q] for q in qubits], arg)

    def gate2(self,
              name: str,
              pairs: Iterable[Tuple[complex, complex]]) -> None:
        pairs = sorted(pairs, key=lambda pair: (complex_key(pair[0]), complex_key(pair[1])))
        if name == 'XCZ':
            pairs = [pair[::-1] for pair in pairs]
            name = 'CX'
        if name == 'YCZ':
            pairs = [pair[::-1] for pair in pairs]
            name = 'CY'
        if name == 'SWAPCX':
            pairs = [pair[::-1] for pair in pairs]
            name = 'CXSWAP'
        if name in SYMMETRIC_GATES:
            pairs = [sorted_complex(pair) for pair in pairs]
        if not pairs:
            return
        self.circuit.append(name, [self.q2i[q] for pair in pairs for q in pair])

    def shift_coords(self, *, dp: complex = 0, dt: int):
        self.circuit.append("SHIFT_COORDS", [], [dp.real, dp.imag, dt])

    def measure_patch(self, patch: 'Patch', *, save_layer: Any, cmp_layer: Optional[Any] = None) -> None:
        for tile in patch.tiles:
            self.measure_pauli_product(q2b={
                tile.ordered_data_qubits[k]: tile.bases[k]
                for k in range(len(tile.ordered_data_qubits))
                if tile.ordered_data_qubits[k] is not None
            }, key=AtLayer(tile.measurement_qubit, save_layer))
        if cmp_layer is not None:
            for tile in patch.tiles:
                m = tile.measurement_qubit
                self.detector([AtLayer(m, save_layer), AtLayer(m, cmp_layer)], pos=m)

    def demolition_measure_with_feedback_passthrough(
            self,
            xs: Iterable[complex] = (),
            ys: Iterable[complex] = (),
            zs: Iterable[complex] = (),
            *,
            tracker_key: Callable[[complex], Any] = lambda e: e,
            save_layer: Any) -> None:
        """Performs demolition measurements that look like measurements w.r.t. detectors.

        This is done by adding feedback operations that flip the demolished qubits depending
        on the measurement result. This feedback can then later be removed using
        stim.Circuit.with_inlined_feedback. The benefit is that it can be easier to
        programmatically create the detectors using the passthrough measurements, and
        then they can be automatically converted.
        """
        self.measure(qubits=xs, basis='X', tracker_key=tracker_key, save_layer=save_layer)
        self.measure(qubits=ys, basis='Y', tracker_key=tracker_key, save_layer=save_layer)
        self.measure(qubits=zs, basis='Z', tracker_key=tracker_key, save_layer=save_layer)
        self.tick()
        self.gate('RX', xs)
        self.gate('RY', ys)
        self.gate('RZ', zs)
        for (qs, b) in [(xs, 'Z'), (ys, 'X'), (zs, 'X')]:
            for q in qs:
                self.classical_paulis(control_keys=[AtLayer(tracker_key(q), save_layer)], targets=[q], basis=b)

    def measure(self,
                qubits: Iterable[complex],
                *,
                basis: str = 'Z',
                tracker_key: Callable[[complex], Any] = lambda e: e,
                save_layer: Any) -> None:
        qubits = sorted_complex(qubits)
        if not qubits:
            return
        self.circuit.append(f"M{basis}", [self.q2i[q] for q in qubits])
        for q in qubits:
            self.tracker.record_measurement(AtLayer(tracker_key(q), save_layer))

    def measure_pauli_product(self,
                              observable: Optional['PauliString'] = None,
                              *,
                              xs: Iterable[complex] = (),
                              ys: Iterable[complex] = (),
                              zs: Iterable[complex] = (),
                              b2qs: Dict[str, Iterable[complex]] = None,
                              q2b: Dict[complex, str] = None,
                              noise: Optional[float] = None,
                              key: Any):
        """Adds an MPP operation to measure the given qubits. Supports a variety of formats.

        Note that all formats are combined as if multiplying Pauli observables (ignoring phase and
        sign).

        Args:
            observable: A gen.PauliString to measure.
            xs: A list of qubits to include in the product as X basis terms.
            ys: A list of qubits to include in the product as Y basis terms.
            zs: A list of qubits to include in the product as Z basis terms.
            b2qs: A mapping from the desired basis to qubits to include in the product in that basis.
            q2b: A mapping from qubit to basis. Each qubit:basis pair is includedin the product.
            noise: Make the measurement noisy.
            key: Measurement key to track the result under.
        """
        x = set(xs)
        y = set(ys)
        z = set(zs)
        if b2qs is not None:
            for b, bqs in b2qs.items():
                if b == 'X':
                    x |= set(bqs)
                elif b == 'Y':
                    y |= set(bqs)
                elif b == 'Z':
                    z |= set(bqs)
                else:
                    raise NotImplementedError(f'{b=}')
        if q2b is not None:
            for q, b in q2b.items():
                if b == 'X':
                    x.add(q)
                elif b == 'Y':
                    y.add(q)
                elif b == 'Z':
                    z.add(q)
                else:
                    raise NotImplementedError(f'{b=}')
        if observable is not None:
            for q, b in observable.qubits.items():
                if b == 'X':
                    x.add(q)
                elif b == 'Y':
                    y.add(q)
                elif b == 'Z':
                    z.add(q)
                else:
                    raise NotImplementedError(f'{b=}')
        xz = x & z
        xy = x & y
        yz = y & z
        x -= xz
        x -= xy
        z -= xz
        z -= yz
        y -= xy
        y -= yz
        x |= yz
        y |= xz
        z |= xy
        vals = {}
        for q in x:
            vals[q] = stim.target_x(self.q2i[q])
        for q in y:
            vals[q] = stim.target_y(self.q2i[q])
        for q in z:
            vals[q] = stim.target_z(self.q2i[q])

        targets = []
        comb = stim.target_combiner()
        for q in sorted_complex(vals.keys()):
            targets.append(vals[q])
            targets.append(comb)
        if targets:
            targets.pop()
            self.circuit.append('MPP', targets, noise)
            self.tracker.record_measurement(key)
        else:
            self.tracker.make_measurement_group([], key=key)

    def detector(self,
                 keys: Iterable[Any],
                 *,
                 pos: Optional[complex],
                 t: float = 0,
                 extra_coords: Iterable[float] = (),
                 mark_as_post_selected: bool = False,
                 ignore_non_existent: bool = False) -> None:
        if pos is not None:
            coords = [pos.real, pos.imag, t] + list(extra_coords)
            if mark_as_post_selected:
                coords.append(1)
        else:
            if list(extra_coords):
                raise ValueError('pos is None but extra_coords is not empty')
            if mark_as_post_selected:
                raise ValueError('pos is None and mark_as_post_selected')
            coords = None

        if ignore_non_existent:
            keys = [k for k in keys if k in self.tracker.recorded]
        targets = self.tracker.current_measurement_record_targets_for(keys)
        self.circuit.append('DETECTOR', targets, coords)

    def obs_include(self,
                    keys: Iterable[Any],
                    *,
                    obs_index: int) -> None:
        ms = self.tracker.current_measurement_record_targets_for(keys)
        if ms:
            self.circuit.append(
                'OBSERVABLE_INCLUDE',
                ms,
                obs_index,
            )

    def tick(self) -> None:
        self.circuit.append('TICK')

    def cz(self, pairs: List[Tuple[complex, complex]]) -> None:
        sorted_pairs = []
        for a, b in pairs:
            if complex_key(a) > complex_key(b):
                a, b = b, a
            sorted_pairs.append((a, b))
        sorted_pairs = sorted(sorted_pairs, key=lambda e: (complex_key(e[0]), complex_key(e[1])))
        for a, b in sorted_pairs:
            self.circuit.append('CZ', [self.q2i[a], self.q2i[b]])

    def swap(self, pairs: List[Tuple[complex, complex]]) -> None:
        sorted_pairs = []
        for a, b in pairs:
            if complex_key(a) > complex_key(b):
                a, b = b, a
            sorted_pairs.append((a, b))
        sorted_pairs = sorted(sorted_pairs, key=lambda e: (complex_key(e[0]), complex_key(e[1])))
        for a, b in sorted_pairs:
            self.circuit.append('SWAP', [self.q2i[a], self.q2i[b]])

    def classical_paulis(self,
                         *,
                         control_keys: Iterable[Any],
                         targets: Iterable[complex],
                         basis: str) -> None:
        gate = f'C{basis}'
        indices = [self.q2i[q] for q in sorted_complex(targets)]
        for rec in self.tracker.current_measurement_record_targets_for(control_keys):
            for i in indices:
                self.circuit.append(gate, [rec, i])

    def plan_interactions(
            self,
            *,
            layer_count: int,
            start_orientations: Optional[Dict[complex, str]] = None,
            end_orientations: Optional[Dict[complex, str]] = None,
    ) -> 'InteractionPlanner':
        from gen._interaction_planner import InteractionPlanner
        return InteractionPlanner(
            layer_count=layer_count,
            builder=self,
            start_orientations=start_orientations,
            end_orientations=end_orientations,
        )

    def plan_rotations(self) -> 'SingleQubitGatesPlanner':
        from gen._interaction_planner import SingleQubitGatesPlanner
        return SingleQubitGatesPlanner(self)
