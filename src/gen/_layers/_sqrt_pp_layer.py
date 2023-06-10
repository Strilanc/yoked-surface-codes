import collections
import dataclasses
from typing import List, Set

import stim

from gen._layers._data import R_XZY, R_ZYX, R_YXZ
from gen._layers._interact_layer import InteractLayer
from gen._layers._layer import Layer
from gen._layers._rotation_layer import RotationLayer


@dataclasses.dataclass
class SqrtPPLayer(Layer):
    targets1: List[int] = dataclasses.field(default_factory=list)
    targets2: List[int] = dataclasses.field(default_factory=list)
    bases: List[str] = dataclasses.field(default_factory=list)

    def touched(self) -> Set[int]:
        return set(self.targets1 + self.targets2)

    def copy(self) -> 'SqrtPPLayer':
        return SqrtPPLayer(
            targets1=list(self.targets1),
            targets2=list(self.targets2),
            bases=list(self.bases),
        )

    def to_z_basis(self) -> List['Layer']:
        interact = InteractLayer()
        rot = RotationLayer()
        for q1, q2, b in zip(self.targets1, self.targets2, self.bases):
            interact.targets1.append(q1)
            interact.targets2.append(q2)
            interact.bases1.append(b)
            interact.bases1.append(b)
            if b == 'X':
                r = R_XZY
            elif b == 'Y':
                r = R_ZYX
            elif b == 'Z':
                r = R_YXZ
            else:
                raise NotImplementedError(f'{b=}')
            rot.append_rotation(r, q1)
            rot.append_rotation(r, q2)

        return [
            rot,
            *interact.to_z_basis(),
        ]

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        groups = collections.defaultdict(list)
        for q1, q2, b in zip(self.targets1, self.targets2, self.bases):
            gate = f'SQRT_{b}{b}'
            if q2 < q1:
                q1, q2 = q2, q1
            groups[gate].append((q1, q2))
        for gate in sorted(groups.keys()):
            for pair in sorted(groups[gate]):
                out.append(gate, pair)
