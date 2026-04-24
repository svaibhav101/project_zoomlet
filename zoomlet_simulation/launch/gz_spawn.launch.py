#!/usr/bin/env python3

# --- std
import os
# --- launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
# --- launch_ros
from launch_ros.substitutions import FindPackageShare


ARGUMENTS = [
    DeclareLaunchArgument("namespace", default_value="", 
        description="Robot namespace"),
    DeclareLaunchArgument("use_rviz",  default_value="true", choices=["true","false"],
        description="Launch RViz",),
    DeclareLaunchArgument("use_sim_time", default_value="true", choices=["true","false"],
        description="Use simulation time",),
    DeclareLaunchArgument("gz_spawn", default_value="true", choices=["true","false"],
        description="Spawn robot in gazebo environment.",),
    
    # Spawn pose (gazebo)
    DeclareLaunchArgument("x",   default_value="0.0", description="robot translation: x"),
    DeclareLaunchArgument("y",   default_value="0.0", description="robot translation: y"),
    DeclareLaunchArgument("z",   default_value="0.0", description="robot translation: z"),
    DeclareLaunchArgument("yaw", default_value="0.0", description="robot orientation: yaw"),
]


def generate_launch_description():
    pkg_description = FindPackageShare("zoomlet_description")
    pkg_controller = FindPackageShare("zoomlet_controller")

    try:
        is_ignition = "true" if os.environ["ROS_DISTRO"] == "humble" else "false"
    except Exception:
        is_ignition = "true"
    is_ignition_arg = DeclareLaunchArgument("is_ignition", default_value=is_ignition)
    
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_description, "launch", "spawn_robot.launch.py"])
        ),
        launch_arguments={
            "namespace": LaunchConfiguration("namespace"),  # must be explicit - LaunchConfiguration default doesn't resolve across IncludeLaunchDescription
            "use_rviz": LaunchConfiguration("use_rviz"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "gz_spawn": LaunchConfiguration("gz_spawn"),
            "is_ignition": LaunchConfiguration("is_ignition"),
            "x": LaunchConfiguration("x"),
            "y": LaunchConfiguration("y"),
            "z": LaunchConfiguration("z"),
            "yaw": LaunchConfiguration("yaw"),
        }.items(),
    )
    
    spawn_controller =  IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_controller, "launch", "controller.launch.py"])
        ),
        launch_arguments={
            "namespace": LaunchConfiguration("namespace"),  # must be explicit - LaunchConfiguration default doesn't resolve across IncludeLaunchDescription
        }.items(),
    )


    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(is_ignition_arg)
    ld.add_action(spawn_robot)
    ld.add_action(spawn_controller)

    return ld
