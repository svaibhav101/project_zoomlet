#!/usr/bin/env python3


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.conditions import LaunchConfigurationNotEquals


from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


ARGUMENTS = [
    DeclareLaunchArgument(
        "namespace", default_value="", description="Robot namespace"
    ),
]


def generate_launch_description():

    namespace = LaunchConfiguration("namespace")

    zoomlet_controller_pkg_path = FindPackageShare("zoomlet_controller")

    # Build full path to the JOY configuration file
    controller_config_path = PathJoinSubstitution(
        [zoomlet_controller_pkg_path, "config", "zoomlet_controllers.yaml"]
    )

    # controller_manager = PathJoinSubstitution(
    #     [LaunchConfiguration("namespace"), "controller_manager"]
    # )

    # Nodes
    joint_state_broadcaster_spawner_node = Node(
        package="controller_manager",
        executable="spawner",
        namespace=namespace,
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "controller_manager",
            # controller_manager,
        ],
        # parameters=[{"use_sim_time": use_sim_time}], # NOT NEEDED
        output="screen",
    )

    diffdrive_controller_node = Node(
        package="controller_manager",
        executable="spawner",
        namespace=namespace,
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        parameters=[controller_config_path],
        arguments=[
            "diffdrive_controller",
            "--controller-manager",
            "controller_manager",
            # controller_manager,
        ],
        output="screen",
    )

    diffdrive_controller_callback = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner_node,
            on_exit=[diffdrive_controller_node],
        )
    )

    # diffdrive_controller_callback = TimerAction(
    #     period=2.0, actions=[diffdrive_controller_node]
    # )

    tf_namespaced_odom_publisher = Node(
        condition=LaunchConfigurationNotEquals("namespace", ""),
        package="tf2_ros",
        executable="static_transform_publisher",
        name="tf_namespaced_odom_publisher",
        namespace=namespace,
        arguments=[
            "--x", "0",
            "--y", "0",
            "--z", "0",
            "--roll", "0",
            "--pitch", "0",
            "--yaw", "0",
            "--frame-id", "odom",
            "--child-frame-id", [namespace, "/odom"], # odom --> ns/odom
        ],
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        output="screen",
    )
    
    tf_namespaced_base_footprint_publisher = Node(
        condition=LaunchConfigurationNotEquals("namespace", ""),
        package="tf2_ros",
        executable="static_transform_publisher",
        name="tf_namespaced_base_footprint_publisher",
        namespace=namespace,
        arguments=[
            "--x", "0",
            "--y", "0",
            "--z", "0",
            "--roll", "0",
            "--pitch", "0",
            "--yaw", "0",
            "--frame-id", [namespace, "/base_footprint"], 
            "--child-frame-id", "base_footprint", # ns/base_footprint --> base_footprint
        ],
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
        output="screen",
    )
    

    ld = LaunchDescription(ARGUMENTS)

    ld.add_action(joint_state_broadcaster_spawner_node)
    ld.add_action(diffdrive_controller_callback)
    ld.add_action(tf_namespaced_odom_publisher)
    ld.add_action(tf_namespaced_base_footprint_publisher)

    return ld
