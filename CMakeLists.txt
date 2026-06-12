cmake_minimum_required(VERSION 3.8)
project(gazebo_simulator)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2_msgs REQUIRED)
find_package(uec_msgs REQUIRED)
find_package(yaml-cpp REQUIRED)

# include ディレクトリ
include_directories(include)

# C++ executable: CAN to Joint Trajectory converter
add_executable(can_to_gazebo
  src/can_to_gazebo.cpp
)

ament_target_dependencies(can_to_gazebo
  rclcpp
  std_msgs
  uec_msgs
)

target_link_libraries(can_to_gazebo yaml-cpp)

# C++ executable: extract robot body pose from TF stream
add_executable(gazebo_to_uodom
  src/gazebo_to_uodom.cpp
)

ament_target_dependencies(gazebo_to_uodom
  rclcpp
  tf2_msgs
  uec_msgs
)


install(TARGETS can_to_gazebo
  gazebo_to_uodom
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
  DIRECTORY models
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY include
  DESTINATION include
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
