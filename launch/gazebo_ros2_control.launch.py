from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
import os


def generate_launch_description():
    ros2_ws = os.environ.get("ROS2_WS")
    world_path = os.path.join(
        ros2_ws,
        "src/models/world_ros2control.sdf"
    )
    controller_config_path = os.path.join(
        ros2_ws,
        "src/gazebo_simulator/config/controller_config.yaml"
    )
    urdf_path = os.path.join(
        ros2_ws,
        "src/gazebo_simulator/urdf/demorobot.urdf.xacro"
    )

    return LaunchDescription([
        # Gazebo
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_path],
            output="screen"
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

        # Joint Trajectory Controller
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "demorobot_joint_trajectory_controller",
                "--controller-manager", "/controller_manager"
            ],
            output="screen",
        ),

        # CAN to Joint Trajectory Converter (C++)
        Node(
            package="gazebo_simulator",
            executable="can_to_joint_trajectory_node",
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
