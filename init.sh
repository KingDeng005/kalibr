# Save script current directory
DIR=$(pwd)

set -e
set -u
set -x

echo "##############################################"
echo "# install Kalibr"
echo "# reference: \n"
echo "#           https://github.com/ethz-asl/kalibr/wiki/installation"
echo "##############################################"


# install dependency by ros version

# ROS_DIS = $ROS_DISTRO

# echo ROS_DIS
if [$ROS_DISTRO = "indigo"]; then
    sudo apt-get install -y python-setuptools 
    sudo apt-get install -y python-rosinstall 
    sudo apt-get install -y ipython 
    sudo apt-get install -y libeigen3-dev 
    sudo apt-get install -y libboost-all-dev 
    sudo apt-get install -y doxygen 
    sudo apt-get install -y libopencv-dev 
    sudo apt-get install -y ros-indigo-vision-opencv 
    sudo apt-get install -y ros-indigo-image-transport-plugins 
    sudo apt-get install -y ros-indigo-cmake-modules 
    sudo apt-get install -y python-software-properties 
    sudo apt-get install -y software-properties-common 
    sudo apt-get install -y libpoco-dev 
    sudo apt-get install -y python-matplotlib 
    sudo apt-get install -y python-scipy 
    sudo apt-get install -y python-git 
    sudo apt-get install -y python-pip 
    sudo apt-get install -y ipython 
    sudo apt-get install -y libtbb-dev 
    sudo apt-get install -y libblas-dev 
    sudo apt-get install -y liblapack-dev 
    sudo apt-get install -y python-catkin-tools 
    sudo apt-get install -y libv4l-dev

    sudo pip install python-igraph --upgrade
fi

if [ $ROS_DISTRO = "kinetic" ]; then
    sudo apt-get install -y python-setuptools 
    sudo apt-get install -y python-rosinstall 
    sudo apt-get install -y ipython 
    sudo apt-get install -y libeigen3-dev 
    sudo apt-get install -y libboost-all-dev 
    sudo apt-get install -y doxygen 
    sudo apt-get install -y libopencv-dev 
    sudo apt-get install -y ros-kinetic-vision-opencv 
    sudo apt-get install -y ros-kinetic-image-transport-plugins 
    sudo apt-get install -y ros-kinetic-cmake-modules 
    sudo apt-get install -y python-software-properties 
    sudo apt-get install -y software-properties-common 
    sudo apt-get install -y libpoco-dev 
    sudo apt-get install -y python-matplotlib 
    sudo apt-get install -y python-scipy 
    sudo apt-get install -y python-git 
    sudo apt-get install -y python-pip 
    sudo apt-get install -y ipython 
    sudo apt-get install -y libtbb-dev 
    sudo apt-get install -y libblas-dev 
    sudo apt-get install -y liblapack-dev 
    sudo apt-get install -y python-catkin-tools 
    sudo apt-get install -y libv4l-dev

    sudo pip install python-igraph --upgrade
fi

# ros build 
cd ../../
catkin config --extend /opt/ros/$ROS_DISTRO
catkin build


cd $DIR

