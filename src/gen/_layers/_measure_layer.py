import dataclasses
from typing import List, Optional, Set

import stim

from gen._layers._data import R_ZYX, R_XYZ, R_XZY
from gen._layers._layer import Layer
from gen._layers._rotation_layer import RotationLayer


@dataclasses.dataclass
class MeasureLayer(Layer):
    targets: List[int] = dataclasses.field(default_factory=list)
    bases: List[str] = dataclasses.field(default_factory=list)

    def copy(self) -> 'MeasureLayer':
        return MeasureLayer(targets=list(self.targets), bases=list(self.bases))

    def touched(self) -> Set[int]:
        return set(self.targets)

    def to_z_basis(self) -> List['Layer']:
        rot = RotationLayer({q: R_XYZ if b == 'Z' else R_ZYX if b == 'X' else R_XZY for q, b in zip(self.targets, self.bases)})
        return [
            rot,
            MeasureLayer(targets=list(self.targets), bases=['Z'] * len(self.targets)),
            rot.copy(),
        ]

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        for t, b in zip(self.targets, self.bases):
            out.append('M' + b, [t])

    def locally_optimized(self, next_layer: Optional['Layer']) -> List[Optional['Layer']]:
        if isinstance(next_layer, MeasureLayer) and set(self.targets).isdisjoint(next_layer.targets):
            return [MeasureLayer(
                targets=self.targets + next_layer.targets,
                bases=self.bases + next_layer.bases,
            )]
        return [self, next_layer]
