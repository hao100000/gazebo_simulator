from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
import os
import subprocess
import tempfile

MODEL_NAME = "omni_2024"
WORLD_FILE = "world.sdf"
RUNTIME_HOME = "/tmp/gazebo_omni_2024_home"


def launch_setup(context, *args, **kwargs):
    ros2_ws = os.environ.get("ROS2_WS")
    if not ros2_ws:
        raise RuntimeError("ROS2_WS environment variable is required")

    spawn_x = LaunchConfiguration("spawn_x").perform(context)
    spawn_y = LaunchConfiguration("spawn_y").perform(context)
    spawn_z = LaunchConfiguration("spawn_z").perform(context)
    spawn_yaw = LaunchConfiguration("spawn_yaw").perform(context)
    world_path = LaunchConfiguration("world_path").perform(context)

    model_dir = os.path.join(ros2_ws, f"src/gazebo_simulator/models/{MODEL_NAME}")
    xacro_path = os.path.join(model_dir, "urdf", f"{MODEL_NAME}.xacro")
    world_template_path = os.path.join(ros2_ws, f"src/gazebo_simulator/models/{world_path}")
    os.makedirs(model_dir, exist_ok=True)

    urdf_path = os.path.join(model_dir, f"{MODEL_NAME}.urdf")
    model_sdf_path = os.path.join(model_dir, "model.sdf")

    with open(urdf_path, "w", encoding="utf-8") as urdf_file:
        subprocess.run(
            ["xacro", xacro_path],
            check=True,
            stdout=urdf_file,
        )

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        subprocess.run(["gz", "sdf", "-p", urdf_path], check=True, stdout=sdf_file)

    with open(model_sdf_path, "r", encoding="utf-8") as sdf_file:
        model_sdf = sdf_file.read()

    model_sdf = model_sdf.replace("model://meshes/", "meshes/")

    with open(model_sdf_path, "w", encoding="utf-8") as sdf_file:
        sdf_file.write(model_sdf)

    config_path = os.path.join(model_dir, "model.config")
    model_config = f"""<?xml version="1.0"?>
<model>
  <name>{MODEL_NAME}</name>
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

    world_sdf = world_sdf.replace("__MODEL_NAME__", MODEL_NAME)
    world_sdf = world_sdf.replace(
        "<pose>0 0 0.1 0 0 0</pose>",
        f"<pose>{spawn_x} {spawn_y} {spawn_z} 0 0 {spawn_yaw}</pose>",
    )

    world_file_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        suffix=".sdf",
        prefix=f"{MODEL_NAME}_world_",
    )
    world_file_handle.write(world_sdf)
    world_file_handle.close()

    robot_description = Command([
        "xacro ",
        xacro_path,
    ])

    models_path = os.path.join(ros2_ws, "src/gazebo_simulator/models")
    gz_resource_path = os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    if gz_resource_path:
        gz_resource_path = models_path + ":" + gz_resource_path
    else:
        gz_resource_path = models_path

    gz_plugin_path = os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "")
    if gz_plugin_path:
        gz_plugin_path = gz_plugin_path + ":/opt/ros/jazzy/lib"
    else:
        gz_plugin_path = "/opt/ros/jazzy/lib"

    runtime_env = {
        "HOME": RUNTIME_HOME,
        "ROS_HOME": os.path.join(RUNTIME_HOME, ".ros"),
        "XDG_RUNTIME_DIR": os.path.join(RUNTIME_HOME, "runtime"),
        "ROS_LOCALHOST_ONLY": "1",
    }
    os.makedirs(runtime_env["ROS_HOME"], exist_ok=True)
    os.makedirs(runtime_env["XDG_RUNTIME_DIR"], exist_ok=True)

    return [
        ExecuteProcess(
            cmd=["gz", "sim", "-s", "-r", world_file_handle.name],
            output="screen",
            additional_env={
                "GZ_SIM_RESOURCE_PATH": gz_resource_path,
                "GZ_SIM_SYSTEM_PLUGIN_PATH": gz_plugin_path,
                **runtime_env,
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
            ,
            additional_env=runtime_env,
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                f'/model/{MODEL_NAME}/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            ],
            output='screen'
            ,
            additional_env=runtime_env,
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager", "/controller_manager"
            ],
            additional_env=runtime_env,
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "wheel_controller",
                "--controller-manager", "/controller_manager"
            ],
            additional_env=runtime_env,
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "suspension_controller",
                "--controller-manager", "/controller_manager"
            ],
            additional_env=runtime_env,
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "spawn_x",
            default_value="0.0",
            description="Spawn x position",
        ),
        DeclareLaunchArgument(
            "spawn_y",
            default_value="0.0",
            description="Spawn y position",
        ),
        DeclareLaunchArgument(
            "spawn_z",
            default_value="0.0",
            description="Spawn z position",
        ),
        DeclareLaunchArgument(
            "spawn_yaw",
            default_value="0.0",
            description="Spawn yaw",
        ),
        DeclareLaunchArgument(
            "world_path",
            default_value=WORLD_FILE,
            description="World file inside gazebo_simulator/models",
        ),
        OpaqueFunction(function=launch_setup),
    ])
