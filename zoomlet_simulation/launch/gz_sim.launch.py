#!/usr/bin/env python3

# --- launch
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
# --- launch_ros
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_simulation = FindPackageShare("zoomlet_simulation")

    world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_simulation, "launch", "gz_world.launch.py"])
        ),
    )

    zoomlet1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_simulation, "launch", "gz_spawn.launch.py"])
        ),
        launch_arguments={
            "namespace": "zoomlet1",  # must be explicit - LaunchConfiguration default doesn't resolve across IncludeLaunchDescription
            "use_rviz": "true", "use_sim_time": "true", "gz_spawn": "true",
            "is_ignition": "true",
            "x": "0.0", "y": "0.0", "z": "0.0",
            "yaw": "0.0",
        }.items(),
    )

    zoomlet2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_simulation, "launch", "gz_spawn.launch.py"])
        ),
        launch_arguments={
            "namespace": "zoomlet2",  # must be explicit - LaunchConfiguration default doesn't resolve across IncludeLaunchDescription
            "use_rviz": "true", "use_sim_time": "true", "gz_spawn": "true", 
            "is_ignition": "true",
            "x": "2.0", "y": "1.0", "z": "0.0",
            "yaw": "0.0",
        }.items(),
    )

    zoomlet3 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_simulation, "launch", "gz_spawn.launch.py"])
        ),
        launch_arguments={
            "namespace": "zoomlet3",  # must be explicit - LaunchConfiguration default doesn't resolve across IncludeLaunchDescription
            "use_rviz": "true", "use_sim_time": "true", "gz_spawn": "true", 
            "is_ignition": "true",
            "x": "-2.0", "y": "1.0", "z": "0.0",
            "yaw": "0.0",
        }.items(),
    )

    ld = LaunchDescription()
    ld.add_action(world)
    ld.add_action(TimerAction(period=0.0, actions=[zoomlet1]))
    ld.add_action(TimerAction(period=3.0, actions=[zoomlet2]))
    ld.add_action(TimerAction(period=6.0, actions=[zoomlet3]))

    return ld
