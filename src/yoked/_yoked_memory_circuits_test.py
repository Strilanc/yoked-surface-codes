import itertools

import pytest
import stim

import gen
from yoked._yoked_memory_circuits import yoked_magic_memory_circuit


@pytest.mark.parametrize('num_patches,yokes,patch_diameter', itertools.product(
    [1, 2, 5],
    [0, 1, 2],
    [3, 4, 5, 6, 7]
))
def test_yoked_magic_memory_circuit(
        num_patches: int,
        yokes: int,
        patch_diameter: int,
):
    if num_patches < yokes:
        return
    c = yoked_magic_memory_circuit(
        patch_diameter=patch_diameter,
        rounds=7,
        noise=gen.NoiseModel.si1000(1e-3),
        yokes=yokes,
        num_patches=num_patches,
        style='cz',
    )
    assert c.num_observables == num_patches * 2
    assert c.detector_error_model(decompose_errors=True) is not None
    if yokes == 0:
        expected_distance = patch_diameter
    elif yokes == 1:
        expected_distance = 2*patch_diameter - 1
    elif yokes == 2:
        expected_distance = 2*patch_diameter
    actual_distance = len(c.shortest_graphlike_error())
    assert actual_distance == expected_distance


def test_yoked_magic_memory_circuit_exact():
    c = yoked_magic_memory_circuit(
        patch_diameter=4,
        rounds=100,
        noise=gen.NoiseModel.si1000(2**-6),
        yokes=1,
        num_patches=3,
        style='cz',
    )
    assert c == stim.Circuit("""
        QUBIT_COORDS(0, -2) 0
        QUBIT_COORDS(0, 0) 1
        QUBIT_COORDS(0, 1) 2
        QUBIT_COORDS(0, 2) 3
        QUBIT_COORDS(0, 3) 4
        QUBIT_COORDS(1, 0) 5
        QUBIT_COORDS(1, 1) 6
        QUBIT_COORDS(1, 2) 7
        QUBIT_COORDS(1, 3) 8
        QUBIT_COORDS(2, 0) 9
        QUBIT_COORDS(2, 1) 10
        QUBIT_COORDS(2, 2) 11
        QUBIT_COORDS(2, 3) 12
        QUBIT_COORDS(3, 0) 13
        QUBIT_COORDS(3, 1) 14
        QUBIT_COORDS(3, 2) 15
        QUBIT_COORDS(3, 3) 16
        QUBIT_COORDS(5, -2) 17
        QUBIT_COORDS(5, 0) 18
        QUBIT_COORDS(5, 1) 19
        QUBIT_COORDS(5, 2) 20
        QUBIT_COORDS(5, 3) 21
        QUBIT_COORDS(6, 0) 22
        QUBIT_COORDS(6, 1) 23
        QUBIT_COORDS(6, 2) 24
        QUBIT_COORDS(6, 3) 25
        QUBIT_COORDS(7, 0) 26
        QUBIT_COORDS(7, 1) 27
        QUBIT_COORDS(7, 2) 28
        QUBIT_COORDS(7, 3) 29
        QUBIT_COORDS(8, 0) 30
        QUBIT_COORDS(8, 1) 31
        QUBIT_COORDS(8, 2) 32
        QUBIT_COORDS(8, 3) 33
        QUBIT_COORDS(10, -2) 34
        QUBIT_COORDS(10, 0) 35
        QUBIT_COORDS(10, 1) 36
        QUBIT_COORDS(10, 2) 37
        QUBIT_COORDS(10, 3) 38
        QUBIT_COORDS(11, 0) 39
        QUBIT_COORDS(11, 1) 40
        QUBIT_COORDS(11, 2) 41
        QUBIT_COORDS(11, 3) 42
        QUBIT_COORDS(12, 0) 43
        QUBIT_COORDS(12, 1) 44
        QUBIT_COORDS(12, 2) 45
        QUBIT_COORDS(12, 3) 46
        QUBIT_COORDS(13, 0) 47
        QUBIT_COORDS(13, 1) 48
        QUBIT_COORDS(13, 2) 49
        QUBIT_COORDS(13, 3) 50
        QUBIT_COORDS(-0.5, 1.5) 51
        QUBIT_COORDS(0.5, -0.5) 52
        QUBIT_COORDS(0.5, 0.5) 53
        QUBIT_COORDS(0.5, 1.5) 54
        QUBIT_COORDS(0.5, 2.5) 55
        QUBIT_COORDS(0.5, 3.5) 56
        QUBIT_COORDS(1.5, 0.5) 57
        QUBIT_COORDS(1.5, 1.5) 58
        QUBIT_COORDS(1.5, 2.5) 59
        QUBIT_COORDS(2.5, -0.5) 60
        QUBIT_COORDS(2.5, 0.5) 61
        QUBIT_COORDS(2.5, 1.5) 62
        QUBIT_COORDS(2.5, 2.5) 63
        QUBIT_COORDS(2.5, 3.5) 64
        QUBIT_COORDS(3.5, 1.5) 65
        QUBIT_COORDS(4.5, 1.5) 66
        QUBIT_COORDS(5.5, -0.5) 67
        QUBIT_COORDS(5.5, 0.5) 68
        QUBIT_COORDS(5.5, 1.5) 69
        QUBIT_COORDS(5.5, 2.5) 70
        QUBIT_COORDS(5.5, 3.5) 71
        QUBIT_COORDS(6.5, 0.5) 72
        QUBIT_COORDS(6.5, 1.5) 73
        QUBIT_COORDS(6.5, 2.5) 74
        QUBIT_COORDS(7.5, -0.5) 75
        QUBIT_COORDS(7.5, 0.5) 76
        QUBIT_COORDS(7.5, 1.5) 77
        QUBIT_COORDS(7.5, 2.5) 78
        QUBIT_COORDS(7.5, 3.5) 79
        QUBIT_COORDS(8.5, 1.5) 80
        QUBIT_COORDS(9.5, 1.5) 81
        QUBIT_COORDS(10.5, -0.5) 82
        QUBIT_COORDS(10.5, 0.5) 83
        QUBIT_COORDS(10.5, 1.5) 84
        QUBIT_COORDS(10.5, 2.5) 85
        QUBIT_COORDS(10.5, 3.5) 86
        QUBIT_COORDS(11.5, 0.5) 87
        QUBIT_COORDS(11.5, 1.5) 88
        QUBIT_COORDS(11.5, 2.5) 89
        QUBIT_COORDS(12.5, -0.5) 90
        QUBIT_COORDS(12.5, 0.5) 91
        QUBIT_COORDS(12.5, 1.5) 92
        QUBIT_COORDS(12.5, 2.5) 93
        QUBIT_COORDS(12.5, 3.5) 94
        QUBIT_COORDS(13.5, 1.5) 95
        MPP X0*X1*X2*X3*X4
        OBSERVABLE_INCLUDE(0) rec[-1]
        MPP X17*X18*X19*X20*X21
        OBSERVABLE_INCLUDE(2) rec[-1]
        MPP X34*X35*X36*X37*X38
        OBSERVABLE_INCLUDE(4) rec[-1]
        MPP Z0*Z1*Z5*Z9*Z13
        OBSERVABLE_INCLUDE(1) rec[-1]
        MPP Z17*Z18*Z22*Z26*Z30
        OBSERVABLE_INCLUDE(3) rec[-1]
        MPP Z34*Z35*Z39*Z43*Z47
        OBSERVABLE_INCLUDE(5) rec[-1]
        MPP Z2*Z3 X1*X5 Z1*Z2*Z5*Z6 X2*X3*X6*X7 Z3*Z4*Z7*Z8 X4*X8 X5*X6*X9*X10 Z6*Z7*Z10*Z11 X7*X8*X11*X12 X9*X13 Z9*Z10*Z13*Z14 X10*X11*X14*X15 Z11*Z12*Z15*Z16 X12*X16 Z14*Z15 Z19*Z20 X18*X22 Z18*Z19*Z22*Z23 X19*X20*X23*X24 Z20*Z21*Z24*Z25 X21*X25 X22*X23*X26*X27 Z23*Z24*Z27*Z28 X24*X25*X28*X29 X26*X30 Z26*Z27*Z30*Z31 X27*X28*X31*X32 Z28*Z29*Z32*Z33 X29*X33 Z31*Z32 Z36*Z37 X35*X39 Z35*Z36*Z39*Z40 X36*X37*X40*X41 Z37*Z38*Z41*Z42 X38*X42 X39*X40*X43*X44 Z40*Z41*Z44*Z45 X41*X42*X45*X46 X43*X47 Z43*Z44*Z47*Z48 X44*X45*X48*X49 Z45*Z46*Z49*Z50 X46*X50 Z48*Z49
        TICK
        REPEAT 100 {
            R 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            X_ERROR(0.03125) 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            DEPOLARIZE1(0.0015625) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
            DEPOLARIZE1(0.03125) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
            TICK
            H 2 4 5 7 10 12 19 21 22 24 27 29 36 38 39 41 44 46 53 54 55 56 57 58 59 61 62 63 64 65 68 69 70 71 72 73 74 76 77 78 79 80 83 84 85 86 87 88 89 91 92 93 94 95
            DEPOLARIZE1(0.0015625) 2 4 5 7 10 12 19 21 22 24 27 29 36 38 39 41 44 46 53 54 55 56 57 58 59 61 62 63 64 65 68 69 70 71 72 73 74 76 77 78 79 80 83 84 85 86 87 88 89 91 92 93 94 95 1 3 6 8 9 11 13 14 15 16 18 20 23 25 26 28 30 31 32 33 35 37 40 42 43 45 47 48 49 50 51 52 60 66 67 75 81 82 90
            TICK
            CZ 1 53 2 54 3 55 4 56 5 57 6 58 7 59 9 61 10 62 11 63 12 64 14 65 18 68 19 69 20 70 21 71 22 72 23 73 24 74 26 76 27 77 28 78 29 79 31 80 35 83 36 84 37 85 38 86 39 87 40 88 41 89 43 91 44 92 45 93 46 94 48 95
            DEPOLARIZE2(0.015625) 1 53 2 54 3 55 4 56 5 57 6 58 7 59 9 61 10 62 11 63 12 64 14 65 18 68 19 69 20 70 21 71 22 72 23 73 24 74 26 76 27 77 28 78 29 79 31 80 35 83 36 84 37 85 38 86 39 87 40 88 41 89 43 91 44 92 45 93 46 94 48 95
            DEPOLARIZE1(0.0015625) 8 13 15 16 25 30 32 33 42 47 49 50 51 52 60 66 67 75 81 82 90
            TICK
            H 1 2 3 4 5 6 7 8 9 10 11 12 14 16 18 19 20 21 22 23 24 25 26 27 28 29 31 33 35 36 37 38 39 40 41 42 43 44 45 46 48 50 51 52 60 66 67 75 81 82 90
            DEPOLARIZE1(0.0015625) 1 2 3 4 5 6 7 8 9 10 11 12 14 16 18 19 20 21 22 23 24 25 26 27 28 29 31 33 35 36 37 38 39 40 41 42 43 44 45 46 48 50 51 52 60 66 67 75 81 82 90 13 15 30 32 47 49 53 54 55 56 57 58 59 61 62 63 64 65 68 69 70 71 72 73 74 76 77 78 79 80 83 84 85 86 87 88 89 91 92 93 94 95
            TICK
            CZ 2 53 4 55 6 54 7 58 8 56 9 57 10 61 11 59 12 63 14 62 15 65 16 64 19 68 21 70 23 69 24 73 25 71 26 72 27 76 28 74 29 78 31 77 32 80 33 79 36 83 38 85 40 84 41 88 42 86 43 87 44 91 45 89 46 93 48 92 49 95 50 94
            DEPOLARIZE2(0.015625) 2 53 4 55 6 54 7 58 8 56 9 57 10 61 11 59 12 63 14 62 15 65 16 64 19 68 21 70 23 69 24 73 25 71 26 72 27 76 28 74 29 78 31 77 32 80 33 79 36 83 38 85 40 84 41 88 42 86 43 87 44 91 45 89 46 93 48 92 49 95 50 94
            DEPOLARIZE1(0.0015625) 1 3 5 13 18 20 22 30 35 37 39 47 51 52 60 66 67 75 81 82 90
            TICK
            CZ 1 52 2 51 3 54 5 53 6 57 7 55 8 59 9 60 10 58 11 62 13 61 15 63 18 67 19 66 20 69 22 68 23 72 24 70 25 74 26 75 27 73 28 77 30 76 32 78 35 82 36 81 37 84 39 83 40 87 41 85 42 89 43 90 44 88 45 92 47 91 49 93
            DEPOLARIZE2(0.015625) 1 52 2 51 3 54 5 53 6 57 7 55 8 59 9 60 10 58 11 62 13 61 15 63 18 67 19 66 20 69 22 68 23 72 24 70 25 74 26 75 27 73 28 77 30 76 32 78 35 82 36 81 37 84 39 83 40 87 41 85 42 89 43 90 44 88 45 92 47 91 49 93
            DEPOLARIZE1(0.0015625) 4 12 14 16 21 29 31 33 38 46 48 50 56 64 65 71 79 80 86 94 95
            TICK
            H 3 5 6 7 8 10 11 12 13 14 15 16 20 22 23 24 25 27 28 29 30 31 32 33 37 39 40 41 42 44 45 46 47 48 49 50
            DEPOLARIZE1(0.0015625) 3 5 6 7 8 10 11 12 13 14 15 16 20 22 23 24 25 27 28 29 30 31 32 33 37 39 40 41 42 44 45 46 47 48 49 50 1 2 4 9 18 19 21 26 35 36 38 43 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            TICK
            CZ 3 51 5 52 6 53 7 54 8 55 10 57 11 58 12 59 13 60 14 61 15 62 16 63 20 66 22 67 23 68 24 69 25 70 27 72 28 73 29 74 30 75 31 76 32 77 33 78 37 81 39 82 40 83 41 84 42 85 44 87 45 88 46 89 47 90 48 91 49 92 50 93
            DEPOLARIZE2(0.015625) 3 51 5 52 6 53 7 54 8 55 10 57 11 58 12 59 13 60 14 61 15 62 16 63 20 66 22 67 23 68 24 69 25 70 27 72 28 73 29 74 30 75 31 76 32 77 33 78 37 81 39 82 40 83 41 84 42 85 44 87 45 88 46 89 47 90 48 91 49 92 50 93
            DEPOLARIZE1(0.0015625) 1 2 4 9 18 19 21 26 35 36 38 43 56 64 65 71 79 80 86 94 95
            TICK
            H 1 5 7 9 10 12 13 15 18 22 24 26 27 29 30 32 35 39 41 43 44 46 47 49 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            DEPOLARIZE1(0.0015625) 1 5 7 9 10 12 13 15 18 22 24 26 27 29 30 32 35 39 41 43 44 46 47 49 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 2 3 4 6 8 11 14 16 19 20 21 23 25 28 31 33 36 37 38 40 42 45 48 50
            TICK
            M(0.078125) 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            DETECTOR(-0.5, 1.5, 0) rec[-90] rec[-45]
            DETECTOR(0.5, -0.5, 0) rec[-89] rec[-44]
            DETECTOR(0.5, 0.5, 0) rec[-88] rec[-43]
            DETECTOR(0.5, 1.5, 0) rec[-87] rec[-42]
            DETECTOR(0.5, 2.5, 0) rec[-86] rec[-41]
            DETECTOR(0.5, 3.5, 0) rec[-85] rec[-40]
            DETECTOR(1.5, 0.5, 0) rec[-84] rec[-39]
            DETECTOR(1.5, 1.5, 0) rec[-83] rec[-38]
            DETECTOR(1.5, 2.5, 0) rec[-82] rec[-37]
            DETECTOR(2.5, -0.5, 0) rec[-81] rec[-36]
            DETECTOR(2.5, 0.5, 0) rec[-80] rec[-35]
            DETECTOR(2.5, 1.5, 0) rec[-79] rec[-34]
            DETECTOR(2.5, 2.5, 0) rec[-78] rec[-33]
            DETECTOR(2.5, 3.5, 0) rec[-77] rec[-32]
            DETECTOR(3.5, 1.5, 0) rec[-76] rec[-31]
            DETECTOR(4.5, 1.5, 0) rec[-75] rec[-30]
            DETECTOR(5.5, -0.5, 0) rec[-74] rec[-29]
            DETECTOR(5.5, 0.5, 0) rec[-73] rec[-28]
            DETECTOR(5.5, 1.5, 0) rec[-72] rec[-27]
            DETECTOR(5.5, 2.5, 0) rec[-71] rec[-26]
            DETECTOR(5.5, 3.5, 0) rec[-70] rec[-25]
            DETECTOR(6.5, 0.5, 0) rec[-69] rec[-24]
            DETECTOR(6.5, 1.5, 0) rec[-68] rec[-23]
            DETECTOR(6.5, 2.5, 0) rec[-67] rec[-22]
            DETECTOR(7.5, -0.5, 0) rec[-66] rec[-21]
            DETECTOR(7.5, 0.5, 0) rec[-65] rec[-20]
            DETECTOR(7.5, 1.5, 0) rec[-64] rec[-19]
            DETECTOR(7.5, 2.5, 0) rec[-63] rec[-18]
            DETECTOR(7.5, 3.5, 0) rec[-62] rec[-17]
            DETECTOR(8.5, 1.5, 0) rec[-61] rec[-16]
            DETECTOR(9.5, 1.5, 0) rec[-60] rec[-15]
            DETECTOR(10.5, -0.5, 0) rec[-59] rec[-14]
            DETECTOR(10.5, 0.5, 0) rec[-58] rec[-13]
            DETECTOR(10.5, 1.5, 0) rec[-57] rec[-12]
            DETECTOR(10.5, 2.5, 0) rec[-56] rec[-11]
            DETECTOR(10.5, 3.5, 0) rec[-55] rec[-10]
            DETECTOR(11.5, 0.5, 0) rec[-54] rec[-9]
            DETECTOR(11.5, 1.5, 0) rec[-53] rec[-8]
            DETECTOR(11.5, 2.5, 0) rec[-52] rec[-7]
            DETECTOR(12.5, -0.5, 0) rec[-51] rec[-6]
            DETECTOR(12.5, 0.5, 0) rec[-50] rec[-5]
            DETECTOR(12.5, 1.5, 0) rec[-49] rec[-4]
            DETECTOR(12.5, 2.5, 0) rec[-48] rec[-3]
            DETECTOR(12.5, 3.5, 0) rec[-47] rec[-2]
            DETECTOR(13.5, 1.5, 0) rec[-46] rec[-1]
            SHIFT_COORDS(0, 0, 1)
            DEPOLARIZE1(0.015625) 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            DEPOLARIZE1(0.0015625) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
            DEPOLARIZE1(0.03125) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
            TICK
        }
        MPP Z2*Z3 X1*X5 Z1*Z2*Z5*Z6 X2*X3*X6*X7 Z3*Z4*Z7*Z8 X4*X8 X5*X6*X9*X10 Z6*Z7*Z10*Z11 X7*X8*X11*X12 X9*X13 Z9*Z10*Z13*Z14 X10*X11*X14*X15 Z11*Z12*Z15*Z16 X12*X16 Z14*Z15 Z19*Z20 X18*X22 Z18*Z19*Z22*Z23 X19*X20*X23*X24 Z20*Z21*Z24*Z25 X21*X25 X22*X23*X26*X27 Z23*Z24*Z27*Z28 X24*X25*X28*X29 X26*X30 Z26*Z27*Z30*Z31 X27*X28*X31*X32 Z28*Z29*Z32*Z33 X29*X33 Z31*Z32 Z36*Z37 X35*X39 Z35*Z36*Z39*Z40 X36*X37*X40*X41 Z37*Z38*Z41*Z42 X38*X42 X39*X40*X43*X44 Z40*Z41*Z44*Z45 X41*X42*X45*X46 X43*X47 Z43*Z44*Z47*Z48 X44*X45*X48*X49 Z45*Z46*Z49*Z50 X46*X50 Z48*Z49
        DETECTOR(-0.5, 1.5, 0) rec[-90] rec[-45]
        DETECTOR(0.5, -0.5, 0) rec[-89] rec[-44]
        DETECTOR(0.5, 0.5, 0) rec[-88] rec[-43]
        DETECTOR(0.5, 1.5, 0) rec[-87] rec[-42]
        DETECTOR(0.5, 2.5, 0) rec[-86] rec[-41]
        DETECTOR(0.5, 3.5, 0) rec[-85] rec[-40]
        DETECTOR(1.5, 0.5, 0) rec[-84] rec[-39]
        DETECTOR(1.5, 1.5, 0) rec[-83] rec[-38]
        DETECTOR(1.5, 2.5, 0) rec[-82] rec[-37]
        DETECTOR(2.5, -0.5, 0) rec[-81] rec[-36]
        DETECTOR(2.5, 0.5, 0) rec[-80] rec[-35]
        DETECTOR(2.5, 1.5, 0) rec[-79] rec[-34]
        DETECTOR(2.5, 2.5, 0) rec[-78] rec[-33]
        DETECTOR(2.5, 3.5, 0) rec[-77] rec[-32]
        DETECTOR(3.5, 1.5, 0) rec[-76] rec[-31]
        DETECTOR(4.5, 1.5, 0) rec[-75] rec[-30]
        DETECTOR(5.5, -0.5, 0) rec[-74] rec[-29]
        DETECTOR(5.5, 0.5, 0) rec[-73] rec[-28]
        DETECTOR(5.5, 1.5, 0) rec[-72] rec[-27]
        DETECTOR(5.5, 2.5, 0) rec[-71] rec[-26]
        DETECTOR(5.5, 3.5, 0) rec[-70] rec[-25]
        DETECTOR(6.5, 0.5, 0) rec[-69] rec[-24]
        DETECTOR(6.5, 1.5, 0) rec[-68] rec[-23]
        DETECTOR(6.5, 2.5, 0) rec[-67] rec[-22]
        DETECTOR(7.5, -0.5, 0) rec[-66] rec[-21]
        DETECTOR(7.5, 0.5, 0) rec[-65] rec[-20]
        DETECTOR(7.5, 1.5, 0) rec[-64] rec[-19]
        DETECTOR(7.5, 2.5, 0) rec[-63] rec[-18]
        DETECTOR(7.5, 3.5, 0) rec[-62] rec[-17]
        DETECTOR(8.5, 1.5, 0) rec[-61] rec[-16]
        DETECTOR(9.5, 1.5, 0) rec[-60] rec[-15]
        DETECTOR(10.5, -0.5, 0) rec[-59] rec[-14]
        DETECTOR(10.5, 0.5, 0) rec[-58] rec[-13]
        DETECTOR(10.5, 1.5, 0) rec[-57] rec[-12]
        DETECTOR(10.5, 2.5, 0) rec[-56] rec[-11]
        DETECTOR(10.5, 3.5, 0) rec[-55] rec[-10]
        DETECTOR(11.5, 0.5, 0) rec[-54] rec[-9]
        DETECTOR(11.5, 1.5, 0) rec[-53] rec[-8]
        DETECTOR(11.5, 2.5, 0) rec[-52] rec[-7]
        DETECTOR(12.5, -0.5, 0) rec[-51] rec[-6]
        DETECTOR(12.5, 0.5, 0) rec[-50] rec[-5]
        DETECTOR(12.5, 1.5, 0) rec[-49] rec[-4]
        DETECTOR(12.5, 2.5, 0) rec[-48] rec[-3]
        DETECTOR(12.5, 3.5, 0) rec[-47] rec[-2]
        DETECTOR(13.5, 1.5, 0) rec[-46] rec[-1]
        MPP X0*X1*X2*X3*X4
        OBSERVABLE_INCLUDE(0) rec[-1]
        MPP X17*X18*X19*X20*X21
        OBSERVABLE_INCLUDE(2) rec[-1]
        MPP X34*X35*X36*X37*X38
        OBSERVABLE_INCLUDE(4) rec[-1]
        MPP Z0*Z1*Z5*Z9*Z13
        OBSERVABLE_INCLUDE(1) rec[-1]
        MPP Z17*Z18*Z22*Z26*Z30
        OBSERVABLE_INCLUDE(3) rec[-1]
        MPP Z34*Z35*Z39*Z43*Z47
        OBSERVABLE_INCLUDE(5) rec[-1]
        DETECTOR(0, -2, 0) rec[-4602] rec[-4601] rec[-4600] rec[-4599] rec[-4598] rec[-4597] rec[-6] rec[-5] rec[-4] rec[-3] rec[-2] rec[-1]
    """)
