cmake_minimum_required(VERSION 3.8)
project(gazebo_simulator)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(uec_msgs REQUIRED)

# C++ executable: CAN to Joint Trajectory converter
add_executable(can_to_joint_trajectory_node
  src/can_to_joint_trajectory_node.cpp
)

ament_target_dependencies(can_to_joint_trajectory_node
  rclcpp
  trajectory_msgs
  uec_msgs
)

install(TARGETS can_to_joint_trajectory_node
  DESTINATION lib/${PROJECT_NAME}
)

# Python scripts
install(
  PROGRAMS
    scripts/teleop_twist_keyboard.py
  RENAME teleop_twist_keyboard
  DESTINATION lib/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/teleop_CANArray_keyboard.py
  RENAME teleop_CANArray_keyboard
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

