# 知识清单与 16 周学习路线

这份路线按每周 8–12 小时设计。第一轮目标不是“看完所有论文”，而是能解释数据流、写出基线、量化误差并在仿真里闭环运行。

## 1. 数学与机器人几何

- [ ] 向量、矩阵、坐标基、特征值、SVD、伪逆、最小二乘。
- [ ] 概率、条件概率、贝叶斯估计、高斯分布、协方差、最大似然。
- [ ] 梯度、Jacobian、Hessian；梯度下降、Gauss–Newton、Levenberg–Marquardt。
- [ ] 鲁棒核、RANSAC、外点与置信区间。
- [ ] 2D/3D 刚体变换、齐次坐标、SO(2)/SO(3)、SE(2)/SE(3)。
- [ ] 欧拉角、四元数、李群与李代数的基本用途。
- [ ] 差速、全向、Ackermann 运动学；机械臂正逆运动学和 Jacobian。
- [ ] 能独立画出 `map → odom → base_link → camera` 坐标树并解释每条边。

完成标准：P01 投影/反投影测试通过；能解释像素、相机、机器人和地图坐标的单位与轴方向。

## 2. 相机与传统视觉

- [ ] 针孔模型、内参/外参、径向与切向畸变。
- [ ] 相机标定、重投影误差、双目校正和同步。
- [ ] 眼在手上/眼在手外的手眼标定，理解 `AX = XB` 与时间同步误差。
- [ ] 单应矩阵、基础矩阵、本质矩阵、极线几何、三角化。
- [ ] 双目关系 `Z = fB / d`，理解视差为零和远距离噪声。
- [ ] Harris/SIFT/ORB、描述子匹配、KLT/Lucas–Kanade 光流。
- [ ] PnP、ICP、Bundle Adjustment、Pose Graph。
- [ ] 图像滤波、形态学、阈值、连通域和轮廓。

完成标准：P02 能消除小噪声并输出正确框；对自己的相机能得到合理标定与 PnP 结果。

## 3. 深度学习视觉

- [ ] CNN、残差连接、FPN、ViT、注意力、Transformer。
- [ ] 分类、目标检测、语义/实例/全景分割的输出差异。
- [ ] Anchor 与 anchor-free；DETR query 和 Hungarian matching。
- [ ] BCE、Focal、Dice、IoU/GIoU 等常见损失。
- [ ] 数据划分、增强、类别不均衡、域偏移、过拟合、置信度校准。
- [ ] PyTorch Dataset/DataLoader、AMP、checkpoint、冻结与微调。
- [ ] ONNX、TensorRT、OpenVINO 的作用；预处理必须与训练一致。
- [ ] 区分 relative depth、metric depth、stereo depth，不把伪尺度深度直接送进安全代价地图。

评价指标：检测用 AP/mAP；分割用 mIoU/Dice/PQ；跟踪用 HOTA/IDF1；深度用 AbsRel/RMSE/δ1；部署同时报告 p50/p95 延迟和显存。

## 4. 状态估计、里程计与 SLAM

- [ ] 马尔可夫假设、Bayes filter、Kalman Filter、EKF/UKF、粒子滤波。
- [ ] 编码器里程计、IMU bias、时间同步、外参和噪声模型。
- [ ] VO/SLAM 前端：特征、匹配、光流、直接法和关键帧。
- [ ] 后端：局部 BA、回环检测、位姿图优化、边缘化。
- [ ] 单目尺度不可观问题；视觉惯性初始化。
- [ ] ATE、RPE、跟踪丢失率、运行频率和地图内存。
- [ ] 经典 ORB-SLAM3 与学习式 DPVO/MASt3R-SLAM 的假设和工程差异。

完成标准：P06 的 EKF 比纯里程计误差低；随后在 TUM-RGBD/EuRoC 上用 `evo` 评测至少两种 SLAM。

## 5. 地图、规划与控制

- [ ] Occupancy Grid、costmap、体素地图、ESDF/SDF。
- [ ] Configuration Space、Minkowski sum、机器人 footprint 与障碍膨胀。
- [ ] BFS、Dijkstra、A*、Weighted A*、Theta*、JPS。
- [ ] D* Lite、AD*、ARA*、SIPP 及何时复用前次搜索。
- [ ] Hybrid A*、State Lattice、运动原语和非完整约束。
- [ ] PRM、RRT/RRTConnect、RRT*/PRM*、Informed RRT*、BIT*/AIT*/EIT*。
- [ ] CHOMP、STOMP、TrajOpt；初值、局部极小和轨迹平滑。
- [ ] Pure Pursuit、DWA/DWB、LQR/iLQR、NMPC、MPPI。
- [ ] PID、离散采样周期、稳定性与可控性、执行器饱和及 anti-windup。
- [ ] 全局规划、局部控制、碰撞监控各自负责什么。
- [ ] 多机器人 CBS/EECBS、PIBT/LaCAM、ORCA 的适用边界。

完成标准：P03 中 A* 与 Dijkstra 的最优代价相同且扩展更少；P04 生成无碰撞路径；P05 闭环抵达目标。

## 6. ROS 2 与软件工程

- [ ] Linux/WSL2、Git、Python、现代 C++、CMake、Docker/Compose。
- [ ] ROS 2 node/topic/service/action、参数、launch、Lifecycle、QoS。
- [ ] tf2、URDF/SRDF、rosbag2、RViz、Gazebo。
- [ ] `Image`、`CameraInfo`、`PointCloud2`、`OccupancyGrid`、`Path`。
- [ ] `image_transport`、`cv_bridge`、消息时间戳与传感器同步。
- [ ] Nav2 的 Behavior Tree、Planner、Controller、Smoother、Costmap 和 Collision Monitor。
- [ ] MoveIt 2 的 Planning Scene、OMPL、规划适配器和时间参数化。
- [ ] 单元测试、固定随机种子、headless smoke test、基准和失败案例回放。

完成标准：容器中的 `robot_lab_demo` 能发布地图和路径；Nav2 headless 仿真能启动并完成导航任务。

## 7. 前沿但后置的主题

- [ ] 开放词汇检测/分割与视频概念跟踪。
- [ ] feed-forward 3D reconstruction、foundation SLAM、动态场景 SLAM。
- [ ] 3D 语义地图、scene graph、语言到可达子目标。
- [ ] VLM/VLA、action chunk、flow matching、Diffusion Policy。
- [ ] Sim2Real、域随机化、主动学习、不确定性、安全屏蔽。

原则：学习模型可生成语义目标、子目标或轨迹候选；急停、碰撞检查、速度/关节限制仍由可验证的安全层执行。

## 16 周第一轮

| 周 | 主题 | 实作和验收 |
|---|---|---|
| 1 | 线代、坐标、针孔模型 | P01；手算三个点投影与反投影 |
| 2 | 标定、PnP、特征 | 用 OpenCV 完成棋盘格标定，报告重投影误差 |
| 3 | 分割、连通域、评价 | P02；手动加入噪声并调阈值 |
| 4 | CNN/ViT/检测 | P08；在 20 张图上记录误检、漏检和延迟 |
| 5 | 深度和点云 | 双目 SGBM 或 RGB-D，输出点云和误差图 |
| 6 | EKF 与传感器融合 | P06；改变噪声协方差并解释结果 |
| 7 | VO/SLAM | ORB-SLAM3 跑一个公开数据集，输出 ATE/RPE |
| 8 | 栅格、碰撞空间 | P07；改变机器人半径，观察可行域变化 |
| 9 | Dijkstra/A*/Theta* | P03；加入 Weighted A* 并画速度/代价曲线 |
| 10 | D* Lite/SIPP | 动态封路和移动行人重规划 |
| 11 | RRT/RRT*/OMPL | P04；比较种子、迭代预算和成功率 |
| 12 | DWA/MPPI/MPC | P05；报告跟踪误差、最小间隙和计算周期 |
| 13 | ROS 2、tf2、消息 | 构建并启动 `robot_lab_demo` |
| 14 | Gazebo + Nav2 | TurtleBot3 headless 与 WSLg GUI 导航 |
| 15 | MoveIt 2 或语义导航 | 按目标机器人选择一条分支 |
| 16 | 综合基准 | 20 个固定种子；报告成功率、碰撞、p95 延迟和失败分类 |

## 统一完成定义

每个项目至少包含：

1. 一个命令启动；一个命令运行测试。
2. 输入、输出、单位和坐标系说明。
3. 固定随机种子并记录依赖版本；正式基准再锁定镜像 digest/lockfile。
4. 精度、速度、资源至少三类指标。
5. 自动碰撞/越界/NaN 检查，而不只看动画。
6. 保存失败样本并解释原因。
7. 模型、数据、地图记录来源、许可和 SHA-256。
