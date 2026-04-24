#!/usr/bin/env python3

# -- LAUNCH ---
# Core launch system for ROS 2
from launch import LaunchDescription

# -- LAUNCH.ACTIONS ---
# DeclareLaunchArgument: used to create launch arguments that can be passed when launching
# Command: runs shell commands (used here to process xacro)
# LaunchConfiguration: retrieves values of launch arguments
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch.substitutions import PathJoinSubstitution

# -- LAUNCH_ROS.ACTIONS ---
# Node: used to launch ROS 2 nodes
from launch_ros.actions import Node

# FindPackageShare: finds the share directory of a ROS package
from launch_ros.substitutions import FindPackageShare

# ParameterValue: ensures the correct parameter type is passed to nodes
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Locate the share directory of the package "zoomlet_description"
    zoomlet_description_path = FindPackageShare("zoomlet_description")

    # Build the full path to the RViz configuration file
    rviz_config_path = PathJoinSubstitution(
        [zoomlet_description_path, "config", "view.rviz"]
    )

    # Declare a launch argument named "model"
    # This allows the user to optionally pass a different URDF/XACRO file when launching
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

    # Declare a launch argument to control whether simulation time should be used
    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description="Use simulation time",
    )

    # Convert the XACRO file into a URDF string using the xacro command
    # The output is stored in the parameter 'robot_description'
    robot_description = ParameterValue(
        Command(
            [
                "xacro",
                " ",  # NOTE: space is required so command executes correctly
                LaunchConfiguration("model"),
            ]
        ),
        value_type=str,
    )

    # Node that publishes the robot's TF transforms based on the URDF
    # It reads the robot_description parameter
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,  # URDF description of the robot
                "use_sim_time": LaunchConfiguration("use_sim_time"),  # simulation clock
            }
        ],
        output="screen",
    )

    # GUI tool that allows manual control of robot joint states
    # Useful for testing robot visualization without real hardware
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen",
    )

    # Launch RViz2 for visualization
    # Loads a predefined configuration file
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config_path],  # load rviz config file
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        output="screen",
    )

    # Return the full launch description with all arguments and nodes
    return LaunchDescription(
        [
            model_arg,
            use_sim_time_arg,
            robot_state_publisher_node,
            joint_state_publisher_gui_node,
            rviz2_node,
        ]
    )
