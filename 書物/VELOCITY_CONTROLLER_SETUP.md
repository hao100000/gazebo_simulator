# JointGroupVelocityController セットアップ

## 概要
ros2_control の **JointGroupVelocityController** を使用した、シンプルで軽量な制御システムに変更しました。

## アーキテクチャ

```
CANArray Topic (/can/tx)
    ↓
[can_to_gazebo (C++)]  ← CANArrayをFloat64MultiArrayに変換
    ↓
Float64MultiArray Topic (/forward_velocity_controller/commands)
    ↓
[JointGroupVelocityController] ← ros2_control standard controller
    ↓
Gazebo (joint velocity commands)
    ↓
[demoRobot] wheel_left_joint, wheel_right_joint 回転
```

## 変更内容

### 1. can_to_gazebo ノード (C++)
- **ファイル**: `src/can_to_gazebo.cpp`
- **ヘッダ**: `include/gazebo_simulator/can_to_gazebo.hpp`
- CANArray → Float64MultiArray 変換
- motor_id: 1=左輪, 2=右輪
- **トピック**:
  - IN: `/can/tx` (uec_msgs/CANArray)
  - OUT: `/forward_velocity_controller/commands` (std_msgs/Float64MultiArray)

### 2. controller_config.yaml
```yaml
controller_manager:
  forward_velocity_controller:
    type: velocity_controllers/JointGroupVelocityController

forward_velocity_controller:
  joints: [wheel_left_joint, wheel_right_joint]
```

### 3. demorobot.urdf.xacro
- ros2_control セクション削除（URDF simplify）
- gazebo_ros2_control プラグイン削除
- Joint定義のみ残す（velocity limits設定済み）

### 4. world.sdf
- gazebo_ros2_control プラグイン削除
- JointController プラグイン復活（シンプル実装）

### 5. launch ファイル
- **新規**: `launch/gazebo_sim.launch.py`
- 起動順序:
  1. Gazebo
  2. Controller Manager
  3. Joint State Broadcaster
  4. Forward Velocity Controller
  5. CAN to Gazebo Converter

## 使用方法

### 起動
```bash
source ~/.bashrc
cd ~/Ubuntu_3/Private/simulator/ros2_ws
source install/setup.bash
export ROS2_WS=$PWD

ros2 launch gazebo_simulator gazebo_sim.launch.py
```

### テスト
別ターミナルで CANArray メッセージ送信：

```bash
# 左輪を 2 rad/s
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 1, data: [2.0]}]}'

# 右輪を 2 rad/s  
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 2, data: [2.0]}]}'

# 両輪 2 rad/s
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 1, data: [2.0]}, {id: 0, bulk_id: 2, data: [2.0]}]}'
```

### ジョイント状態確認
```bash
ros2 topic echo /joint_states
```

### コントローラ状態確認
```bash
ros2 control list_controllers
```

## ファイル構成
```
gazebo_simulator/
├── CMakeLists.txt (更新: std_msgs, include ディレクトリ)
├── config/
│   └── controller_config.yaml (JointGroupVelocityController設定)
├── include/
│   └── gazebo_simulator/
│       └── can_to_gazebo.hpp (新規)
├── src/
│   └── can_to_gazebo.cpp (新規)
└── launch/
    └── gazebo_sim.launch.py (新規)
```

## メリット

✅ **gazebo_ros2_control プラグイン不要** - システム依存少ない
✅ **軽量** - 必要最小限のセットアップ
✅ **JointGroupVelocityController は標準** - 安定・信頼性高い
✅ **実機対応容易** - 同じコントローラを実機でも使用可能

## トラブルシューティング

### Forward Velocity Controller が起動しない
```bash
ros2 control list_controllers
# forward_velocity_controller が "inactive" の場合:
ros2 control set_controller_state forward_velocity_controller active
```

### CANArray が反応しない
```bash
ros2 topic echo /can/tx  # CANメッセージが流れているか確認
ros2 node list | grep can_to_gazebo  # ノードが起動しているか確認
ros2 topic echo /forward_velocity_controller/commands  # 出力を確認
```

### Gazebo が起動しない
```bash
echo $ROS2_WS
ls src/models/world.sdf  # ファイルが存在するか確認
```
