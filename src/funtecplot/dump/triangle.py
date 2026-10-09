"""Tecplot FEPOINT 三角形网格导出器。"""

from pathlib import Path
from typing import Sequence

import numpy as np

from .base import Base


class TriangleData(Base):
    """将点坐标、点数据和三角形连接关系导出为 FEPOINT 格式。

    Args:
        point: 二维点坐标数组，每行表示一个点。
        data: 二维点数据数组，行数必须与 ``point`` 相同。
        edge: 三角形连接数组，每行包含 3 个从零开始的整数点索引。
            导出时会转换为 Tecplot 要求的从一开始的节点编号。
        variables: 坐标和点数据的变量名，数量须等于两者列数之和。
        title: 可选的 Tecplot 数据集标题。
    """

    def __init__(
        self,
        point: np.ndarray,
        data: np.ndarray,
        edge: np.ndarray,
        variables: Sequence[str] | str | None = None,
        title: str | None = None,
    ) -> None:
        """初始化三角形网格数据及其导出配置。

        Args:
            point: 二维点坐标数组，每行表示一个点。
            data: 二维点数据数组，行数必须与 ``point`` 相同。
            edge: 三角形连接数组，每行包含 3 个从零开始的整数点索引。
                导出时会转换为 Tecplot 要求的从一开始的节点编号。
            variables: 坐标和点数据的变量名，数量须等于两者列数之和。
            title: 可选的 Tecplot 数据集标题。

        Returns:
            None。

        Raises:
            ValueError: 数组为空、形状不匹配、索引不是整数、索引越界或变量名数量不符时抛出。
        """
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
        if not np.issubdtype(edges.dtype, np.integer):
            raise ValueError("三角形顶点索引必须是整数")
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
        """格式化坐标或数据值。

        Args:
            data: 标量或待格式化的数据数组。

        Returns:
            由空格分隔的浮点数字符串。
        """
        return " ".join(f"{value:6f}" for value in np.asarray(data).reshape(-1))

    def format_int(self, data: np.ndarray) -> str:
        """格式化三角形顶点索引。

        Args:
            data: 待格式化的顶点索引数组。

        Returns:
            由空格分隔的整数字符串。
        """
        return " ".join(str(int(value) + 1) for value in np.asarray(data).reshape(-1))

    def _dump(self) -> list[str]:
        """生成点数据行和三角形连接行。"""
        lines = [
            f"{self.data_format(point)} {self.data_format(value)}"
            for point, value in zip(self.point, self.data)
        ]
        lines.extend(self.format_int(edge) for edge in self.edge)
        return lines


def example() -> None:
    """生成一个最小三角形网格示例文件。

    Returns:
        None。函数会在当前目录写入 ``001.dat``。
    """
    TriangleData(
        variables=["x", "y", "ux", "uy"],
        point=np.random.random((10, 2)),
        data=np.random.random((10, 2)),
        edge=np.array([[0, 1, 3], [1, 2, 4], [2, 0, 9]]),
    ).dump(Path("001.dat"))
