#!/usr/bin/env python3

import os  # Used to read environment variables like ROS_DISTRO

# -- LAUNCH ---
# Core ROS 2 launch system
from launch import LaunchDescription

# -- LAUNCH. ---
# DeclareLaunchArgument -> create arguments that can be passed when launching
# SetEnvironmentVariable -> set environment variables during launch
# IncludeLaunchDescription -> include another launch file
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    IncludeLaunchDescription,
)

# Allows launching nodes conditionally
from launch.conditions import IfCondition

# Command -> executes shell command (used for xacro processing)
# LaunchConfiguration -> retrieves values of launch arguments
from launch.substitutions import Command, LaunchConfiguration
from launch.substitutions import PathJoinSubstitution

# Used to include another Python launch file
from launch.launch_description_sources import PythonLaunchDescriptionSource

# -- LAUNCH_ROS ---
# Node -> used to launch ROS 2 nodes
from launch_ros.actions import Node

# FindPackageShare -> finds the share directory of a ROS package
from launch_ros.substitutions import FindPackageShare

# ParameterValue -> ensures correct parameter type is passed
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Find the path to the package "zoomlet_description"
    zoomlet_description_path = FindPackageShare("zoomlet_description")

    # Find the path to ros_gz_sim package (used for Gazebo simulation)
    ros_gz_sim_path = FindPackageShare("ros_gz_sim")

    # Build full path to the RViz configuration file
    rviz_config_path = PathJoinSubstitution(
        [zoomlet_description_path, "config", "view.rviz"]
    )

    # Launch argument for robot model (URDF/Xacro)
    # Allows user to override the robot model path
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=PathJoinSubstitution(
            [
                zoomlet_description_path,
                "urdf",
                "zoomlet.urdf.xacro",
            ]
        ),
        description="Absolute path to robot URDF file.",
    )

    # Detect ROS distribution to determine simulation type
    try:
        ros_distro = os.environ["ROS_DISTRO"]

        # If using ROS2 Humble -> assume Ignition Gazebo
        is_ignition = "true" if ros_distro == "humble" else "false"

    except Exception:
        # Default fallback if ROS_DISTRO not found
        is_ignition = "true"

    # Launch argument that determines if Ignition Gazebo is used
    ignition_arg = DeclareLaunchArgument(
        name="is_ignition",
        default_value=is_ignition,
        choices=["true", "false"],
        description="Use Ignition Gazebo if true",
    )

    # Launch argument to optionally enable/disable RViz
    rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        choices=["true", "false"],
        description="Launch RViz",
    )

    # Launch argument to control simulation time
    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        choices=["true", "false"],
        description="Use simulation time",
    )

    # Convert Xacro file -> URDF using xacro command
    # Also passes parameter is_ignition to the xacro file
    robot_description = ParameterValue(
        Command(
            [
                "xacro",
                " ",  # Required space so command executes properly
                LaunchConfiguration("model"),
                " is_ignition:=",
                LaunchConfiguration("is_ignition"),
            ]
        ),
        value_type=str,
    )

    # Node that publishes TF transforms based on URDF
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,  # robot URDF
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }
        ],
        output="screen",
    )

    # Set Gazebo resource path so Gazebo can find models, meshes, and worlds
    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=PathJoinSubstitution([zoomlet_description_path, ".."]),
    )

    # Launch Gazebo simulator using ros_gz_sim launch file
    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [
                        ros_gz_sim_path,
                        "launch",
                        "gz_sim.launch.py",
                    ]
                ),
            ]
        ),
        # Gazebo arguments
        launch_arguments={"gz_args": "-r -v 4 empty.sdf"}.items(),
        # -r -> run immediately
        # -v 4 -> verbose level
        # empty.sdf -> load empty world
    )

    # Bridge Gazebo clock -> ROS /clock topic
    # Required for all nodes using use_sim_time: true
    # Without this, all sim-time nodes are frozen at t=0
    # causing TwistStamped to publish with zero timestamps
    gz_ros2_bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
        ],
        # remappings=[("/imu", "/imu/out")],
        output="screen",
    )

    # Spawn the robot entity inside Gazebo
    gz_spawn_entity_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "robot_description",  # get robot model from this topic
            "-name",
            "zoomlet",  # name of robot in Gazebo
        ],
        output="screen",
    )

    # Launch RViz visualization node
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        # Load RViz config file automatically
        arguments=["-d", rviz_config_path],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        output="screen",
        # Launch only if use_rviz argument is true
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    # Return launch description containing all nodes and arguments
    return LaunchDescription(
        [
            model_arg,
            ignition_arg,
            rviz_arg,
            use_sim_time_arg,
            robot_state_publisher_node,
            rviz2_node,
            gazebo_resource_path,
            launch_gazebo,
            gz_ros2_bridge_node,
            gz_spawn_entity_node,
        ]
    )