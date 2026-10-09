# funtecplot

将 numpy 数组导出为 Tecplot ASCII 数据格式的小工具，把点云/网格计算结果转换成 Tecplot 可以直接读取的 `.dat` 文件，方便后续可视化。

## 安装

```bash
pip install funtecplot
```

## 用法示例

### 点数据（POINT 格式）

```python
import numpy as np
from funtecplot import PointData

# axis_dim=1 表示一维坐标轴，data_dim=3 表示每个点有 3 个分量的数据
PointData(
    data=np.random.rand(30, 3),
    variables=["x", "ux", "uy", "uz"],
    axis_dim=1,
    data_dim=3,
).dump("example.dat")
```

`PointData`（`funtecplot/dump/point.py`）支持 1/2/3 维坐标轴（分别对应 Tecplot ZONE 里的 I / I,J / I,J,K），按坐标顺序把 numpy 数组展开写成 Tecplot 的 `POINT` 格式。

### 三角形网格数据（FEPOINT 格式）

```python
import numpy as np
from funtecplot.dump.triangle import TriangleData

TriangleData(
    variables=["x", "y", "ux", "uy"],
    point=np.random.random((10, 2)),
    data=np.random.random((10, 2)),
    edge=np.array([[0, 1, 3], [1, 2, 4], [2, 0, 9]]),
).dump("mesh.dat")
```

`TriangleData`（`funtecplot/dump/triangle.py`）用于导出有限元三角形网格（`ZONE ... F=FEPOINT, ET=TRIANGLE`）：先写每个点的坐标+数据，再写三角形的顶点索引。`edge` 接受从零开始的整数点索引，导出时会自动转换为 Tecplot FEPOINT 要求的从一开始的节点编号。

`PointData` 和 `TriangleData` 均可从 `funtecplot` 或 `funtecplot.dump` 导入。

两者都继承自 `funtecplot.dump.base.Base`，核心逻辑是拼出 `TITLE` / `VARIABLES` / `ZONE` 头以及逐行的数据体，写入指定文件。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
