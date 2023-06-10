import pytest

from gen._surf._open_curve import OpenCurve


def test_to_from_sequence():
    c1 = OpenCurve(points=[1, 5, 9 + 4j, 9], bases=['Z', 'X', 'X'])
    assert c1.to_sequence() == [1, 'Z', 5, 'X', (9+4j), 'X', 9]
    assert OpenCurve.from_sequence([1, 'Z', 5, 'X', (9+4j), 'X', 9]) == c1
    assert OpenCurve.from_sequence(['Z', 1, 5, 'X', (9+4j), 'X', 9]) == c1
    assert OpenCurve.from_sequence([1, 'Z', 5, 'X', (9+4j), 9]) == c1
    assert OpenCurve.from_sequence([1, 'Z', 5, 'X', 'Z', 'X', (9+4j), 9]) == c1
    assert OpenCurve.from_sequence([1, 'Z', 5, 'X', 5, 'Z', 'X', (9+4j), 9]) == c1
    assert OpenCurve.from_sequence(['Z', 'Z', 'Z', 1, 'Z', 5, 'X', 5, 'Z', 'X', (9+4j), 9, 'X', 'Z']) == c1

    with pytest.raises(ValueError, match='len.+points.+< 2'):
        OpenCurve.from_sequence([])
    with pytest.raises(ValueError, match='len.+points.+< 2'):
        OpenCurve.from_sequence([1])
    with pytest.raises(ValueError, match='len.+points.+< 2'):
        OpenCurve.from_sequence([1, 'X'])
    with pytest.raises(NotImplementedError):
        OpenCurve.from_sequence([1, 'Y', 2])
    with pytest.raises(ValueError, match='len.+points.+< 2'):
        OpenCurve.from_sequence([1, 'X', 'X'])


def test_iter():
    c1 = OpenCurve(points=[1, 5, 9 + 4j, 9], bases=['Z', 'X', 'X'])
    assert list(c1) == [
        ('Z', 1, 5),
        ('X', 5, (9+4j)),
        ('X', (9+4j), 9),
    ]


def test_int_points_in_order():
    c1 = OpenCurve(points=[1, 5, 9 + 4j, 9], bases=['Z', 'X', 'X'])
    assert c1.int_points_in_order() == [
        1+0j,
        2+0j,
        3+0j,
        4+0j,
        5+0j,
        6+1j,
        7+2j,
        8+3j,
        9+4j,
        9+3j,
        9+2j,
        9+1j,
        9+0j,
    ]
