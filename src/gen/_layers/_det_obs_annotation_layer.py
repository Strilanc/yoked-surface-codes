import dataclasses
from typing import Set

import stim

from gen._layers._layer import Layer


@dataclasses.dataclass
class DetObsAnnotationLayer(Layer):
    circuit: stim.Circuit = dataclasses.field(default_factory=stim.Circuit)

    def copy(self) -> 'DetObsAnnotationLayer':
        return DetObsAnnotationLayer(circuit=self.circuit.copy())

    def touched(self) -> Set[int]:
        return set()

    def requires_tick_before(self) -> bool:
        return False

    def implies_eventual_tick_after(self) -> bool:
        return False

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        out += self.circuit
