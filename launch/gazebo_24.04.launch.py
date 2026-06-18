from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
import os
import re
import subprocess
import tempfile

# ============================================================
# 設定：これらの2つの変数を変更すると、使用するモデルを切り替えられます
# ============================================================
DEFAULT_MODEL_NAME = "omni_robot"
DEFAULT_WORLD_FILE = "world.sdf"


def launch_setup(context, *args, **kwargs):
    ros2_ws = os.environ.get("ROS2_WS")
    if not ros2_ws:
        raise RuntimeError("ROS2_WS environment variable is required")

    model_name = LaunchConfiguration("model_name").perform(context)
    world_file = LaunchConfiguration("world_file").perform(context)

    model_dir = os.path.join(ros2_ws, f"src/gazebo_simulator/models/{model_name}")
    xacro_path = os.path.join(model_dir, "urdf", f"{model_name}.xacro")
    world_template_path = os.path.join(ros2_ws, f"src/gazebo_simulator/models/{world_file}")
    os.makedirs(model_dir, exist_ok=True)

    urdf_path = os.path.join(model_dir, f"{model_name}.urdf")
    model_sdf_path = os.path.join(model_dir, "model.sdf")

    with open(urdf_path, "w", encoding="utf-8") as urdf_file:
        subprocess.run(
            ["xacro", xacro_path, f"robot_name:={model_name}"],
            check=True,
            stdout=urdf_file,
        )

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        subprocess.run(["gz", "sdf", "-p", urdf_path], check=True, stdout=sdf_file)

    with open(model_sdf_path, "r", encoding="utf-8") as sdf_file:
        model_sdf = sdf_file.read()

    model_sdf = re.sub(r"model://.*?/meshes/", "meshes/", model_sdf)
    model_sdf = model_sdf.replace("model://meshes/", "meshes/")

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        sdf_file.write(model_sdf)

    config_path = os.path.join(model_dir, "model.config")
    model_config = f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <author>
    <name>Hao</name>
  </author>
  <description>
    Auto-generated model configuration
  </description>
</model>
"""
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write(model_config)

    with open(world_template_path, "r", encoding="utf-8") as template_file:
        world_sdf = template_file.read()

    world_sdf = world_sdf.replace("__MODEL_NAME__", model_name)
    world_file_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        suffix=".sdf",
        prefix=f"{model_name}_world_",
    )
    world_file_handle.write(world_sdf)
    world_file_handle.close()

    robot_description = Command([
        "xacro ",
        xacro_path,
        " robot_name:=",
        model_name,
    ])

    models_path = os.path.join(ros2_ws, "src/gazebo_simulator/models")
    gz_model_path = os.environ.get("GZ_MODEL_PATH", "")
    if gz_model_path:
        gz_model_path = models_path + ":" + gz_model_path
    else:
        gz_model_path = models_path

    gz_plugin_path = os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "")
    if gz_plugin_path:
        gz_plugin_path = gz_plugin_path + ":/opt/ros/jazzy/lib"
    else:
        gz_plugin_path = "/opt/ros/jazzy/lib"

    return [
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_file_handle.name],
            output="screen",
            additional_env={
                "GZ_MODEL_PATH": gz_model_path,
                "GZ_SIM_SYSTEM_PLUGIN_PATH": gz_plugin_path,
            }
        ),
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
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                f'/model/{model_name}/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
            ],
            output='screen'
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager", "/controller_manager"
            ],
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "forward_velocity_controller",
                "--controller-manager", "/controller_manager"
            ],
        ),
        Node(
            package="gazebo_simulator",
            executable="can_to_gazebo",
            parameters=[{'robot_name': model_name}],
            output="screen"
        ),
        
        # # ============================================================
        # # 2. Keyboard Teleop - CAN Command (/can/tx)
        # # ============================================================
        Node(
            package="gazebo_simulator",
            executable="teleop_CANArray_keyboard",
            output="screen",
            prefix="xterm -e"
        ),        

        # ============================================================
        # 3. Keyboard Teleop - Twist Command (/cmd_vel)
        # ============================================================

        # Node(
        #     package="gazebo_simulator",
        #     executable="teleop_twist_keyboard",
        #     output="screen",
        #     prefix="xterm -e"
        # ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "model_name",
            default_value=DEFAULT_MODEL_NAME,
            description="Gazebo model name",
        ),
        DeclareLaunchArgument(
            "world_file",
            default_value=DEFAULT_WORLD_FILE,
            description="World template file inside models/",
        ),
        OpaqueFunction(function=launch_setup),
    ])
