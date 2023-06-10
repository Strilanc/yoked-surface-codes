from typing import Dict, Callable

import stim

import gen
from gen._core._util import sorted_complex
from gen._core._tile import Tile


class PauliString:
    """A qubit-to-pauli mapping."""
    def __init__(self, qubits: Dict[complex, str]):
        self.qubits = {q: qubits[q] for q in gen.sorted_complex(qubits.keys())}
        self._hash = hash(tuple(self.qubits.items()))

    @staticmethod
    def from_stim_pauli_string(stim_pauli_string: stim.PauliString) -> 'PauliString':
        return PauliString({
            q: '_XYZ'[stim_pauli_string[q]]
            for q in range(len(stim_pauli_string))
            if stim_pauli_string[q]
        })

    def __bool__(self):
        return bool(self.qubits)

    def __mul__(self, other: 'PauliString') -> 'PauliString':
        result = {}
        for q in self.qubits.keys() | other.qubits.keys():
            a = self.qubits.get(q, 'I')
            b = other.qubits.get(q, 'I')
            ax = a in 'XY'
            az = a in 'YZ'
            bx = b in 'XY'
            bz = b in 'YZ'
            cx = ax ^ bx
            cz = az ^ bz
            c = 'IXZY'[cx + cz*2]
            if c != 'I':
                result[q] = c
        return PauliString(result)

    def __repr__(self):
        return f'PauliString(qubits={self.qubits!r})'

    def __str__(self):
        return '*'.join(
            f'{self.qubits[q]}{q}'
            for q in sorted_complex(self.qubits.keys())
        )

    def with_xz_flipped(self) -> 'PauliString':
        return PauliString({
            q: "Z" if p == 'X' else 'X' if p == 'Z' else p for q, p in self.qubits.items()
        })

    def commutes(self, other: 'PauliString') -> bool:
        return not self.anticommutes(other)

    def anticommutes(self, other: 'PauliString') -> bool:
        t = 0
        for q in self.qubits.keys() & other.qubits.keys():
            t += self.qubits[q] != other.qubits[q]
        return t % 2 == 1

    def with_transformed_coords(self, transform: Callable[[complex], complex]) -> 'PauliString':
        return PauliString({
            transform(q): p for q, p in self.qubits.items()
        })

    @staticmethod
    def from_tile_data(tile: Tile) -> 'PauliString':
        return PauliString({
            k: v
            for k, v in zip(tile.ordered_data_qubits, tile.bases)
            if k is not None
        })

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, PauliString):
            return NotImplemented
        return self.qubits == other.qubits
