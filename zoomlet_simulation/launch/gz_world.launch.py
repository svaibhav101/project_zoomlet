#!/usr/bin/env python3

# --- launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
# --- launch_ros
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    zoomlet_description_path = FindPackageShare("zoomlet_description")
    ros_gz_sim_path = FindPackageShare("ros_gz_sim")

    gz_world_arg = DeclareLaunchArgument(
        "gz_world", default_value="empty.sdf", description="Gazebo world file"
    )

    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=PathJoinSubstitution([zoomlet_description_path, ".."]),
    )

    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([ros_gz_sim_path, "launch", "gz_sim.launch.py"])
        ]),
        launch_arguments={"gz_args": ["-r -v 4 ", LaunchConfiguration("gz_world")]}.items(),
    )

    gz_clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    ld = LaunchDescription()
    ld.add_action(gz_world_arg)
    ld.add_action(gazebo_resource_path)
    ld.add_action(launch_gazebo)
    ld.add_action(gz_clock_bridge)
    return ld
