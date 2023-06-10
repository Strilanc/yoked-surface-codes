import dataclasses
from typing import Iterable, Dict, Any, Optional, List, TYPE_CHECKING

import stim


@dataclasses.dataclass(frozen=True)
class AtLayer:
    """A special class that indicates the layer to read a measurement key from."""
    key: Any
    layer: Any


class MeasurementTracker:
    """Tracks measurements and groups of measurements, for producing stim record targets."""
    def __init__(self):
        self.recorded: Dict[Any, Optional[List[int]]] = {}
        self.next_measurement_index = 0

    def copy(self) -> 'MeasurementTracker':
        result = MeasurementTracker()
        result.recorded = {k: list(v) for k, v in self.recorded.items()}
        result.next_measurement_index = self.next_measurement_index
        return result

    def _rec(self, key: Any, value: Optional[List[int]]) -> None:
        if key in self.recorded:
            raise ValueError(f'Measurement key collision: {key=}')
        self.recorded[key] = value

    def record_measurement(self, key: Any) -> None:
        self._rec(key, [self.next_measurement_index])
        self.next_measurement_index += 1

    def make_measurement_group(self, sub_keys: Iterable[Any], *, key: Any) -> None:
        self._rec(key, self.measurement_indices(sub_keys))

    def record_obstacle(self, key: Any) -> None:
        self._rec(key, None)

    def measurement_indices(self, keys: Iterable[Any]) -> List[int]:
        result = set()
        for key in keys:
            if key not in self.recorded:
                raise ValueError(f"No such measurement: {key=}")
            for v in self.recorded[key]:
                if v is None:
                    raise ValueError(f"Obstacle at {key=}")
                if v in result:
                    result.remove(v)
                else:
                    result.add(v)
        return sorted(result)

    def current_measurement_record_targets_for(self, keys: Iterable[Any]) -> List[stim.GateTarget]:
        t0 = self.next_measurement_index
        times = self.measurement_indices(keys)
        return [stim.target_rec(t - t0) for t in sorted(times)]
