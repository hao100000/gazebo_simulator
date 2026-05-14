cmake_minimum_required(VERSION 3.8)
project(gazebo_simulator)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 依存パッケージを検索
find_package(ament_cmake REQUIRED)
# 以下のセクションを有効化すると、
# 追加の依存パッケージを手動で指定できます。
# find_package(<dependency> REQUIRED)


# Python ノードをインストール
# ament_python_install_package(${PROJECT_NAME})

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
  PROGRAMS
    scripts/can_to_joint_velocity.py
  RENAME can_to_joint_velocity
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # 以下の行は著作権チェック用リンターをスキップします
  # すべてのソースに著作権・ライセンス表記を追加したらコメントアウトしてください
  set(ament_cmake_copyright_FOUND TRUE)
  # 以下の行は cpplint をスキップします（git リポジトリ内でのみ有効）
  # このパッケージを git 管理し、かつ
  # すべてのソースに著作権・ライセンス表記を追加したらコメントアウトしてください
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
