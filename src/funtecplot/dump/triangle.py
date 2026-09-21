"""Tecplot FEPOINT 三角形网格导出器。"""

from pathlib import Path
from typing import Sequence

import numpy as np

from .base import Base


class TriangleData(Base):
    """将点坐标、点数据和三角形连接关系导出为 FEPOINT 格式。"""

    def __init__(
        self,
        point: np.ndarray,
        data: np.ndarray,
        edge: np.ndarray,
        variables: Sequence[str] | str | None = None,
        title: str | None = None,
    ) -> None:
        """初始化网格点、点数据、三角形连接关系和变量名。"""
        points = np.asarray(point)
        values = np.asarray(data)
        edges = np.asarray(edge)
        if points.ndim != 2 or values.ndim != 2 or edges.ndim != 2:
            raise ValueError("point、data、edge 必须是二维数组")
        if points.size == 0 or values.size == 0 or edges.size == 0:
            raise ValueError("网格数据不能为空")
        if points.shape[0] != values.shape[0]:
            raise ValueError("point 和 data 的点数必须一致")
        if edges.shape[1] != 3:
            raise ValueError("每个三角形必须包含 3 个顶点")
        if np.any(edges < 0) or np.any(edges >= points.shape[0]):
            raise ValueError("三角形顶点索引超出点数据范围")
        names = variables.split(",") if isinstance(variables, str) else variables
        if names is None or len(names) != points.shape[1] + values.shape[1]:
            raise ValueError("variables 数量必须等于坐标列与数据列之和")
        super().__init__(names, title)
        self.point = points
        self.data = values
        self.edge = edges
        self.zone["n"] = points.shape[0]
        self.zone["e"] = edges.shape[0]
        self.zone["f"] = "fepoint"
        self.zone["et"] = "triangle"

    def data_format(self, data: np.ndarray | float) -> str:
        """格式化坐标或数据值。"""
        return " ".join(f"{value:6f}" for value in np.asarray(data).reshape(-1))

    def format_int(self, data: np.ndarray) -> str:
        """格式化三角形顶点索引。"""
        return " ".join(str(int(value)) for value in np.asarray(data).reshape(-1))

    def _dump(self) -> list[str]:
        """生成点数据行和三角形连接行。"""
        lines = [
            f"{self.data_format(point)} {self.data_format(value)}"
            for point, value in zip(self.point, self.data)
        ]
        lines.extend(self.format_int(edge) for edge in self.edge)
        return lines


def example() -> None:
    """生成一个最小三角形网格示例文件。"""
    TriangleData(
        variables=["x", "y", "ux", "uy"],
        point=np.random.random((10, 2)),
        data=np.random.random((10, 2)),
        edge=np.array([[0, 1, 3], [1, 2, 4], [2, 0, 9]]),
    ).dump(Path("001.dat"))
