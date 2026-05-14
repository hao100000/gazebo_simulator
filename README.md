- gazebo起動コマンド
    - gz sim -r ~/Ubuntu_3/Private/simulator/ros2_ws/src/models/world.sdf

- teletop(キーボードから/cmd_velをpublish)を起動するコマンド
    - ros2 run gazebo_simulator teleop_twist_keyboard

- /cmd_velをgazebo用に変換するノードを起動するコマンド
    - ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist

- 上記3つをいっぺんにlaunchして起動するコマンド
    -  ros2 launch gazebo_simulator gazebo.launch.py


    今のmoveBindings{}を、(動くモーターの種類, スピード)っていうふうに変更してほしい。
キーボード配列に沿って、q,w,e,r,t,y,u,i,o,pが押されたら1,2,3,4,5,6,7,8,9,10番のモーターが+の方向に動くようにしてほしい。

z,x,c,v,b,n,m,「,」,.,/が押されたら1,2,3,4,5,6,7,8,9,10番のモーターが-の方向に動くようにしてほしい。