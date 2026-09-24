#!/usr/bin/env bash
set -euo pipefail

if [[ "$(. /etc/os-release && echo "${VERSION_CODENAME}")" != "noble" ]]; then
  echo "This script requires Ubuntu 24.04 (noble)." >&2
  exit 1
fi

sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe -y

ros_apt_source_version="${ROS_APT_SOURCE_VERSION:-1.3.0}"

curl -fsSL -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ros_apt_source_version}/ros2-apt-source_${ros_apt_source_version}.noble_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  ros-jazzy-desktop \
  ros-dev-tools \
  ros-jazzy-ros-gz \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-minimal-tb3-sim \
  ros-jazzy-slam-toolbox \
  ros-jazzy-moveit \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-cv-bridge \
  ros-jazzy-image-transport \
  ros-jazzy-vision-msgs \
  mesa-utils \
  vulkan-tools

if ! grep -Fq 'source /opt/ros/jazzy/setup.bash' "${HOME}/.bashrc"; then
  printf '\nsource /opt/ros/jazzy/setup.bash\n' >> "${HOME}/.bashrc"
fi

echo "ROS 2 Jazzy setup complete. Open a new shell, then run: ros2 doctor --report"
