UL, UR, DL, DR = [e * 0.5 for e in [-1 - 1j, +1 - 1j, -1 + 1j, +1 + 1j]]
Order_Z = [UL, UR, DL, DR]
Order_ᴎ = [UL, DL, UR, DR]
Order_N = [DL, UL, DR, UR]
Order_S = [DL, DR, UL, UR]


def checkerboard_basis(q: complex) -> str:
    """Classifies a coordinate as X type or Z type according to a checkerboard.
    """
    is_x = int(q.real + q.imag) & 1 == 0
    return 'X' if is_x else 'Z'
