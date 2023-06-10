import dataclasses
from typing import List, Optional, Set

import stim

from gen._layers._data import R_XYZ, R_ZYX, R_XZY
from gen._layers._layer import Layer
from gen._layers._rotation_layer import RotationLayer


@dataclasses.dataclass
class ResetLayer(Layer):
    targets: List[int] = dataclasses.field(default_factory=list)
    bases: List[str] = dataclasses.field(default_factory=list)

    def copy(self) -> 'ResetLayer':
        return ResetLayer(targets=list(self.targets), bases=list(self.bases))

    def touched(self) -> Set[int]:
        return set(self.targets)

    def to_z_basis(self) -> List['Layer']:
        return [
            ResetLayer(targets=list(self.targets), bases=['Z'] * len(self.targets)),
            RotationLayer({q: R_XYZ if b == 'Z' else R_ZYX if b == 'X' else R_XZY for q, b in zip(self.targets, self.bases)}),
        ]

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        for t, b in zip(self.targets, self.bases):
            out.append('R' + b, [t])

    def locally_optimized(self, next_layer: Optional['Layer']) -> List[Optional['Layer']]:
        if isinstance(next_layer, ResetLayer):
            combined_dict = {}
            for layer in [self, next_layer]:
                for t, b in zip(layer.targets, layer.bases):
                    combined_dict[t] = b
            combined = ResetLayer()
            for t, b in combined_dict.items():
                combined.targets.append(t)
                combined.bases.append(b)
            return [combined]
        return [self, next_layer]
