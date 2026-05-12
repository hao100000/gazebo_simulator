- gazebo起動コマンド
    - gz sim -r ~/Ubuntu_3/Private/simulator/ros2_ws/src/models/world.sdf

- teletop(キーボードから/cmd_velをpublish)を起動するコマンド
    - ros2 run gazebo_simulator teleop_twist_keyboard

- /cmd_velをgazebo用に変換するノードを起動するコマンド
    - ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist

- 上記3つをいっぺんにlaunchして起動するコマンド
    -  ros2 launch gazebo_simulator gazebo.launch.py