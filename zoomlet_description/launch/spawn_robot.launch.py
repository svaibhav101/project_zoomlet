#!/usr/bin/env python3

# --- std
import os
# --- launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
# --- launch_ros
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


ARGUMENTS = [
    DeclareLaunchArgument(
        "namespace", default_value="zoomlet1", description="Robot namespace"
    ),
    DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        choices=["true", "false"],
        description="Launch RViz",
    ),
    DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        choices=["true", "false"],
        description="Use simulation time",
    ),
    DeclareLaunchArgument(
        "gz_spawn",
        default_value="false",
        choices=["true", "false"],
        description="Spawn robot in gazebo environment.",
    ),
    # Spawn pose (gazebo)
    DeclareLaunchArgument("x", default_value="0.0", description="robot translation: x"),
    DeclareLaunchArgument("y", default_value="0.0", description="robot translation: y"),
    DeclareLaunchArgument("z", default_value="0.0", description="robot translation: z"),
    DeclareLaunchArgument(
        "yaw", default_value="0.0", description="robot orientation: yaw"
    ),
]


def generate_launch_description():

    zoomlet_description_path = FindPackageShare("zoomlet_description")

    try:
        is_ignition = "true" if os.environ["ROS_DISTRO"] == "humble" else "false"
    except Exception:
        is_ignition = "true"

    is_ignition_arg = DeclareLaunchArgument("is_ignition", default_value=is_ignition)

    model_arg = DeclareLaunchArgument(
        "model",
        default_value=PathJoinSubstitution(
            [zoomlet_description_path, "urdf", "zoomlet.urdf.xacro"]
        ),
    )

    robot_description_content = Command(
        [
            "xacro", " ", LaunchConfiguration("model"),  # mind the SPACE
            " ", "is_ignition:=", LaunchConfiguration("is_ignition"),  # mind the SPACE
            " ", "namespace:=", LaunchConfiguration("namespace"),  # mind the SPACE
        ]
    )
    robot_description = ParameterValue(robot_description_content, value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace=LaunchConfiguration("namespace"),
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        parameters=[
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "robot_description": robot_description,
            }
        ],
        output="screen",
    )

    rviz2_node = Node(
        condition=IfCondition(LaunchConfiguration("use_rviz")),
        package="rviz2",
        executable="rviz2",
        namespace=LaunchConfiguration("namespace"),
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        arguments=[
            "-d",
            PathJoinSubstitution([zoomlet_description_path, "config", "view.rviz"]),
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        output="screen",
    )

    gz_spawn_node = Node(
        condition=IfCondition(LaunchConfiguration("gz_spawn")),
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-string", robot_description_content,
            "-name", LaunchConfiguration("namespace"),
            "-x", LaunchConfiguration("x"),  # translation: x
            "-y", LaunchConfiguration("y"),  # translation: y
            "-z", LaunchConfiguration("z"),  # translation: z
            "-Y", LaunchConfiguration("yaw"),  # orientation: yaw
        ],
        output="screen",
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(is_ignition_arg)
    ld.add_action(model_arg)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(gz_spawn_node)
    ld.add_action(rviz2_node)
    return ld
