from launch import LaunchDescription
from launch.actions import ExecuteProcess, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os
import subprocess


def regenerate_model_sdf(context, *args, **kwargs):
    ros2_ws = os.environ.get("ROS2_WS")
    if not ros2_ws:
        raise RuntimeError("ROS2_WS environment variable is required")

    xacro_path = os.path.join(
        ros2_ws,
        "src/gazebo_simulator/urdf/demorobot.urdf.xacro"
    )
    model_dir = os.path.join(
        ros2_ws,
        "src/models/demorobot"
    )
    urdf_path = os.path.join(model_dir, "demorobot.urdf")
    model_sdf_path = os.path.join(model_dir, "model.sdf")

    with open(urdf_path, "w", encoding="utf-8") as urdf_file:
        subprocess.run(["xacro", xacro_path], check=True, stdout=urdf_file)

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        subprocess.run(["gz", "sdf", "-p", urdf_path], check=True, stdout=sdf_file)

    with open(model_sdf_path, "r", encoding="utf-8") as sdf_file:
        model_sdf = sdf_file.read()

    model_sdf = model_sdf.replace("model://meshes/", "../meshes/")

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        sdf_file.write(model_sdf)

    return []


def generate_launch_description():
    pkg_share = FindPackageShare('gazebo_simulator')
    ros2_ws = os.environ.get("ROS2_WS")
    world_path = os.path.join(
        ros2_ws,
        "src/models/world.sdf"
    )
    models_path = os.path.join(
        ros2_ws,
        "src/models"
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
    
    # Set GZ_MODEL_PATH environment variable
    gz_model_path = os.environ.get("GZ_MODEL_PATH", "")
    if gz_model_path:
        gz_model_path = models_path + ":" + gz_model_path
    else:
        gz_model_path = models_path
    
    # Set GZ_SIM_SYSTEM_PLUGIN_PATH for gazebo_ros2_control plugin
    gz_plugin_path = os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "")
    if gz_plugin_path:
        gz_plugin_path = gz_plugin_path + ":/opt/ros/jazzy/lib"
    else:
        gz_plugin_path = "/opt/ros/jazzy/lib"

    return LaunchDescription([
        OpaqueFunction(function=regenerate_model_sdf),

        # Gazebo
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_path],
            output="screen",
            additional_env={
                "GZ_MODEL_PATH": gz_model_path,
                "GZ_SIM_SYSTEM_PLUGIN_PATH": gz_plugin_path
            }
        ),

        # URDF配信
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }],
            output='screen'
        ),
                
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
            ],
            output='screen'
        ),

        # Joint State Broadcaster (spawned within Gazebo)
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
