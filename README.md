# LearnCV：机器人视觉与路径规划实验室

这是一套面向机器人感知、定位和规划的渐进式学习仓库。它同时提供：

- 一份从数学、几何、深度学习到 ROS 2 的知识清单；
- 截至 **2026-09-24** 的主流与前沿算法选型，明确区分“论文前沿”和“工程默认”；
- 7 个完全离线、可在 Windows 原生 Python 运行的核心项目；
- 1 个可选的 YOLO26 现代检测项目；
- ROS 2 Jazzy + Gazebo Harmonic + Nav2 的 Docker 镜像和 ROS 2 A* 发布节点；
- 针对当前主机的 WSL2、Docker Desktop 和 ROS 2 安装脚本。

> 重要边界：不存在脱离数据集、实时性、传感器和机器人约束的“统一 SOTA”。本仓库把稳定可部署的工程主线与高算力前沿实验线分开。

## 当前机器与完成状态

已只读检测到：Windows 11、i7-14700HX、16 GB RAM、RTX 4060 Laptop 8 GB、D 盘约 451 GB 可用。

| 交付项 | 状态 |
|---|---|
| 核心 Python 算法和测试 | 已在独立 Python 3.11 环境运行，9/9 测试通过 |
| P01–P07 离线例程 | 已运行，结果位于 `outputs/` |
| P08 YOLO26 例程 | 已创建；首次运行需下载依赖、权重和示例图 |
| ROS 2 A* 节点 | 已创建并完成 Python/XML 静态检查 |
| ROS 2/Nav2 Docker 镜像 | Dockerfile/Compose 已准备；P10 当前为仿真启动骨架 |
| 镜像实际构建 | 尚未执行：本机当前未安装 WSL 发行版和 Docker，安装需要管理员权限及重启 |
| Isaac Sim | 不部署：当前 16 GB RAM/8 GB VRAM 低于完整工作流官方建议的 32 GB/16 GB |

## 先跑起来

在 PowerShell 中：

```powershell
Set-Location D:\LearnCV
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_native.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run_native_examples.ps1
```

不创建新环境也可以用当前 Python 快速验证：

```powershell
python -m unittest discover -s tests -v
python -m examples.p07_perception_to_planning
```

核心项目：

| 项目 | 命令 | 学习目标 |
|---|---|---|
| P01 | `python -m examples.p01_camera_geometry` | 针孔模型、投影、RGB-D 反投影 |
| P02 | `python -m examples.p02_color_detection` | 分割、连通域、检测框 |
| P03 | `python -m examples.p03_astar_grid` | Dijkstra、A*、启发式 |
| P04 | `python -m examples.p04_rrt_star` | 采样规划、碰撞检测、重连 |
| P05 | `python -m examples.p05_dwa_local_planner` | 差速模型、动态窗口、局部避障 |
| P06 | `python -m examples.p06_ekf_localization` | 运动模型、协方差、传感器融合 |
| P07 | `python -m examples.p07_perception_to_planning` | 感知到代价地图再到路径的闭环 |
| P08 | `python -m examples.p08_yolo26_inference` | 现代实时目标检测与权重推理 |

P08 需要额外依赖：

```powershell
conda run -n robotlab python -m pip install -e ".[modern-vision]"
conda run -n robotlab python -m examples.p08_yolo26_inference
```

## ROS 2 与仿真镜像

完成 WSL2 与 Docker Desktop 安装后，在 Ubuntu 24.04/WSL 中从仓库根目录运行：

```bash
docker compose build algorithm-demo
docker compose up algorithm-demo
docker compose --profile sim up nav2-headless
```

第一个服务发布 `/demo_map` 和 `/demo_path`；第二个服务启动 Nav2 官方 TurtleBot3 headless 仿真。Gazebo/RViz GUI 推荐直接运行于 WSLg，而不是从容器转发：

```bash
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

完整安装步骤与当前阻塞条件见 [环境与镜像指南](docs/03_environment_and_images.md)。

## 文档导航

- [知识清单与 16 周路线](docs/01_learning_checklist.md)
- [2026 主流与前沿算法地图](docs/02_algorithm_landscape_2026.md)
- [本机环境、WSL2、ROS 2 和镜像部署](docs/03_environment_and_images.md)
- [每个项目的设计、验收和扩展](docs/04_projects.md)

建议顺序是：

```text
几何与标定 → 识别/分割 → 深度与 3D → 状态估计/SLAM
             ↓
栅格地图 → 全局规划 → 局部控制 → ROS 2/Nav2 闭环
             ↓
开放词汇语义、Foundation SLAM、VLA（最后学习）
```
