import dataclasses
from typing import List, Optional, Set

import stim

from gen._layers._interact_layer import InteractLayer
from gen._layers._layer import Layer


@dataclasses.dataclass
class SwapLayer(Layer):
    targets1: List[int] = dataclasses.field(default_factory=list)
    targets2: List[int] = dataclasses.field(default_factory=list)

    def touched(self) -> Set[int]:
        return set(self.targets1 + self.targets2)

    def copy(self) -> 'SwapLayer':
        return SwapLayer(targets1=list(self.targets1), targets2=list(self.targets2))

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        pairs = []
        for k in range(len(self.targets1)):
            t1 = self.targets1[k]
            t2 = self.targets2[k]
            t1, t2 = sorted([t1, t2])
            pairs.append((t1, t2))
        for pair in sorted(pairs):
            out.append("SWAP", pair)

    def locally_optimized(self, next_layer: Optional['Layer']) -> List[Optional['Layer']]:
        if isinstance(next_layer, InteractLayer):
            from gen._layers._interact_swap_layer import InteractSwapLayer
            i = next_layer.copy()
            i.targets1, i.targets2 = i.targets2, i.targets1
            return [InteractSwapLayer(i_layer=i, swap_layer=self.copy())]
        return [self, next_layer]
