import itertools

import pytest
import stim

import gen
from yoked._squareberg_circuits import squareberg_magic_memory_circuit, \
    squareberg_phenomenological_circuit


@pytest.mark.parametrize('patch_diameter,num_patches', itertools.product([2, 3, 4], [16, 64]))
def test_squareberg_magic_memory_circuit(
        patch_diameter: int,
        num_patches: int,
):
    c = squareberg_magic_memory_circuit(
        patch_diameter=patch_diameter,
        rounds=6,
        noise=gen.NoiseModel.si1000(1e-3),
        num_patches=num_patches,
        style='cz',
    )
    assert c.num_observables == num_patches * 2
    assert c.detector_error_model(decompose_errors=True) is not None
    actual_distance = len(c.shortest_graphlike_error())
    assert actual_distance == patch_diameter * 4


def test_yoked_magic_memory_circuit_exact():
    c = squareberg_magic_memory_circuit(
        patch_diameter=2,
        rounds=100,
        num_patches=16,
        style='css',
        noise=None,
    )
    assert c == stim.Circuit("""
        QUBIT_COORDS(0, 0) 0
        QUBIT_COORDS(0, 1) 1
        QUBIT_COORDS(0, 3) 2
        QUBIT_COORDS(0, 4) 3
        QUBIT_COORDS(0, 6) 4
        QUBIT_COORDS(0, 7) 5
        QUBIT_COORDS(0, 9) 6
        QUBIT_COORDS(0, 10) 7
        QUBIT_COORDS(1, 0) 8
        QUBIT_COORDS(1, 1) 9
        QUBIT_COORDS(1, 3) 10
        QUBIT_COORDS(1, 4) 11
        QUBIT_COORDS(1, 6) 12
        QUBIT_COORDS(1, 7) 13
        QUBIT_COORDS(1, 9) 14
        QUBIT_COORDS(1, 10) 15
        QUBIT_COORDS(3, 0) 16
        QUBIT_COORDS(3, 1) 17
        QUBIT_COORDS(3, 3) 18
        QUBIT_COORDS(3, 4) 19
        QUBIT_COORDS(3, 6) 20
        QUBIT_COORDS(3, 7) 21
        QUBIT_COORDS(3, 9) 22
        QUBIT_COORDS(3, 10) 23
        QUBIT_COORDS(4, 0) 24
        QUBIT_COORDS(4, 1) 25
        QUBIT_COORDS(4, 3) 26
        QUBIT_COORDS(4, 4) 27
        QUBIT_COORDS(4, 6) 28
        QUBIT_COORDS(4, 7) 29
        QUBIT_COORDS(4, 9) 30
        QUBIT_COORDS(4, 10) 31
        QUBIT_COORDS(6, 0) 32
        QUBIT_COORDS(6, 1) 33
        QUBIT_COORDS(6, 3) 34
        QUBIT_COORDS(6, 4) 35
        QUBIT_COORDS(6, 6) 36
        QUBIT_COORDS(6, 7) 37
        QUBIT_COORDS(6, 9) 38
        QUBIT_COORDS(6, 10) 39
        QUBIT_COORDS(7, 0) 40
        QUBIT_COORDS(7, 1) 41
        QUBIT_COORDS(7, 3) 42
        QUBIT_COORDS(7, 4) 43
        QUBIT_COORDS(7, 6) 44
        QUBIT_COORDS(7, 7) 45
        QUBIT_COORDS(7, 9) 46
        QUBIT_COORDS(7, 10) 47
        QUBIT_COORDS(9, 0) 48
        QUBIT_COORDS(9, 1) 49
        QUBIT_COORDS(9, 3) 50
        QUBIT_COORDS(9, 4) 51
        QUBIT_COORDS(9, 6) 52
        QUBIT_COORDS(9, 7) 53
        QUBIT_COORDS(9, 9) 54
        QUBIT_COORDS(9, 10) 55
        QUBIT_COORDS(10, 0) 56
        QUBIT_COORDS(10, 1) 57
        QUBIT_COORDS(10, 3) 58
        QUBIT_COORDS(10, 4) 59
        QUBIT_COORDS(10, 6) 60
        QUBIT_COORDS(10, 7) 61
        QUBIT_COORDS(10, 9) 62
        QUBIT_COORDS(10, 10) 63
        QUBIT_COORDS(-0.25, -0.25) 64
        QUBIT_COORDS(-0.25, 2.75) 65
        QUBIT_COORDS(-0.25, 5.75) 66
        QUBIT_COORDS(-0.25, 8.75) 67
        QUBIT_COORDS(0.5, -0.5) 68
        QUBIT_COORDS(0.5, 0.5) 69
        QUBIT_COORDS(0.5, 1.5) 70
        QUBIT_COORDS(0.5, 2.5) 71
        QUBIT_COORDS(0.5, 3.5) 72
        QUBIT_COORDS(0.5, 4.5) 73
        QUBIT_COORDS(0.5, 5.5) 74
        QUBIT_COORDS(0.5, 6.5) 75
        QUBIT_COORDS(0.5, 7.5) 76
        QUBIT_COORDS(0.5, 8.5) 77
        QUBIT_COORDS(0.5, 9.5) 78
        QUBIT_COORDS(0.5, 10.5) 79
        QUBIT_COORDS(2.75, -0.25) 80
        QUBIT_COORDS(2.75, 2.75) 81
        QUBIT_COORDS(2.75, 5.75) 82
        QUBIT_COORDS(2.75, 8.75) 83
        QUBIT_COORDS(3.5, -0.5) 84
        QUBIT_COORDS(3.5, 0.5) 85
        QUBIT_COORDS(3.5, 1.5) 86
        QUBIT_COORDS(3.5, 2.5) 87
        QUBIT_COORDS(3.5, 3.5) 88
        QUBIT_COORDS(3.5, 4.5) 89
        QUBIT_COORDS(3.5, 5.5) 90
        QUBIT_COORDS(3.5, 6.5) 91
        QUBIT_COORDS(3.5, 7.5) 92
        QUBIT_COORDS(3.5, 8.5) 93
        QUBIT_COORDS(3.5, 9.5) 94
        QUBIT_COORDS(3.5, 10.5) 95
        QUBIT_COORDS(5.75, -0.25) 96
        QUBIT_COORDS(5.75, 2.75) 97
        QUBIT_COORDS(5.75, 5.75) 98
        QUBIT_COORDS(5.75, 8.75) 99
        QUBIT_COORDS(6.5, -0.5) 100
        QUBIT_COORDS(6.5, 0.5) 101
        QUBIT_COORDS(6.5, 1.5) 102
        QUBIT_COORDS(6.5, 2.5) 103
        QUBIT_COORDS(6.5, 3.5) 104
        QUBIT_COORDS(6.5, 4.5) 105
        QUBIT_COORDS(6.5, 5.5) 106
        QUBIT_COORDS(6.5, 6.5) 107
        QUBIT_COORDS(6.5, 7.5) 108
        QUBIT_COORDS(6.5, 8.5) 109
        QUBIT_COORDS(6.5, 9.5) 110
        QUBIT_COORDS(6.5, 10.5) 111
        QUBIT_COORDS(8.75, -0.25) 112
        QUBIT_COORDS(8.75, 2.75) 113
        QUBIT_COORDS(8.75, 5.75) 114
        QUBIT_COORDS(8.75, 8.75) 115
        QUBIT_COORDS(9.5, -0.5) 116
        QUBIT_COORDS(9.5, 0.5) 117
        QUBIT_COORDS(9.5, 1.5) 118
        QUBIT_COORDS(9.5, 2.5) 119
        QUBIT_COORDS(9.5, 3.5) 120
        QUBIT_COORDS(9.5, 4.5) 121
        QUBIT_COORDS(9.5, 5.5) 122
        QUBIT_COORDS(9.5, 6.5) 123
        QUBIT_COORDS(9.5, 7.5) 124
        QUBIT_COORDS(9.5, 8.5) 125
        QUBIT_COORDS(9.5, 9.5) 126
        QUBIT_COORDS(9.5, 10.5) 127
        MPP X0*X1*X64 X8*X9*X64 Z0*Z8*Z64 Z1*Z9*Z64 X2*X3*X65 X10*X11*X65 Z2*Z10*Z65 Z3*Z11*Z65 X4*X5*X66 X12*X13*X66 Z4*Z12*Z66 Z5*Z13*Z66 X6*X7*X67 X14*X15*X67 Z6*Z14*Z67 Z7*Z15*Z67 X16*X17*X80 X24*X25*X80 Z16*Z24*Z80 Z17*Z25*Z80 X18*X19*X81 X26*X27*X81 Z18*Z26*Z81 Z19*Z27*Z81 X20*X21*X82 X28*X29*X82 Z20*Z28*Z82 Z21*Z29*Z82 X22*X23*X83 X30*X31*X83 Z22*Z30*Z83 Z23*Z31*Z83 X32*X33*X96 X40*X41*X96 Z32*Z40*Z96 Z33*Z41*Z96 X34*X35*X97 X42*X43*X97 Z34*Z42*Z97 Z35*Z43*Z97 X36*X37*X98 X44*X45*X98 Z36*Z44*Z98 Z37*Z45*Z98 X38*X39*X99 X46*X47*X99 Z38*Z46*Z99 Z39*Z47*Z99 X48*X49*X112 X56*X57*X112 Z48*Z56*Z112 Z49*Z57*Z112 X50*X51*X113 X58*X59*X113 Z50*Z58*Z113 Z51*Z59*Z113 X52*X53*X114 X60*X61*X114 Z52*Z60*Z114 Z53*Z61*Z114 X54*X55*X115 X62*X63*X115 Z54*Z62*Z115 Z55*Z63*Z115 X0*X8 Z0*Z1*Z8*Z9 X1*X9 X2*X10 Z2*Z3*Z10*Z11 X3*X11 X4*X12 Z4*Z5*Z12*Z13 X5*X13 X6*X14 Z6*Z7*Z14*Z15 X7*X15 X16*X24 Z16*Z17*Z24*Z25 X17*X25 X18*X26 Z18*Z19*Z26*Z27 X19*X27 X20*X28 Z20*Z21*Z28*Z29 X21*X29 X22*X30 Z22*Z23*Z30*Z31 X23*X31 X32*X40 Z32*Z33*Z40*Z41 X33*X41 X34*X42 Z34*Z35*Z42*Z43 X35*X43 X36*X44 Z36*Z37*Z44*Z45 X37*X45 X38*X46 Z38*Z39*Z46*Z47 X39*X47 X48*X56 Z48*Z49*Z56*Z57 X49*X57 X50*X58 Z50*Z51*Z58*Z59 X51*X59 X52*X60 Z52*Z53*Z60*Z61 X53*X61 X54*X62 Z54*Z55*Z62*Z63 X55*X63
        TICK
        REPEAT 100 {
            RX 68 70 71 73 74 76 77 79 84 86 87 89 90 92 93 95 100 102 103 105 106 108 109 111 116 118 119 121 122 124 125 127
            R 69 72 75 78 85 88 91 94 101 104 107 110 117 120 123 126
            TICK
            CX 0 69 2 72 4 75 6 78 16 85 18 88 20 91 22 94 32 101 34 104 36 107 38 110 48 117 50 120 52 123 54 126 70 1 73 3 76 5 79 7 86 17 89 19 92 21 95 23 102 33 105 35 108 37 111 39 118 49 121 51 124 53 127 55
            TICK
            CX 1 69 3 72 5 75 7 78 17 85 19 88 21 91 23 94 33 101 35 104 37 107 39 110 49 117 51 120 53 123 55 126 70 9 73 11 76 13 79 15 86 25 89 27 92 29 95 31 102 41 105 43 108 45 111 47 118 57 121 59 124 61 127 63
            TICK
            CX 8 69 10 72 12 75 14 78 24 85 26 88 28 91 30 94 40 101 42 104 44 107 46 110 56 117 58 120 60 123 62 126 68 0 71 2 74 4 77 6 84 16 87 18 90 20 93 22 100 32 103 34 106 36 109 38 116 48 119 50 122 52 125 54
            TICK
            CX 9 69 11 72 13 75 15 78 25 85 27 88 29 91 31 94 41 101 43 104 45 107 47 110 57 117 59 120 61 123 63 126 68 8 71 10 74 12 77 14 84 24 87 26 90 28 93 30 100 40 103 42 106 44 109 46 116 56 119 58 122 60 125 62
            TICK
            MX 68 70 71 73 74 76 77 79 84 86 87 89 90 92 93 95 100 102 103 105 106 108 109 111 116 118 119 121 122 124 125 127
            M 69 72 75 78 85 88 91 94 101 104 107 110 117 120 123 126
            DETECTOR(0.5, -0.5, 0) rec[-96] rec[-48]
            DETECTOR(0.5, 0.5, 0) rec[-95] rec[-16]
            DETECTOR(0.5, 1.5, 0) rec[-94] rec[-47]
            DETECTOR(0.5, 2.5, 0) rec[-93] rec[-46]
            DETECTOR(0.5, 3.5, 0) rec[-92] rec[-15]
            DETECTOR(0.5, 4.5, 0) rec[-91] rec[-45]
            DETECTOR(0.5, 5.5, 0) rec[-90] rec[-44]
            DETECTOR(0.5, 6.5, 0) rec[-89] rec[-14]
            DETECTOR(0.5, 7.5, 0) rec[-88] rec[-43]
            DETECTOR(0.5, 8.5, 0) rec[-87] rec[-42]
            DETECTOR(0.5, 9.5, 0) rec[-86] rec[-13]
            DETECTOR(0.5, 10.5, 0) rec[-85] rec[-41]
            DETECTOR(3.5, -0.5, 0) rec[-84] rec[-40]
            DETECTOR(3.5, 0.5, 0) rec[-83] rec[-12]
            DETECTOR(3.5, 1.5, 0) rec[-82] rec[-39]
            DETECTOR(3.5, 2.5, 0) rec[-81] rec[-38]
            DETECTOR(3.5, 3.5, 0) rec[-80] rec[-11]
            DETECTOR(3.5, 4.5, 0) rec[-79] rec[-37]
            DETECTOR(3.5, 5.5, 0) rec[-78] rec[-36]
            DETECTOR(3.5, 6.5, 0) rec[-77] rec[-10]
            DETECTOR(3.5, 7.5, 0) rec[-76] rec[-35]
            DETECTOR(3.5, 8.5, 0) rec[-75] rec[-34]
            DETECTOR(3.5, 9.5, 0) rec[-74] rec[-9]
            DETECTOR(3.5, 10.5, 0) rec[-73] rec[-33]
            DETECTOR(6.5, -0.5, 0) rec[-72] rec[-32]
            DETECTOR(6.5, 0.5, 0) rec[-71] rec[-8]
            DETECTOR(6.5, 1.5, 0) rec[-70] rec[-31]
            DETECTOR(6.5, 2.5, 0) rec[-69] rec[-30]
            DETECTOR(6.5, 3.5, 0) rec[-68] rec[-7]
            DETECTOR(6.5, 4.5, 0) rec[-67] rec[-29]
            DETECTOR(6.5, 5.5, 0) rec[-66] rec[-28]
            DETECTOR(6.5, 6.5, 0) rec[-65] rec[-6]
            DETECTOR(6.5, 7.5, 0) rec[-64] rec[-27]
            DETECTOR(6.5, 8.5, 0) rec[-63] rec[-26]
            DETECTOR(6.5, 9.5, 0) rec[-62] rec[-5]
            DETECTOR(6.5, 10.5, 0) rec[-61] rec[-25]
            DETECTOR(9.5, -0.5, 0) rec[-60] rec[-24]
            DETECTOR(9.5, 0.5, 0) rec[-59] rec[-4]
            DETECTOR(9.5, 1.5, 0) rec[-58] rec[-23]
            DETECTOR(9.5, 2.5, 0) rec[-57] rec[-22]
            DETECTOR(9.5, 3.5, 0) rec[-56] rec[-3]
            DETECTOR(9.5, 4.5, 0) rec[-55] rec[-21]
            DETECTOR(9.5, 5.5, 0) rec[-54] rec[-20]
            DETECTOR(9.5, 6.5, 0) rec[-53] rec[-2]
            DETECTOR(9.5, 7.5, 0) rec[-52] rec[-19]
            DETECTOR(9.5, 8.5, 0) rec[-51] rec[-18]
            DETECTOR(9.5, 9.5, 0) rec[-50] rec[-1]
            DETECTOR(9.5, 10.5, 0) rec[-49] rec[-17]
            SHIFT_COORDS(0, 0, 1)
            TICK
        }
        MPP X0*X8 Z0*Z1*Z8*Z9 X1*X9 X2*X10 Z2*Z3*Z10*Z11 X3*X11 X4*X12 Z4*Z5*Z12*Z13 X5*X13 X6*X14 Z6*Z7*Z14*Z15 X7*X15 X16*X24 Z16*Z17*Z24*Z25 X17*X25 X18*X26 Z18*Z19*Z26*Z27 X19*X27 X20*X28 Z20*Z21*Z28*Z29 X21*X29 X22*X30 Z22*Z23*Z30*Z31 X23*X31 X32*X40 Z32*Z33*Z40*Z41 X33*X41 X34*X42 Z34*Z35*Z42*Z43 X35*X43 X36*X44 Z36*Z37*Z44*Z45 X37*X45 X38*X46 Z38*Z39*Z46*Z47 X39*X47 X48*X56 Z48*Z49*Z56*Z57 X49*X57 X50*X58 Z50*Z51*Z58*Z59 X51*X59 X52*X60 Z52*Z53*Z60*Z61 X53*X61 X54*X62 Z54*Z55*Z62*Z63 X55*X63
        DETECTOR(0.5, -0.5, 0) rec[-96] rec[-48]
        DETECTOR(0.5, 0.5, 0) rec[-64] rec[-47]
        DETECTOR(0.5, 1.5, 0) rec[-95] rec[-46]
        DETECTOR(0.5, 2.5, 0) rec[-94] rec[-45]
        DETECTOR(0.5, 3.5, 0) rec[-63] rec[-44]
        DETECTOR(0.5, 4.5, 0) rec[-93] rec[-43]
        DETECTOR(0.5, 5.5, 0) rec[-92] rec[-42]
        DETECTOR(0.5, 6.5, 0) rec[-62] rec[-41]
        DETECTOR(0.5, 7.5, 0) rec[-91] rec[-40]
        DETECTOR(0.5, 8.5, 0) rec[-90] rec[-39]
        DETECTOR(0.5, 9.5, 0) rec[-61] rec[-38]
        DETECTOR(0.5, 10.5, 0) rec[-89] rec[-37]
        DETECTOR(3.5, -0.5, 0) rec[-88] rec[-36]
        DETECTOR(3.5, 0.5, 0) rec[-60] rec[-35]
        DETECTOR(3.5, 1.5, 0) rec[-87] rec[-34]
        DETECTOR(3.5, 2.5, 0) rec[-86] rec[-33]
        DETECTOR(3.5, 3.5, 0) rec[-59] rec[-32]
        DETECTOR(3.5, 4.5, 0) rec[-85] rec[-31]
        DETECTOR(3.5, 5.5, 0) rec[-84] rec[-30]
        DETECTOR(3.5, 6.5, 0) rec[-58] rec[-29]
        DETECTOR(3.5, 7.5, 0) rec[-83] rec[-28]
        DETECTOR(3.5, 8.5, 0) rec[-82] rec[-27]
        DETECTOR(3.5, 9.5, 0) rec[-57] rec[-26]
        DETECTOR(3.5, 10.5, 0) rec[-81] rec[-25]
        DETECTOR(6.5, -0.5, 0) rec[-80] rec[-24]
        DETECTOR(6.5, 0.5, 0) rec[-56] rec[-23]
        DETECTOR(6.5, 1.5, 0) rec[-79] rec[-22]
        DETECTOR(6.5, 2.5, 0) rec[-78] rec[-21]
        DETECTOR(6.5, 3.5, 0) rec[-55] rec[-20]
        DETECTOR(6.5, 4.5, 0) rec[-77] rec[-19]
        DETECTOR(6.5, 5.5, 0) rec[-76] rec[-18]
        DETECTOR(6.5, 6.5, 0) rec[-54] rec[-17]
        DETECTOR(6.5, 7.5, 0) rec[-75] rec[-16]
        DETECTOR(6.5, 8.5, 0) rec[-74] rec[-15]
        DETECTOR(6.5, 9.5, 0) rec[-53] rec[-14]
        DETECTOR(6.5, 10.5, 0) rec[-73] rec[-13]
        DETECTOR(9.5, -0.5, 0) rec[-72] rec[-12]
        DETECTOR(9.5, 0.5, 0) rec[-52] rec[-11]
        DETECTOR(9.5, 1.5, 0) rec[-71] rec[-10]
        DETECTOR(9.5, 2.5, 0) rec[-70] rec[-9]
        DETECTOR(9.5, 3.5, 0) rec[-51] rec[-8]
        DETECTOR(9.5, 4.5, 0) rec[-69] rec[-7]
        DETECTOR(9.5, 5.5, 0) rec[-68] rec[-6]
        DETECTOR(9.5, 6.5, 0) rec[-50] rec[-5]
        DETECTOR(9.5, 7.5, 0) rec[-67] rec[-4]
        DETECTOR(9.5, 8.5, 0) rec[-66] rec[-3]
        DETECTOR(9.5, 9.5, 0) rec[-49] rec[-2]
        DETECTOR(9.5, 10.5, 0) rec[-65] rec[-1]
        MPP X0*X1*X64 X8*X9*X64 Z0*Z8*Z64 Z1*Z9*Z64 X2*X3*X65 X10*X11*X65 Z2*Z10*Z65 Z3*Z11*Z65 X4*X5*X66 X12*X13*X66 Z4*Z12*Z66 Z5*Z13*Z66 X6*X7*X67 X14*X15*X67 Z6*Z14*Z67 Z7*Z15*Z67 X16*X17*X80 X24*X25*X80 Z16*Z24*Z80 Z17*Z25*Z80 X18*X19*X81 X26*X27*X81 Z18*Z26*Z81 Z19*Z27*Z81 X20*X21*X82 X28*X29*X82 Z20*Z28*Z82 Z21*Z29*Z82 X22*X23*X83 X30*X31*X83 Z22*Z30*Z83 Z23*Z31*Z83 X32*X33*X96 X40*X41*X96 Z32*Z40*Z96 Z33*Z41*Z96 X34*X35*X97 X42*X43*X97 Z34*Z42*Z97 Z35*Z43*Z97 X36*X37*X98 X44*X45*X98 Z36*Z44*Z98 Z37*Z45*Z98 X38*X39*X99 X46*X47*X99 Z38*Z46*Z99 Z39*Z47*Z99 X48*X49*X112 X56*X57*X112 Z48*Z56*Z112 Z49*Z57*Z112 X50*X51*X113 X58*X59*X113 Z50*Z58*Z113 Z51*Z59*Z113 X52*X53*X114 X60*X61*X114 Z52*Z60*Z114 Z53*Z61*Z114 X54*X55*X115 X62*X63*X115 Z54*Z62*Z115 Z55*Z63*Z115
        OBSERVABLE_INCLUDE(0) rec[-5024] rec[-64]
        OBSERVABLE_INCLUDE(1) rec[-5022] rec[-62]
        OBSERVABLE_INCLUDE(2) rec[-5020] rec[-60]
        OBSERVABLE_INCLUDE(3) rec[-5018] rec[-58]
        OBSERVABLE_INCLUDE(4) rec[-5016] rec[-56]
        OBSERVABLE_INCLUDE(5) rec[-5014] rec[-54]
        OBSERVABLE_INCLUDE(6) rec[-5012] rec[-52]
        OBSERVABLE_INCLUDE(7) rec[-5010] rec[-50]
        OBSERVABLE_INCLUDE(8) rec[-5008] rec[-48]
        OBSERVABLE_INCLUDE(9) rec[-5006] rec[-46]
        OBSERVABLE_INCLUDE(10) rec[-5004] rec[-44]
        OBSERVABLE_INCLUDE(11) rec[-5002] rec[-42]
        OBSERVABLE_INCLUDE(12) rec[-5000] rec[-40]
        OBSERVABLE_INCLUDE(13) rec[-4998] rec[-38]
        OBSERVABLE_INCLUDE(14) rec[-4996] rec[-36]
        OBSERVABLE_INCLUDE(15) rec[-4994] rec[-34]
        OBSERVABLE_INCLUDE(16) rec[-4992] rec[-32]
        OBSERVABLE_INCLUDE(17) rec[-4990] rec[-30]
        OBSERVABLE_INCLUDE(18) rec[-4988] rec[-28]
        OBSERVABLE_INCLUDE(19) rec[-4986] rec[-26]
        OBSERVABLE_INCLUDE(20) rec[-4984] rec[-24]
        OBSERVABLE_INCLUDE(21) rec[-4982] rec[-22]
        OBSERVABLE_INCLUDE(22) rec[-4980] rec[-20]
        OBSERVABLE_INCLUDE(23) rec[-4978] rec[-18]
        OBSERVABLE_INCLUDE(24) rec[-4976] rec[-16]
        OBSERVABLE_INCLUDE(25) rec[-4974] rec[-14]
        OBSERVABLE_INCLUDE(26) rec[-4972] rec[-12]
        OBSERVABLE_INCLUDE(27) rec[-4970] rec[-10]
        OBSERVABLE_INCLUDE(28) rec[-4968] rec[-8]
        OBSERVABLE_INCLUDE(29) rec[-4966] rec[-6]
        OBSERVABLE_INCLUDE(30) rec[-4964] rec[-4]
        OBSERVABLE_INCLUDE(31) rec[-4962] rec[-2]
        DETECTOR(-1, 0, 0) rec[-5023] rec[-5007] rec[-4991] rec[-4975] rec[-63] rec[-47] rec[-31] rec[-15]
        DETECTOR(-2, 0, 0) rec[-5019] rec[-5003] rec[-4987] rec[-4971] rec[-59] rec[-43] rec[-27] rec[-11]
        DETECTOR(-3, 0, 0) rec[-5015] rec[-4999] rec[-4983] rec[-4967] rec[-55] rec[-39] rec[-23] rec[-7]
        DETECTOR(-4, 0, 0) rec[-5011] rec[-4995] rec[-4979] rec[-4963] rec[-51] rec[-35] rec[-19] rec[-3]
        DETECTOR(-5, 0, 0) rec[-5024] rec[-5020] rec[-5016] rec[-5012] rec[-64] rec[-60] rec[-56] rec[-52]
        DETECTOR(-6, 0, 0) rec[-5008] rec[-5004] rec[-5000] rec[-4996] rec[-48] rec[-44] rec[-40] rec[-36]
        DETECTOR(-7, 0, 0) rec[-4992] rec[-4988] rec[-4984] rec[-4980] rec[-32] rec[-28] rec[-24] rec[-20]
        DETECTOR(-8, 0, 0) rec[-4976] rec[-4972] rec[-4968] rec[-4964] rec[-16] rec[-12] rec[-8] rec[-4]
        DETECTOR(-9, 0, 0) rec[-5021] rec[-5017] rec[-4989] rec[-4985] rec[-61] rec[-57] rec[-29] rec[-25]
        DETECTOR(-10, 0, 0) rec[-5013] rec[-5009] rec[-4981] rec[-4977] rec[-53] rec[-49] rec[-21] rec[-17]
        DETECTOR(-11, 0, 0) rec[-5005] rec[-5001] rec[-4973] rec[-4969] rec[-45] rec[-41] rec[-13] rec[-9]
        DETECTOR(-12, 0, 0) rec[-4997] rec[-4993] rec[-4965] rec[-4961] rec[-37] rec[-33] rec[-5] rec[-1]
        DETECTOR(-13, 0, 0) rec[-5022] rec[-5014] rec[-5006] rec[-4998] rec[-62] rec[-54] rec[-46] rec[-38]
        DETECTOR(-14, 0, 0) rec[-5018] rec[-5010] rec[-5002] rec[-4994] rec[-58] rec[-50] rec[-42] rec[-34]
        DETECTOR(-15, 0, 0) rec[-4990] rec[-4982] rec[-4974] rec[-4966] rec[-30] rec[-22] rec[-14] rec[-6]
        DETECTOR(-16, 0, 0) rec[-4986] rec[-4978] rec[-4970] rec[-4962] rec[-26] rec[-18] rec[-10] rec[-2]
    """)


@pytest.mark.parametrize('num_patches', [16, 64])
def test_squareberg_phenomenological_circuit(num_patches: int):
    c = squareberg_phenomenological_circuit(
        rounds=10,
        noise=gen.NoiseRule(after={'DEPOLARIZE1': 1e-3}, flip_result=1e-3),
        num_patches=num_patches,
    )
    assert c.num_observables == {16: 2, 64: 34}[num_patches] * 2
    assert c.detector_error_model(decompose_errors=True) is not None
    actual_distance = len(c.shortest_graphlike_error())
    assert actual_distance == 4
