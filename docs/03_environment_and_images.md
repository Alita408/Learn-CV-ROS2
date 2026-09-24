# 本机环境、WSL2、ROS 2 与镜像部署

## 1. 已检测状态

| 项目 | 当前值 |
|---|---|
| OS | Windows 11 家庭中文版，build 26200 |
| CPU | Intel i7-14700HX，20C/28T |
| RAM | 15.8 GB |
| GPU | RTX 4060 Laptop，8 GB，驱动 566.24 |
| 磁盘 | C 盘约 60 GB 可用；D 盘约 451 GB 可用 |
| Python | Anaconda 3.9；另有 Python 3.13 |
| 现有 DL 环境 | PyTorch 1.12 + CUDA 11.3，过旧，不复用 |
| WSL | `wsl.exe` 存在，但尚无发行版/组件未就绪 |
| Docker | 未安装 |

因此当前已在 Windows 原生 Python 上完成 P01–P07 验证；系统级安装没有静默执行，因为 WSL 启用可能要求管理员权限和重启。

## 2. 推荐结构

```text
Windows 11
├─ Conda robotlab：P01–P08、数据处理、模型导出
└─ WSL2 Ubuntu 24.04（VHD 放 D:\WSL）
   ├─ 原生：ROS 2 Jazzy + Gazebo Harmonic + RViz（WSLg GUI）
   └─ Docker：隔离依赖、headless 测试、Nav2、ROS 2 例程
```

当前 Dockerfile 提供可重复执行的构建入口，但基础镜像标签与 apt 包仍会随上游更新。正式基准应记录构建后的镜像 digest，并为关键依赖建立 lockfile 或快照仓库。

ROS 2 Jazzy 的 Tier-1 Ubuntu 是 24.04；Gazebo 官方推荐 Jazzy + Harmonic。2026 年虽已有 ROS 2 Lyrical LTS，但它基于 Ubuntu 26.04，第三方机器人包的教学成熟度仍不如 Jazzy。参考：[ROS 2 Jazzy Ubuntu 安装](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)、[Gazebo/ROS 配对](https://gazebosim.org/docs/latest/ros_installation/)。

## 3. A 层：Windows 原生环境

已提供幂等脚本：

```powershell
Set-Location D:\LearnCV
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_native.ps1
```

它会创建 `robotlab`（Python 3.11）、安装本项目并运行测试。验证：

```powershell
conda run -n robotlab python -m unittest discover -s tests -v
conda run -n robotlab python -m examples.p07_perception_to_planning
```

不要把 ROS 2 Jazzy 的 Python 包装进这个 Conda 环境。ROS 2 官方提醒，预编译 ROS 二进制要求匹配系统 Python，Conda 往往不兼容。

## 4. B 层：安装 WSL2 与 Ubuntu 24.04

这一步需要管理员 PowerShell并可能重启：

```powershell
Set-Location D:\LearnCV
powershell -ExecutionPolicy Bypass -File .\scripts\install_wsl_prerequisites.ps1
```

重启后：

```powershell
wsl --update
wsl --set-default-version 2
wsl --install -d Ubuntu-24.04 --location D:\WSL\Ubuntu-24.04
wsl -l -v
```

微软说明 `wsl --install` 会启用 WSL/Virtual Machine Platform、安装内核，并且可能要求重启；WSL2 支持 Linux GUI 和 vGPU。[WSL 安装](https://learn.microsoft.com/windows/wsl/setup/environment)、[WSLg GUI](https://learn.microsoft.com/windows/wsl/tutorials/gui-apps)。

推荐 `%UserProfile%\.wslconfig`：

```ini
[wsl2]
memory=10GB
processors=12
swap=8GB
swapfile=D:\\WSL\\wsl-swap.vhdx

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

修改后运行 `wsl --shutdown`。16 GB 主机不要长期把全部内存分给 WSL。

## 5. C 层：在 WSL 安装 ROS 2 Jazzy

进入 Ubuntu 后，从挂载仓库执行：

```bash
cd /mnt/d/LearnCV
bash scripts/setup_ros2_jazzy.sh
```

脚本使用 ROS 官方 `ros-apt-source` 安装方式，并安装 ROS desktop、Gazebo bridge、Nav2、SLAM Toolbox、MoveIt 2、ros2_control 和视觉消息。默认固定 `ros-apt-source` 1.3.0；需要升级时可在运行前设置 `ROS_APT_SOURCE_VERSION`。

验证：

```bash
source /opt/ros/jazzy/setup.bash
ros2 doctor --report
ros2 run demo_nodes_cpp talker
```

另一个终端：

```bash
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_py listener
```

GUI/GPU：

```bash
nvidia-smi
echo "$DISPLAY $WAYLAND_DISPLAY"
glxinfo -B
gz sim -v 4 shapes.sdf
```

`glxinfo -B` 不应显示 `llvmpipe`。

### 工作区位置

GUI 可以从 `/mnt/d/LearnCV` 启动，但大型 `colcon` 构建建议把工作副本放在 WSL ext4，例如 `~/LearnCV`。微软明确说明 Linux 命令处理 Linux 文件时，放在 WSL 文件系统更快。WSL 虚拟磁盘本身仍可安装在 D 盘。

## 6. D 层：Docker Desktop 和镜像

安装脚本会通过 winget 请求 Docker Desktop：

```powershell
powershell -ExecutionPolicy Bypass -File D:\LearnCV\scripts\install_docker_desktop.ps1
```

随后在 Docker Desktop 中：

1. 启用 WSL2 backend。
2. 启用 Ubuntu-24.04 integration。
3. 把 Docker disk image location 移到 D 盘。
4. 验证 `docker version` 和 `docker compose version`。

构建与运行：

```bash
cd /mnt/d/LearnCV
docker compose build algorithm-demo
docker compose up algorithm-demo
```

查看 ROS 2 话题：

```bash
docker compose exec algorithm-demo ros2 topic list
docker compose exec algorithm-demo ros2 topic echo /demo_path --once
```

启动 Nav2 官方 TurtleBot3 headless 仿真：

```bash
docker compose --profile sim up nav2-headless
```

镜像基于 Docker 官方 `ros:jazzy-ros-base-noble`，并添加 Nav2、Gazebo bridge、SLAM Toolbox、RViz 和本仓库 ROS 包。[官方 ROS 镜像标签](https://hub.docker.com/_/ros/tags?name=jazzy)。

### 国内 ROS APT 镜像

ROS 官方文档列出 TUNA、USTC、Aliyun 等镜像。构建时可以显式指定：

```bash
export ROS_APT_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/
docker compose build algorithm-demo
```

不要同时修改 Ubuntu、PyPI、Conda 和 ROS 所有源；遇到问题时很难定位。先只切 ROS APT 源。

### 为什么 GUI 不放进默认 Compose

容器内同时转发 Wayland/X11、PulseAudio、OGRE2、GPU 和 DDS 会显著增加故障面。默认镜像用于 headless 和复现；Gazebo/RViz GUI 直接在 WSLg 启动：

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

Nav2 官方 launch 同时提供 `headless` 和 `use_rviz` 参数。

## 7. 保存本地离线镜像

在 WSL 安装 `zstd` 后：

```bash
sudo apt install zstd
bash scripts/export_robotics_image.sh
```

默认输出：

```text
D:\RobotImages\robotics-jazzy-20260924.tar.zst
D:\RobotImages\robotics-jazzy-20260924.tar.zst.sha256
```

恢复：

```bash
sha256sum -c /mnt/d/RobotImages/robotics-jazzy-20260924.tar.zst.sha256
zstd -dc /mnt/d/RobotImages/robotics-jazzy-20260924.tar.zst | docker load
```

单机学习无需先维护私有 registry。模型权重放只读 volume/缓存，记录 URL、版本、SHA-256 和许可，不重复烘焙到每个镜像。

## 8. 镜像拆分原则

长期建议拆分，而不是一个全家桶：

| 镜像 | 内容 |
|---|---|
| `robotics-jazzy` | ROS 2、Nav2、Gazebo headless、MoveIt/控制 |
| `vision-core` | PyTorch、YOLO/D-FINE、ByteTrack、ONNX Runtime |
| `depth-pose` | DA3/Fast-FoundationStereo/FoundationPose |
| `slam-classic` | ORB-SLAM3、Pangolin、evo |
| `slam-foundation` | DPVO 或 MASt3R/VGGT，分别锁版本 |
| `vla` | LeRobot/SmolVLA；π0.5/GR00T 再独立 |

这些项目对 Python、PyTorch、CUDA 和许可证要求冲突，强行合并只会制造不可复现环境。

## 9. Isaac Sim 判定

当前不部署完整 Isaac Sim/Isaac Lab。官方最新安装指南建议至少 32 GB RAM 和 16 GB GPU VRAM；当前为 16 GB/8 GB，且驱动也低于最新验证线。[Isaac Lab 系统要求](https://isaac-sim.github.io/IsaacLab/develop/source/setup/installation/index.html)。

可替代方案：

- 移动机器人和视觉导航：Gazebo Harmonic。
- 更轻量 GUI：Webots。
- 强化学习基础：MuJoCo 或 Isaac Lab 的 kit-less Newton 路径。
- 硬件升级到至少 32 GB RAM、16 GB VRAM 后再评估 Windows 原生 Isaac Sim。

## 10. 常见坑

- WSL 内不要安装 NVIDIA Linux 内核驱动；Windows 驱动通过 WSL 映射。`nvidia-smi` 的 CUDA 版本是驱动能力上限，不代表已装 Toolkit。
- Jazzy 用现代 `gz sim`/`ros_gz`，不要混入 Gazebo Classic `gazebo11`。
- 不要在一个 shell 同时 source Humble 和 Jazzy。
- ROS 2 用系统 Python；只支持 Python 3.10 的视觉仓库放独立容器，通过消息连接。
- 16 GB RAM 下源码编译 MoveIt 时使用 `colcon build --parallel-workers 2`。
- 多容器 ROS 2 易受 DDS multicast、NAT 和防火墙影响；入门阶段让仿真和 Nav2 处在同一容器。
- 不要盲目 `docker system prune -a`；先列出镜像、volume 和缓存，模型缓存可能难以恢复。
