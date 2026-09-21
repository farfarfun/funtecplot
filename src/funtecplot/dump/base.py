"""Tecplot 导出器的共享基类。"""

from pathlib import Path
from typing import Sequence


class Base:
    """生成 Tecplot 文件头并委托子类生成数据体。"""

    def __init__(self, variables: Sequence[str] | str | None = None, title: str | None = None) -> None:
        """初始化变量名和可选标题。"""
        if variables is None:
            raise ValueError("variables 不能为空")
        self.variables = variables
        self.title = title
        self.zone: dict[str, int | str] = {}
        self.data: object = []

    def dump(self, filepath: str | Path) -> None:
        """将当前对象导出到指定文件。"""
        variables = self.variables
        if isinstance(variables, str):
            variables = variables.strip().split(",")
        names = ", ".join(f'"{var}"' for var in variables)
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
