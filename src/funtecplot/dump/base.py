"""Tecplot 导出器的共享基类。"""

from pathlib import Path
from typing import Sequence


class Base:
    """生成 Tecplot 文件头并委托子类生成数据体。

    Args:
        variables: Tecplot 变量名序列，或以逗号分隔的变量名字符串，不能为空。
        title: 可选的 Tecplot 数据集标题。
    """

    def __init__(self, variables: Sequence[str] | str | None = None, title: str | None = None) -> None:
        """初始化变量名和可选标题。

        Args:
            variables: Tecplot 变量名序列，或以逗号分隔的变量名字符串，不能为空。
            title: 可选的 Tecplot 数据集标题。

        Returns:
            None。

        Raises:
            ValueError: ``variables`` 为 ``None``、空字符串、空序列，或其中包含
                空白变量名时抛出。
        """
        if variables is None:
            raise ValueError("variables 不能为空")
        names = variables.split(",") if isinstance(variables, str) else list(variables)
        names = [str(name).strip() for name in names]
        if not names or any(name == "" for name in names):
            raise ValueError("variables 不能为空")
        self.variables = names
        self.title = title
        self.zone: dict[str, int | str] = {}
        self.data: object = []

    def dump(self, filepath: str | Path) -> None:
        """将当前对象导出到指定文件。

        Args:
            filepath: 输出文件路径；文件已存在时会被覆盖。

        Returns:
            None。方法会在指定路径写入 Tecplot ASCII 文件。
        """
        names = ", ".join(f'"{var}"' for var in self.variables)
        with open(filepath, "w") as file:
            if self.title:
                file.write(f"TITLE = {self.title}\n")
            file.write(f"VARIABLES = {names}\n")
            zone = " ".join(f"{key}={value}" for key, value in self.zone.items())
            file.write(f"ZONE {zone}\n")
            for line in self._dump():
                file.write(f"{line}\n")

    def _dump(self) -> list[str]:
        """返回待写入的数据行；由具体导出器实现。"""
        raise NotImplementedError
