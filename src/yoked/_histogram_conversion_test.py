import numpy as np

from yoked._histogram_conversion import histogram_bucket_holds, \
    curve_rescaled_to_target_area, area_under_curve, \
    curve_to_curve_between_midpoints, histogram_cosine_convolve


def test_histogram_bucket_holds():
    xs, ys = histogram_bucket_holds(
        hits={
            3: 20,
            5: 5,
            6: 6,
            16: 1,
        },
        bucket_width=4,
    )
    np.testing.assert_array_equal(xs, [1, 1, 3, 3, 4, 4, 5, 5, 7, 7, 8, 8, 14, 14, 18, 18])
    np.testing.assert_array_equal(ys, [0, 20, 20, 25, 25, 31, 31, 11, 11, 6, 6, 0, 0, 1, 1, 0])


def test_rescaled_area_under_curve():
    xs = [1, 3, 6]
    ys = [1, 1, 3]
    assert area_under_curve(xs, ys) == 1 * 2 + (1 + 3) / 2 * 3 == 8
    xs2, ys2 = curve_rescaled_to_target_area(
        xs=xs,
        ys=ys,
        expected_total=1,
    )
    np.testing.assert_array_equal(xs2, [1, 3, 6])
    np.testing.assert_array_equal(ys2, [0.125, 0.125, 0.375])


def test_curve_to_curve_between_midpoints():
    xs = [1, 3, 3, 10, 10]
    ys = [1, 1, 5, 10, 20]
    xs2, ys2 = curve_to_curve_between_midpoints(
        xs=xs,
        ys=ys,
    )
    np.testing.assert_array_equal(xs2, [1, 2, 3, 6.5, 10, 10])
    np.testing.assert_array_equal(ys2, [1, 1, 3, 7.5, 15, 20])


def test_histogram_cosine_convolve():
    xs, ys = histogram_cosine_convolve(
        hits={1: 5, 5: 1, 6: 2},
        bucket_width=3,
    )
    np.testing.assert_allclose(xs, [-2.0, -1.875, -1.75, -1.625, -1.5, -1.375, -1.25, -1.125, -1.0, -0.875, -0.75, -0.625, -0.5, -0.375, -0.25, -0.125, 0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875, 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875, 4.0, 4.125, 4.25, 4.375, 4.5, 4.625, 4.75, 4.875, 5.0, 5.125, 5.25, 5.375, 5.5, 5.625, 5.75, 5.875, 6.0, 6.125, 6.25, 6.375, 6.5, 6.625, 6.75, 6.875, 7.0, 7.125, 7.25, 7.375, 7.5, 7.625, 7.75, 7.875, 8.0, 8.125, 8.25, 8.375, 8.5, 8.625, 8.75, 8.875], atol=1e-3)
    np.testing.assert_allclose(ys, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1093, 0.4323, 0.9549, 1.6543, 2.5, 3.4549, 4.4774, 5.5226, 6.5451, 7.5, 8.3457, 9.0451, 9.5677, 9.8907, 10, 9.8907, 9.5677, 9.0451, 8.3457, 7.5, 6.5451, 5.5226, 4.4774, 3.4549, 2.5, 1.6543, 0.9549, 0.4323, 0.1093, 0, 0, 0, 0.0219, 0.0865, 0.191, 0.3309, 0.5, 0.691, 0.8955, 1.1045, 1.3527, 1.6729, 2.0511, 2.4708, 2.9135, 3.3601, 3.7909, 4.1872, 4.5316, 4.809, 5.0074, 5.118, 5.1361, 5.0608, 4.8955, 4.6473, 4.3271, 3.9489, 3.5292, 3.0865, 2.6399, 2.2091, 1.7909, 1.382, 1.0, 0.6617, 0.382, 0.1729, 0.0437, 0, 0, 0, 0, 0, 0, 0, 0, 0], atol=1e-3)
