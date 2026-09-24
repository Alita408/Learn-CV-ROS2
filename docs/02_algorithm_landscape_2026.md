# 2026 主流与前沿算法地图

资料快照：**2026-09-24**。这里的“前沿/SOTA”只表示某一论文任务、数据集或速度—精度前沿上的强候选，不表示在你的机器人上必然最好。落地前必须用自己的传感器、场景、延迟预算和安全指标重新基准。

## 视觉感知

| 任务 | 工程主线 | 前沿候选 | 当前主机判断 | 关键限制 |
|---|---|---|---|---|
| 相机几何/6D 基线 | OpenCV 标定、PnP-RANSAC、AprilTag | — | CPU 足够 | 先解决时间同步、内外参和尺度 |
| 闭集实时检测 | [YOLO26 n/s](https://docs.ultralytics.com/models/yolo26)、[D-FINE N/S](https://github.com/Peterande/D-FINE) | RF-DETR | 预计可推理；微调需实测 | YOLO 为 AGPL/商业双许可；需要领域数据 |
| DETR 检测 | [RT-DETRv2](https://github.com/lyuwenyu/RT-DETR)、D-FINE | RF-DETR | 可跑小/中模型 | 训练/导出生态需逐项验证 |
| 开放词汇检测 | [YOLO-World](https://github.com/AILab-CVC/YOLO-World)、YOLOE-26 | [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO)、SAM 3 detector | 小模型可实验，大模型慢 | 文本歧义和长尾误报，不用于毫秒级急停 |
| 实时语义分割 | PIDNet-S、SegFormer-B0/B1 | Mask2Former | 适合 8 GB | 闭集，需本场景标注和边界评测 |
| 提示式分割/视频跟踪 | SAM 2.1 tiny/small | [SAM 3.1](https://github.com/facebookresearch/sam3) | SAM 3 不建议本机主线 | SAM 3 为 848M，要求 Python 3.12、PyTorch 2.7+、CUDA 12.6+，权重需授权访问 |
| 多目标跟踪 | [ByteTrack](https://github.com/FoundationVision/ByteTrack)、[BoT-SORT](https://github.com/NirAharon/BoT-SORT) | detector + Re-ID/运动补偿 | 适合 | 上限受 detector 支配，长遮挡会换 ID |
| 任意点跟踪 | [CoTracker3](https://github.com/facebookresearch/co-tracker) | TAPNext++ | 8 GB 可做短序列 | 它跟踪像素点，不等于物体身份跟踪 |
| 单目/多视图深度 | [Depth Anything 3 Small/Base](https://github.com/ByteDance-Seed/Depth-Anything-3) | DA3 Large/Giant/Nested | Small/Base 可实验 | relative 与 metric 必须区分；模型权重许可不同 |
| 双目深度 | OpenCV SGBM | [Fast-FoundationStereo](https://github.com/NVlabs/Fast-FoundationStereo) | 适合 | 双目标定、同步、纹理和最大视差决定上限 |
| 新物体 6D 位姿 | PnP + CAD/marker | [FoundationPose](https://github.com/NVlabs/FoundationPose) | 可推理，但建议独立镜像 | 需要可靠 mask、尺度、内参，RGB-D 更稳 |
| 关键点 | RTMPose/MMPose、YOLO26-pose | RF-DETR keypoint | 适合 | 人体关键点和刚体 6D pose 是不同任务 |

P08 只固定 Ultralytics 版本，没有替你锁定 PyTorch/CUDA wheel；先运行推理并记录显存峰值，再决定 8 GB 显存下的 batch、图像尺寸与微调策略。

### 深度选择的硬规则

- `relative depth` 只能表达远近关系，不能直接当作米制障碍距离。
- `metric monocular depth` 仍需用你的相机、视场和场景标定误差。
- 双目/RGB-D 能提供几何尺度，安全 costmap 优先使用真实深度并做置信度门控。
- DA3 官方模型卡显示 Small/Base 为 Apache-2.0；Large/Giant/Nested 多为非商用许可，部署前逐权重复核。

## 视觉里程计与 SLAM

| 层级 | 算法 | 何时选 | 限制 |
|---|---|---|---|
| 必学经典 | [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) | 学完整前端、回环、BA；CPU 实时基线 | 弱纹理、强动态、曝光变化；GPLv3 |
| ROS 2 工程 2D | SLAM Toolbox | 激光/深度生成 2D 图并接 Nav2 | 不等于纯视觉 SLAM |
| 学习式稀疏 | [DPVO/DPV-SLAM](https://github.com/princeton-vl/DPVO) | 视频 VO 和学习式前端对照 | CUDA 扩展和版本兼容成本 |
| 稠密前沿 | [MASt3R-SLAM](https://github.com/rmurai0610/MASt3R-SLAM) | 免/弱标定、稠密重建研究 | 模型大；官方还为 WSL 单设分支；桌面高端 GPU 更现实 |
| feed-forward 3D | [VGGT](https://github.com/facebookresearch/vggt)、VGGT-SLAM | 相机 pose、深度、点图和 3D 重建研究 | 不是嵌入式成熟 SLAM 的直接替代 |

推荐顺序：ORB-SLAM3 → DPVO → MASt3R-SLAM/VGGT-SLAM。所有算法统一输出 TUM 轨迹，用 `evo` 比较 ATE/RPE、丢失次数、Hz、显存和内存。

## 路径规划与控制

| 场景 | 首选 | 原因 | 注意事项 |
|---|---|---|---|
| 静态二维、圆形底盘 | A*、NavFn、Smac 2D | 成熟、稳定、易调试 | 不保证车辆可执行性 |
| 任意角栅格 | Theta* | 比 8 邻域路径自然 | 不含动力学约束 |
| 均匀代价大栅格 | JPS | 减少搜索节点 | 不适合任意代价图 |
| 地图局部变化 | D* Lite、AD* | 复用前次搜索 | 动态障碍轨迹已知时研究 SIPP |
| 动态时空规划 | SIPP | 安全时间区间压缩状态 | 依赖预测可靠性 |
| Ackermann | Hybrid A*、State Lattice | 显式处理曲率、倒车和 footprint | Lattice 需合适运动原语 |
| 机械臂快速可行解 | RRTConnect | MoveIt/OMPL 中成熟且快 | 不以路径质量为目标 |
| 重复静态查询 | PRM*/LazyPRM* | 路网可复用 | 建图有前期开销 |
| 渐近最优 | Informed RRT*、BIT* | 质量随时间改善 | 必须在自己的场景基准 |
| 研究型最优采样 | ABIT*、AIT*、EIT* | [OMPL](https://ompl.kavrakilab.org/planners.html) 已实现 | 没有跨所有问题的统一冠军 |
| 含动力学约束 | SST、KPIECE、control-RRT | 直接在控制空间规划 | 模型和传播器决定结果 |
| 机械臂平滑 | OMPL → CHOMP/STOMP | 先找可行解，再局部优化 | 局部最优和初值敏感 |
| 低算力路径跟踪 | Regulated Pure Pursuit | 简单、稳定、快速 | 不是完整动态障碍规划器 |
| 复杂局部避障 | [Nav2 MPPI](https://github.com/ros-navigation/navigation2/tree/main/nav2_mppi_controller) | 预测式、支持多运动模型和 critic | 调参和算力要求高于 RPP/DWB |
| 多机器人即时避碰 | ORCA | 分布式、速度空间高效 | 可能死锁，无全局可达保证 |
| MAPF 最优 | CBS/ICBS/CBSH2-RTC | 可证明最优 | 最坏情况指数增长 |
| MAPF 有界次优 | EECBS + SIPPS | 可控速度—质量折中 | 拥堵时仍可能昂贵 |
| 大规模 MAPF | MAPF-LNS2、PIBT、LaCAM | 扩展性优先 | 通常放弃严格全局最优 |

理论边界：RRT/PRM 是概率完备；RRT*/PRM* 才有渐近最优性。CHOMP/STOMP/TrajOpt 是局部优化。MPPI 是采样式随机预测控制，不等同于确定性 QP-MPC。

## Nav2 与 MoveIt 2 的默认组合

### 移动机器人

- 差速室内：Smac 2D 或 Theta* + Regulated Pure Pursuit。
- 动态/拥挤：Smac 2D/Hybrid + MPPI + Collision Monitor。
- Ackermann：Smac Hybrid-A* 或 State Lattice + MPPI。
- 固定道路/仓库：Jazzy 使用 waypoint/行为树与自由空间 planner；Route Server 是 Kilted 及之后版本的选项。
- 非圆形底盘/窄通道：完整 footprint + Hybrid/Lattice。

官方入口：[Nav2 Jazzy 文档](https://docs.nav2.org/configuration/index.html)、[Smac Planner](https://docs.nav2.org/configuration/packages/configuring-smac-planner.html)、[MPPI](https://docs.nav2.org/configuration/packages/configuring-mppic.html)。

### 机械臂

- 默认首解：RRTConnect。
- 多次查询：PRM/LazyPRM。
- 给足时间追求质量：Informed RRT*、BIT*、AIT*/EIT*。
- 平滑：OMPL 生成种子，再用 CHOMP/STOMP。
- 工业 PTP/LIN/CIRC：Pilz。
- 时间参数化：TOTG 后用 Ruckig 做 jerk-limited smoothing。

MoveIt 通过插件和规划流水线组合 OMPL、Pilz、CHOMP、STOMP；官方也支持并行跑多条规划流水线再选解：[MoveIt Motion Planning](https://moveit.picknik.ai/main/doc/concepts/motion_planning.html)、[Python 多流水线示例](https://moveit.picknik.ai/main/doc/examples/motion_planning_python_api/motion_planning_python_api_tutorial.html)。

## VLA 与学习型导航

| 方向 | 可落地起点 | 前沿 | 当前主机判断 |
|---|---|---|---|
| 操作策略 | ACT/Diffusion Policy | [SmolVLA](https://github.com/huggingface/lerobot) | 8 GB 更适合 ACT；SmolVLA 推理/小批量实验，训练需谨慎 |
| 大型 VLA | — | [OpenPI π0.5](https://github.com/Physical-Intelligence/openpi)、[GR00T N1.7](https://github.com/NVIDIA/Isaac-GR00T) | 不适合本机主线；OpenPI 官方推理要求大于 8 GB |
| 视觉导航 | ViNT/NoMaD、VLFM | NavDP、NaVILA、NavFoM | 先在 Habitat/独立镜像实验 |

VLA 只作为高层语义/子目标或实验策略；局部碰撞监控、急停、速度和关节限制保持独立。

## 本机优先级

1. 立即做：OpenCV 几何、YOLO26n/D-FINE-N、PIDNet/SegFormer、小型跟踪、SGBM、ORB-SLAM3、Nav2、MoveIt 2。
2. 独立环境后做：DA3 Small/Base、DPVO、FoundationPose、SmolVLA 推理。
3. 暂缓：SAM 3.1、MASt3R-SLAM 大规模实验、π0.5、GR00T、完整 Isaac Sim。

“能加载模型”不是完成。每个候选都要在目标输入分辨率、批量 1、你的相机数据上记录准确率、p50/p95 延迟、峰值显存和失败样本。
