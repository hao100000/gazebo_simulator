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

        # Bridge wheel joint commands from ROS to Gazebo
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                "/model/demoRobot/joint/wheel_left_joint/cmd_vel@std_msgs/msg/Float64@gz.msgs.Double",
                "/model/demoRobot/joint/wheel_right_joint/cmd_vel@std_msgs/msg/Float64@gz.msgs.Double",
            ],
            output="screen"
        ),

        # Convert CAN motor commands to joint velocity commands
        Node(
            package="gazebo_simulator",
            executable="can_to_joint_velocity",
            output="screen"
        ),

        # Teleop(sudo apt install xtermでxtermのインストールが必要)
        Node(
            package="gazebo_simulator",
            executable="teleop_CANArray_keyboard",
            output="screen",
            prefix="xterm -e"
        ),
    ])