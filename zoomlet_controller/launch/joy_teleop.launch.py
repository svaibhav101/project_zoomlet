#!/usr/bin/env python3

# -- LAUNCH ---
# Core ROS 2 launch system
from launch import LaunchDescription

# -- LAUNCH. ---
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

# -- LAUNCH_ROS ---
# Node → used to launch ROS 2 nodes
from launch_ros.actions import Node

# FindPackageShare → finds the share directory of a ROS package
from launch_ros.substitutions import FindPackageShare

ARGUMENTS = [
    DeclareLaunchArgument(
        "namespace", default_value="", description="Robot namespace"
    )
]


def generate_launch_description():

    # Find the path to the package "abc_description"
    # zoomlet_controller_pkg_path = FindPackageShare("zoomlet_controller").find("zoomlet_controller")
    zoomlet_controller_pkg_path = FindPackageShare("zoomlet_controller")

    # Build full path to the JOY configuration file
    joy_config_path = PathJoinSubstitution(
        [zoomlet_controller_pkg_path, "config", "joy_config.yaml"]
    )

    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joystick",
        namespace=LaunchConfiguration("namespace"),
        parameters=[joy_config_path],
        output="screen",
    )

    joy_teleop_node = Node(
        package="joy_teleop",
        executable="joy_teleop",
        name="joy_teleop",
        namespace=LaunchConfiguration("namespace"),
        parameters=[joy_config_path],
        # remappings=[("/cmd_vel", "/zoomlet1/diffdrive_controller/cmd_vel")],
        output="screen",
    )

    # Return launch description containing all nodes and arguments
    return LaunchDescription(ARGUMENTS + [joy_node, joy_teleop_node])
