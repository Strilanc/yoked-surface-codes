import dataclasses
from typing import List, Optional, Set, Iterable

import stim

from gen._layers._layer import Layer


@dataclasses.dataclass
class ShiftCoordAnnotationLayer(Layer):
    shift: List[float] = dataclasses.field(default_factory=list)

    def offset_by(self, args: Iterable[float]):
        for k, arg in enumerate(args):
            if k >= len(self.shift):
                self.shift.append(arg)
            else:
                self.shift[k] += arg

    def copy(self) -> 'ShiftCoordAnnotationLayer':
        return ShiftCoordAnnotationLayer(shift=self.shift)

    def touched(self) -> Set[int]:
        return set()

    def requires_tick_before(self) -> bool:
        return False

    def implies_eventual_tick_after(self) -> bool:
        return False

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        out.append('SHIFT_COORDS', [], self.shift)

    def locally_optimized(self, next_layer: Optional['Layer']) -> List[Optional['Layer']]:
        if isinstance(next_layer, ShiftCoordAnnotationLayer):
            result = self.copy()
            result.offset_by(next_layer.shift)
            return [result]
        return [self, next_layer]
