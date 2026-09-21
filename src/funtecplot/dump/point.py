"""Tecplot POINT 格式导出器。"""

from pathlib import Path
from typing import Sequence

import numpy as np

from .base import Base


class PointData(Base):
    """将规则网格数据导出为 Tecplot POINT 格式。"""

    def __init__(
        self,
        data: np.ndarray,
        axis_dim: int = 2,
        data_dim: int = 3,
        variables: Sequence[str] | str | None = None,
        title: str | None = None,
    ) -> None:
        """初始化数据、坐标维度、数据维度和变量名。"""
        if axis_dim not in (1, 2, 3):
            raise ValueError("axis_dim 必须是 1、2 或 3")
        if data_dim < 1:
            raise ValueError("data_dim 必须大于 0")
        values = np.asarray(data)
        if values.size == 0 or values.ndim not in (axis_dim, axis_dim + 1):
            raise ValueError("data 的维度或内容为空")
        if values.ndim == axis_dim + 1 and values.shape[-1] != data_dim:
            raise ValueError("data 最后一维与 data_dim 不一致")
        if values.ndim == axis_dim and data_dim != 1:
            raise ValueError("多分量数据必须包含最后一维")
        names = variables.split(",") if isinstance(variables, str) else variables
        if names is None or len(names) != axis_dim + data_dim:
            raise ValueError("variables 数量必须等于 axis_dim + data_dim")
        super().__init__(names, title)
        self.data = values
        self.axis_dim = axis_dim
        self.data_dim = data_dim
        self.axis_shape = values.shape[:axis_dim]
        if any(size == 0 for size in self.axis_shape):
            raise ValueError("坐标轴长度不能为空")
        if axis_dim >= 1:
            self.zone["I"] = self.axis_shape[-1]
        if axis_dim >= 2:
            self.zone["J"] = self.axis_shape[-2]
        if axis_dim >= 3:
            self.zone["K"] = self.axis_shape[-3]
        self.zone["f"] = "point"

    def data_format(self, data: np.ndarray | float) -> str:
        """格式化一行数据值。"""
        values = np.asarray(data).reshape(-1)
        return " ".join(f"{value:6f}" for value in values[: self.data_dim])

    def _dump(self) -> list[str]:
        """生成 POINT 数据行。"""
        lines: list[str] = []
        for index in np.ndindex(self.axis_shape):
            coordinates = " ".join(f"{part + 1:6f}" for part in index)
            lines.append(f"{coordinates} {self.data_format(self.data[index])}")
        return lines


def example() -> None:
    """生成一个最小 POINT 示例文件。"""
    PointData(
        data=np.random.rand(30), variables=["x", "u"], axis_dim=1, data_dim=1
    ).dump(Path("example_1_1_1.txt"))
