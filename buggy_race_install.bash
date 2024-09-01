#!/bin/bash
#run "bash /path/to/install.bash"
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing locales..."
sudo apt install locales

echo "Generating locale en_US.UTF-8..."
sudo locale-gen en_US en_US.UTF-8

echo "Updating system locale settings..."
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

echo "Installing software-properties-common..."
sudo apt install software-properties-common

echo "Adding the 'universe' repository..."
sudo add-apt-repository universe

echo "Installing curl..."
sudo apt install curl -y

ROS_VERSION="humble"

if ! [ -f /usr/share/keyrings/ros-archive-keyring.gpg ]; then
  echo "Adding ROS keyring..."
  sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
fi

if ! [ -f /etc/apt/sources.list.d/ros2.list ]; then
  echo "Adding ROS 2 repository..."
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
fi

echo "Updating package lists..."
sudo apt-get -y update

echo "Installing ROS 2 and other dependencies..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  ament-cmake \
  python3-colcon-common-extensions \
  python3-colcon-ros \
  python3-rosdep \
  python3-vcstool \
  ros-${ROS_VERSION}-actuator-msgs \
  ros-${ROS_VERSION}-compressed-image-transport \
  ros-${ROS_VERSION}-cyclonedds \
  ros-${ROS_VERSION}-desktop \
  ros-${ROS_VERSION}-foxglove-bridge \
  ros-${ROS_VERSION}-gps-msgs \
  ros-${ROS_VERSION}-nav2-bringup \
  ros-${ROS_VERSION}-navigation2 \
  ros-${ROS_VERSION}-rmw-cyclonedds-cpp \
  ros-${ROS_VERSION}-rqt-tf-tree \
  ros-${ROS_VERSION}-topic-tools

GAZEBO_VERSION="harmonic"

if ! [ -f /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg ]; then
  echo "Adding Gazebo keyring..."
  sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
fi

if ! [ -f /etc/apt/sources.list.d/gazebo-stable.list ]; then
  echo "Adding Gazebo repository..."
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
fi

echo "Updating package lists..."
sudo apt-get -y update

echo "Installing Gazebo and ROS 2 Gazebo packages..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  gz-${GAZEBO_VERSION} \
  ros-humble-ros-gz${GAZEBO_VERSION}-bridge \
  ros-humble-ros-gz${GAZEBO_VERSION}-image \
  ros-humble-ros-gz${GAZEBO_VERSION}-sim

echo "Installing additional tools..."
sudo apt-get update
sudo apt install gnome-terminal
sudo apt-get install git wget -y


# Modify .bashrc
if ! grep -qF "BuggyRace" ~/.bashrc; then
  echo "Modifying .bashrc to set up ROS environment..."
  cat << EOF >> ~/.bashrc
# BuggyRace
source /opt/ros/humble/setup.bash

if [ -f \$HOME/cognipilot/gazebo/install/setup.sh ]; then
  source \$HOME/BuggyRace/install/setup.sh
fi
source /usr/share/colcon_cd/function/colcon_cd.sh
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
export ROS_DOMAIN_ID=9
export CMAKE_EXPORT_COMPILE_COMMANDS=ON
export CCACHE_TEMPDIR=/tmp/ccache
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export PYTHONWARNINGS=ignore:::setuptools.installer,ignore:::setuptools.command.install,ignore:::setuptools.command.easy_install

EOF
fi

if [ ! -f ~/BuggyRace/.git/HEAD ]; then
  echo "Cloning BuggyRace repository..."
  cd ~
  git clone https://github.com/SiPAyi/BuggyRace.git
else
  echo "BuggyRace repository already exists, pulling latest changes..."
  cd ~/BuggyRace
  git pull
fi

echo "Building BuggyRace workspace..."
cd ~/BuggyRace
colcon build --symlink-install
source ~/.bashrc

echo "Installing OpenCV Python package..."
pip install opencv-python

echo "Updating rosdep..."
sudo rosdep init
sudo rosdep update

echo "Installing dependencies"
cd ~/BuggyRace
rosdep install --from-paths src --ignore-src -r -y


echo "Script execution completed."

