FROM ros:jazzy-ros-base-noble

ARG DEBIAN_FRONTEND=noninteractive
ARG ROS_APT_MIRROR=""

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ROS_APT_MIRROR may be set to a documented mirror such as
# https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/ when building in China.
RUN if [[ -n "${ROS_APT_MIRROR}" ]]; then \
      find /etc/apt/sources.list.d -type f -exec \
        sed -i "s|http://packages.ros.org/ros2/ubuntu|${ROS_APT_MIRROR%/}|g; \
                s|https://packages.ros.org/ros2/ubuntu|${ROS_APT_MIRROR%/}|g" {} +; \
    fi \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      python3-colcon-common-extensions \
      python3-matplotlib \
      python3-numpy \
      python3-pip \
      ros-jazzy-nav2-bringup \
      ros-jazzy-nav2-minimal-tb3-sim \
      ros-jazzy-navigation2 \
      ros-jazzy-ros-gz \
      ros-jazzy-rviz2 \
      ros-jazzy-slam-toolbox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . /workspace

RUN python3 -m pip install --break-system-packages --no-deps -e /workspace \
    && cd /workspace/ros2_ws \
    && source /opt/ros/jazzy/setup.bash \
    && colcon build --symlink-install \
    && chmod +x /workspace/docker/entrypoint.sh

ENV ROS_DISTRO=jazzy
ENV ROS_DOMAIN_ID=42
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp

ENTRYPOINT ["/workspace/docker/entrypoint.sh"]
CMD ["ros2", "launch", "robot_lab_demo", "astar_demo.launch.py"]
