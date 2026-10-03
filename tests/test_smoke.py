"""覆盖数组到 Tecplot ASCII 文件的真实导出路径。"""

import numpy as np
import pytest


def test_import_top_level_package():
    import funtecplot  # noqa: F401


def test_import_dump_subpackage_and_point_data():
    import funtecplot.dump  # noqa: F401
    from funtecplot.dump import PointData  # noqa: F401


def test_import_triangle_module():
    from funtecplot.dump.triangle import TriangleData  # noqa: F401


def test_import_base_module():
    from funtecplot.dump.base import Base  # noqa: F401


def _make_dummy():
    from funtecplot.dump.base import Base

    class Dummy(Base):
        def _dump(self):
            return ["line"]

    return Dummy


@pytest.mark.parametrize("variables", ["", [], ["x", ""], ["", "y"], ["  "]])
def test_base_rejects_empty_or_blank_variables(variables):
    Dummy = _make_dummy()

    with pytest.raises(ValueError, match="variables 不能为空"):
        Dummy(variables=variables)


def test_base_dump_round_trips_comma_separated_variables(tmp_path):
    Dummy = _make_dummy()
    out_file = tmp_path / "base_dump.dat"

    Dummy(variables="x, y").dump(str(out_file))

    content = out_file.read_text()
    assert content.splitlines()[0] == 'VARIABLES = "x", "y"'


def test_top_level_reexports_public_api():
    from funtecplot import PointData, TriangleData  # noqa: F401


@pytest.mark.parametrize("kwargs", [{"axis_dim": 0}, {"axis_dim": 4}])
def test_point_data_rejects_invalid_axis_dim(kwargs):
    from funtecplot import PointData

    with pytest.raises(ValueError, match="axis_dim"):
        PointData(np.ones((2,)), variables=["x", "u"], data_dim=1, **kwargs)


def test_point_data_rejects_shape_mismatch():
    from funtecplot import PointData

    with pytest.raises(ValueError, match="最后一维"):
        PointData(
            np.ones((2, 2)),
            variables=["x", "u", "v", "w"],
            axis_dim=1,
            data_dim=3,
        )


def test_triangle_data_rejects_mismatched_points():
    from funtecplot import TriangleData

    with pytest.raises(ValueError, match="点数"):
        TriangleData(
            point=np.ones((2, 2)),
            data=np.ones((1, 1)),
            edge=np.ones((1, 3), dtype=int),
            variables=["x", "y", "u"],
        )


def test_triangle_data_rejects_invalid_edges():
    from funtecplot import TriangleData

    with pytest.raises(ValueError, match="索引"):
        TriangleData(
            point=np.ones((3, 2)),
            data=np.ones((3, 1)),
            edge=np.array([[0, 1, 3]]),
            variables=["x", "y", "u"],
        )


def test_point_data_2d_writes_tecplot_file(tmp_path):
    from funtecplot.dump import PointData

    data = np.array(
        [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
        ]
    )
    out_file = tmp_path / "point_2d.dat"

    PointData(
        data=data,
        variables=["x", "y", "u"],
        axis_dim=2,
        data_dim=1,
        title="smoke",
    ).dump(str(out_file))

    assert out_file.exists()
    content = out_file.read_text()
    lines = content.splitlines()

    assert lines[0] == "TITLE = smoke"
    assert lines[1] == 'VARIABLES = "x", "y", "u"'
    assert lines[2] == "ZONE I=3 J=3 f=point"

    # 3x3 grid -> 9 data rows after the 3 header lines.
    data_lines = lines[3:]
    assert len(data_lines) == 9
    for line in data_lines:
        # i, j, value -> 3 whitespace separated numbers.
        assert len(line.split()) == 3


def test_point_data_1d_writes_tecplot_file(tmp_path):
    from funtecplot.dump import PointData

    data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    out_file = tmp_path / "point_1d.dat"

    PointData(data=data, variables=["x", "u"], axis_dim=1, data_dim=1).dump(
        str(out_file)
    )

    assert out_file.exists()
    lines = out_file.read_text().splitlines()

    assert lines[0] == 'VARIABLES = "x", "u"'
    assert lines[1] == "ZONE I=5 f=point"

    data_lines = lines[2:]
    assert len(data_lines) == 5
    for line in data_lines:
        assert len(line.split()) == 2


def test_triangle_data_writes_fepoint_tecplot_file(tmp_path):
    from funtecplot.dump.triangle import TriangleData

    point = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
        ]
    )
    data = np.array(
        [
            [0.0, 0.0],
            [1.0, 1.0],
            [2.0, 2.0],
            [3.0, 3.0],
        ]
    )
    edge = np.array([[0, 1, 2], [1, 2, 3]])
    out_file = tmp_path / "triangle.dat"

    TriangleData(
        variables=["x", "y", "ux", "uy"],
        point=point,
        data=data,
        edge=edge,
    ).dump(str(out_file))

    assert out_file.exists()
    lines = out_file.read_text().splitlines()

    assert lines[0] == 'VARIABLES = "x", "y", "ux", "uy"'
    assert lines[1] == "ZONE n=4 e=2 f=fepoint et=triangle"

    body = lines[2:]
    # 4 point rows (coords + data) followed by 2 edge (triangle index) rows.
    assert len(body) == 4 + 2

    point_rows, edge_rows = body[:4], body[4:]
    for line in point_rows:
        # x, y, ux, uy -> 4 values per point row.
        assert len(line.split()) == 4
    for line in edge_rows:
        # 3 vertex indices per triangle.
        assert len(line.split()) == 3
        for token in line.split():
            assert token.isdigit()
