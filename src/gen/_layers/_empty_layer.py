import dataclasses
from typing import List, TypeVar, Type, Optional, cast, Set

import stim

from gen._layers._layer import Layer


@dataclasses.dataclass
class EmptyLayer(Layer):
    def copy(self) -> 'EmptyLayer':
        return EmptyLayer()

    def touched(self) -> Set[int]:
        return set()

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        pass

    def locally_optimized(self, next_layer: Optional['Layer']) -> List[Optional['Layer']]:
        return [next_layer]

    def is_vacuous(self) -> bool:
        return True
