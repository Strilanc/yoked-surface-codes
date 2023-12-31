import dataclasses
from typing import List, Set

import stim

from gen._layers._data import R_ZYX, R_XZY
from gen._layers._layer import Layer
from gen._layers._rotation_layer import RotationLayer


@dataclasses.dataclass
class MppLayer(Layer):
    targets: List[List[stim.GateTarget]] = dataclasses.field(default_factory=list)

    def copy(self) -> 'MppLayer':
        return MppLayer(targets=[list(e) for e in self.targets])

    def touched(self) -> Set[int]:
        return set(t.value for mpp in self.targets for t in mpp)

    def to_z_basis(self) -> List['Layer']:
        assert len(self.touched()) == sum(len(e) for e in self.targets)
        rot = RotationLayer()
        new_targets: List[List[stim.GateTarget]] = []
        for groups in self.targets:
            new_group: List[stim.GateTarget] = []
            for t in groups:
                new_group.append(stim.target_z(t.value))
                if t.is_x_target:
                    rot.append_rotation(R_ZYX, t.value)
                elif t.is_y_target:
                    rot.append_rotation(R_XZY, t.value)
                elif not t.is_z_target:
                    raise NotImplementedError(f'{t=}')
            new_targets.append(new_group)

        return [
            rot,
            MppLayer(targets=new_targets),
            rot.copy(),
        ]

    def append_into_stim_circuit(self, out: stim.Circuit) -> None:
        flat_targets = []
        for group in self.targets:
            for t in group:
                flat_targets.append(t)
                flat_targets.append(stim.target_combiner())
            flat_targets.pop()
        out.append('MPP', flat_targets)
