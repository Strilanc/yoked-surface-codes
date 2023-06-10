from gen._surf._closed_curve import ClosedCurve
from gen._surf._patch_transition_outline import PatchTransitionOutline
from gen._surf._path_outline import PathOutline


def test_data_set():
    trans = PatchTransitionOutline(
        observable_deltas={1: PathOutline([(0 + 1j, 2 + 1j)])},
        data_boundary_planes=[ClosedCurve.from_cycle(['X', 0, 2, 2 + 2j, 2j])],
    )
    assert trans.data_set == {0, 1, 2, 1j, 1j + 1, 1j + 2, 2j, 2j + 1, 2j + 2}
