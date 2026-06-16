from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from ament_index_python.packages import PackageNotFoundError, get_package_prefix
import os
import re
import subprocess
import tempfile

# ============================================================
# Ubuntu 22.04 / ROS 2 Humble / Gazebo Sim 6 (ign gazebo)
# ============================================================
DEFAULT_MODEL_NAME = "arm_1"
DEFAULT_WORLD_FILE = "world.sdf"


def require_ros_package(package_name: str, apt_name: str):
    try:
        return get_package_prefix(package_name)
    except PackageNotFoundError as exc:
        raise RuntimeError(
            f"{package_name} is required for gazebo_22.04.launch.py. "
            f"Install it with: sudo apt install {apt_name}"
        ) from exc


def append_env_paths(current_value: str, paths):
    values = [path for path in current_value.split(os.pathsep) if path]
    for path in paths:
        if path and os.path.isdir(path) and path not in values:
            values.append(path)
    return os.pathsep.join(values)


def resolve_ros2_ws(ros2_ws: str):
    expanded_path = os.path.expanduser(ros2_ws)
    candidates = [expanded_path] if os.path.isabs(expanded_path) else [
        os.path.join(os.path.expanduser("~"), expanded_path),
        os.path.abspath(expanded_path),
    ]
    package_marker = os.path.join("src", "gazebo_simulator", "package.xml")
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, package_marker)):
            return os.path.realpath(candidate)

    return os.path.realpath(candidates[0])


def build_world_sdf(ros2_ws: str, model_name: str, world_file: str):
    world_template_path = os.path.join(
        ros2_ws,
        f"src/gazebo_simulator/models/{world_file}",
    )
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
    return world_file_handle.name


def regenerate_model_sdf(ros2_ws: str, model_name: str):
    model_dir = os.path.join(ros2_ws, f"src/gazebo_simulator/models/{model_name}")
    xacro_path = os.path.join(model_dir, "urdf", f"{model_name}.xacro")
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
        subprocess.run(["ign", "sdf", "-p", urdf_path], check=True, stdout=sdf_file)

    with open(model_sdf_path, "r", encoding="utf-8") as sdf_file:
        model_sdf = sdf_file.read()

    model_sdf = re.sub(r"model://.*?/meshes/", "meshes/", model_sdf)
    model_sdf = model_sdf.replace("model://meshes/", "meshes/")
    model_sdf = model_sdf.replace(
        "libgz-sim-pose-publisher-system.so",
        "libignition-gazebo-pose-publisher-system.so",
    )
    model_sdf = model_sdf.replace(
        "gz::sim::systems::PosePublisher",
        "ignition::gazebo::systems::PosePublisher",
    )

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


def launch_setup(context, *args, **kwargs):
    ros2_ws = os.environ.get("ROS2_WS")
    if not ros2_ws:
        raise RuntimeError("ROS2_WS environment variable is required")
    ros2_ws = resolve_ros2_ws(ros2_ws)

    ros_gz_bridge_prefix = require_ros_package(
        "ros_gz_bridge",
        "ros-humble-ros-gz-bridge",
    )
    gz_ros2_control_prefix = require_ros_package(
        "gz_ros2_control",
        "ros-humble-gz-ros2-control",
    )

    model_name = LaunchConfiguration("model_name").perform(context)
    world_file = LaunchConfiguration("world_file").perform(context)
    common_env = {"ROS2_WS": ros2_ws}

    regenerate_model_sdf(ros2_ws, model_name)
    world_path = build_world_sdf(ros2_ws, model_name, world_file)

    robot_description = Command([
        "xacro ",
        os.path.join(
            ros2_ws,
            f"src/gazebo_simulator/models/{model_name}/urdf/{model_name}.xacro",
        ),
        " robot_name:=",
        model_name,
    ])

    models_path = os.path.join(ros2_ws, "src/gazebo_simulator/models")
    resource_path = append_env_paths(
        os.environ.get("IGN_GAZEBO_RESOURCE_PATH", ""),
        [models_path],
    )
    plugin_path = append_env_paths(
        os.environ.get("IGN_GAZEBO_SYSTEM_PLUGIN_PATH", ""),
        [
            "/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins",
            os.path.join(ros_gz_bridge_prefix, "lib"),
            os.path.join(gz_ros2_control_prefix, "lib"),
        ],
    )

    return [
        ExecuteProcess(
            cmd=["ign", "gazebo", "-r", world_path],
            output="screen",
            additional_env={
                **common_env,
                "IGN_GAZEBO_RESOURCE_PATH": resource_path,
                "IGN_GAZEBO_SYSTEM_PLUGIN_PATH": plugin_path,
            },
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{
                "robot_description": robot_description,
                "use_sim_time": True,
            }],
            output="screen",
            additional_env=common_env,
        ),
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                f"/model/{model_name}/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            ],
            output="screen",
            additional_env=common_env,
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager", "/controller_manager",
            ],
            additional_env=common_env,
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "forward_velocity_controller",
                "--controller-manager", "/controller_manager",
            ],
            additional_env=common_env,
        ),
        Node(
            package="gazebo_simulator",
            executable="can_to_gazebo",
            parameters=[{"robot_name": model_name}],
            output="screen",
            additional_env=common_env,
        ),
        Node(
            package="gazebo_simulator",
            executable="teleop_CANArray_keyboard",
            output="screen",
            prefix="xterm -e",
            condition=IfCondition(LaunchConfiguration("enable_teleop")),
            additional_env=common_env,
        ),
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
        DeclareLaunchArgument(
            "enable_teleop",
            default_value="true",
            description="Start keyboard teleop in xterm",
        ),
        OpaqueFunction(function=launch_setup),
    ])
