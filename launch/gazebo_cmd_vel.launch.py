from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import os

def generate_launch_description():
    ros2_ws = os.environ.get("ROS2_WS")
    world_path = os.path.join(
        ros2_ws,
        "src/models/world.sdf"
    )

    return LaunchDescription([

        # Gazebo
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_path],
            output="screen"
        ),

        # Bridge
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=["/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist"],
            output="screen"
        ),

        # Teleop(sudo apt install xtermでxtermのインストールが必要)
        Node(
            package="gazebo_simulator",
            executable="teleop_twist_keyboard",
            output="screen",
            prefix="xterm -e"
        ),
    ])