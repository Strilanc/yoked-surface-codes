import dataclasses
from typing import List, Dict, Set, Iterable

import stim

from gen._layers._layer import Layer


@dataclasses.dataclass
class QubitCoordAnnotationLayer(Layer):
    coords: Dict[int, List[float]] = dataclasses.field(default_factory=dict)

    def offset_by(self, args: Iterable[float]):
        for index, offset in enumerate(args):
            if offset:
                for q, qubit_coords in self.coords.items():
                    if index < len(qubit_coords):
                        qubit_coords[index] += offset

    def copy(self) -> 'Layer':
        return QubitCoordAnnotationLayer(coords=dict(self.coords))

    def touched(self) -> Set[int]:
        return set()

    def requires_tick_before(self) -> bool:
        return False

    def implies_eventual_tick_after(self) -> bool:
        return False

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        for q in sorted(self.coords.keys()):
            out.append('QUBIT_COORDS', [q], self.coords[q])
