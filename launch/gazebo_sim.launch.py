from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    pkg_share = FindPackageShare('gazebo_simulator')
    ros2_ws = os.environ.get("ROS2_WS")
    world_path = os.path.join(
        ros2_ws,
        "src/models/world.sdf"
    )
    xacro_file = PathJoinSubstitution([
        pkg_share,
        'urdf',
        'demorobot.urdf.xacro'
    ])
    robot_description = Command(['xacro ', xacro_file])
    controller_config_path = os.path.join(
        ros2_ws,
        "src/gazebo_simulator/config/controller_config.yaml"
    )

    return LaunchDescription([
        # Gazebo
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_path],
            output="screen"
        ),

        # URDF配信
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),


        # Controller Manager
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[controller_config_path],
            output="screen",
        ),

        # Joint State Broadcaster
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager", "/controller_manager"
            ],
            output="screen",
        ),

        # Forward Velocity Controller
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "forward_velocity_controller",
                "--controller-manager", "/controller_manager"
            ],
            output="screen",
        ),

        # CAN to Gazebo Converter (C++)
        Node(
            package="gazebo_simulator",
            executable="can_to_gazebo",
            output="screen"
        ),

        # Teleop (optional)
        Node(
            package="gazebo_simulator",
            executable="teleop_CANArray_keyboard",
            output="screen",
            prefix="xterm -e"
        ),
    ])
