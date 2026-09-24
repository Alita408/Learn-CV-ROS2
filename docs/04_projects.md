# 项目设计、运行方法与验收

P01–P07 只依赖 NumPy 和 Matplotlib，已经在当前机器实际运行。P08 是联网的现代模型项目。所有图默认写入 `outputs/`。

## P01：相机几何与 RGB-D 点云

目标：理解针孔模型，而不是把深度 API 当黑盒。

```powershell
python -m examples.p01_camera_geometry
```

流程：生成米制深度图 → 用内参反投影成 3D 点 → 再投影回像素 → 绘制深度和点云。

验收：

- 单元测试的像素 round-trip 在浮点误差内一致。
- 能解释 `fx/fy/cx/cy` 和相机坐标轴。
- 深度非正或 NaN 不进入点云。

扩展：加入畸变；读取真实 `CameraInfo`；将点云变换到 `base_link`。

## P02：可解释的颜色检测基线

```powershell
python -m examples.p02_color_detection
```

流程：RGB 主色阈值 → 二值 mask → 4 连通域 → 面积过滤 → bbox/centroid。

验收：检测出 3 个大障碍并过滤小红噪声；框不越界。

扩展：改成 HSV；加入形态学；用 YOLO 的 AP/Recall 指标比较规则基线。机器人项目必须保留一个简单基线，它常能暴露数据和坐标问题。

## P03：Dijkstra 与 A*

```powershell
python -m examples.p03_astar_grid
```

实现了 8 邻域、octile heuristic、对角 corner-cutting 防护。

验收：

- A* 与 Dijkstra 得到相同最优代价。
- A* 展开节点更少。
- 路径不穿障碍，也不从障碍角缝中挤过。

扩展：Weighted A*、Theta*、JPS；在 MovingAI 地图上输出 CSV：路径代价、展开数、耗时。

## P04：RRT*

```powershell
python -m examples.p04_rrt_star
```

流程：目标偏置采样 → 最近节点 → steer → 线段/圆碰撞检测 → 选择低成本父节点 → 邻域重连。

验收：固定种子找到无碰撞路径；起终点正确；输出节点数、迭代数和代价。

扩展：重复 100 个种子，画成功率/路径质量随迭代预算的曲线；加入 Informed RRT*；在 OMPL 对照 BIT*/AIT*/EIT*。

## P05：DWA 局部控制

```powershell
python -m examples.p05_dwa_local_planner
```

流程：根据当前速度和加速度约束构造 dynamic window → 前向滚动差速模型 → 对目标距离、朝向、速度和间隙打分 → 只执行第一步。

验收：预测轨迹不进入机器人半径；闭环到达目标阈值；无 NaN。

扩展：把 A* 全局路径加入评分；加入移动障碍；与 RPP、DWB、MPPI 比较 RMS 跟踪误差、最小间隙、jerk 和单周期时间。

## P06：EKF 地标定位

```powershell
python -m examples.p06_ekf_localization
```

流程：带偏差/噪声的里程计预测 → 地标 range-bearing 更新 → Joseph form 协方差更新。

本机固定种子的示例结果：纯里程计位置 RMSE 约 `0.85 m`，EKF 约 `0.10 m`。

验收：更新后位置误差下降；协方差维度和角度归一正确。

扩展：NEES/NIS 一致性检验；加入 IMU bias；用 `robot_localization` 对照。

## P07：感知到规划的最小闭环

```powershell
python -m examples.p07_perception_to_planning
```

流程：俯视 RGB → 红色障碍 mask → 按机器人半径膨胀 → A* → 路径可视化。

这是仓库最重要的集成样例：识别输出不能直接成为路径，必须先形成有坐标、分辨率、footprint 和未知区语义的地图。

验收：固定场景得到路径；路径不进入膨胀障碍；改变膨胀半径后可行域按预期收缩。

扩展：把二值分割替换为 PIDNet/SegFormer；使用 RGB-D 投影到 `base_link`；发布 Nav2 costmap layer。

## P08：YOLO26 现代检测

安装并运行：

```powershell
conda run -n robotlab python -m pip install -e ".[modern-vision]"
conda run -n robotlab python -m examples.p08_yolo26_inference
```

首次运行下载 `yolo26n.pt` 和官方示例图。也可指定本地图像：

```powershell
conda run -n robotlab python -m examples.p08_yolo26_inference `
  --source D:\data\frame.jpg `
  --output outputs\my_detection.jpg
```

验收不能只看图片：至少准备 20–100 张本场景数据，记录 mAP50-95、Recall、p50/p95 延迟、峰值显存，并保留误检/漏检样本。商用前复核 Ultralytics 的 AGPL/企业许可。

## P09：ROS 2 地图与 Path 发布节点

镜像内运行：

```bash
docker compose up --build algorithm-demo
```

节点将同一 A* 思想封装为 ROS 2 程序，使用 transient-local QoS 发布 `/demo_map` 和 `/demo_path`。

验收：

```bash
docker compose exec algorithm-demo ros2 topic echo /demo_path --once
```

消息包含有效 `frame_id=map`、时间戳和连续 poses。

扩展：RViz 显示；订阅实时 `OccupancyGrid`；将算法改写为 Nav2 GlobalPlanner 插件。

## P10：Nav2 TurtleBot3 仿真启动骨架与基准规格

环境就绪后：

```bash
docker compose --profile sim up nav2-headless
```

GUI 在 WSL 原生运行：

```bash
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

当前仓库完成的是可运行的 headless 仿真入口；自动发目标、切换插件、动态障碍注入与指标采集 harness 是本项目下一步实现内容。计划实验矩阵：

- 全局：NavFn、Smac 2D、Theta*。
- 局部：DWB、RPP、MPPI。
- 场景：开阔、窄门、U 型障碍、动态障碍。

最终验收（尚未实现自动化）：每个组合 20 个固定种子；统计成功率、碰撞率、路径长度、最小间隙、跟踪 RMS、p50/p95 规划延迟。学习模型不参与安全层。

## 下一阶段的独立项目规格

这些项目需要额外数据/大型依赖，所以没有塞进基础镜像；应分别创建锁版本环境。

### A. 深度与点云

1. OpenCV SGBM 理解 rectification/disparity/尺度。
2. DA3 Small/Base 或 Fast-FoundationStereo。
3. 输出深度、置信度、`PointCloud2` 和俯视障碍图。
4. 与仿真真值比较 AbsRel/RMSE，并单独统计弱纹理、反光和远距离。

### B. 6D 位姿

基线 AprilTag/PnP；进阶 detector/mask + RGB-D + CAD → FoundationPose。输出 `camera → object` TF 和 pre-grasp pose，按平移、旋转、ADD/ADD-S 评估。

### C. SLAM 基准

统一比较 ORB-SLAM3、DPVO、MASt3R-SLAM/VGGT-SLAM。统一导出 TUM 轨迹、PLY/map、Hz 和峰值内存；用 `evo` 算 ATE/RPE并记录跟踪丢失。

### D. 开放词汇 3D 语义地图

YOLO-World/YOLOE/SAM 3 接文本查询；mask + depth + SLAM pose 多帧融合为 3D landmark；把目标转换为安全可达 waypoint，而不是物体中心。

### E. MoveIt 2 机械臂规划

Panda/Kinova 上比较 RRTConnect、PRM*、BIT*、OMPL→CHOMP/STOMP。固定 50 个查询，报告成功率、首解时间、路径长度、最小间隙和平滑度。

### F. VLA 仿真操作

先 ACT/Diffusion Policy，再 SmolVLA；使用 LIBERO/RoboCasa，收集 50–100 条一致演示。至少 20 回合未见布局评测，报告成功率、完成时间、动作频率和失败类型。π0.5/GR00T 需更大 GPU。

## 一键回归

```powershell
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File .\scripts\run_native_examples.ps1
```

新增算法时先写一个会失败的测试，然后实现；不要用动画“看起来合理”代替碰撞和数值验证。
