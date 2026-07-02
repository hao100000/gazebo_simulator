# ros2_control セットアップ完了

## 概要
ros2_control フレームワークに完全に移行しました。
CANArray メッセージの処理は C++ で実装され、ros2_control コントローラへの変換を行います。

## 実装内容

### 1. URDF ファイル
- **ファイル**: `urdf/demorobot.urdf.xacro`
- **内容**:
  - ロボット全体の構造定義（base_link, wheels, casters）
  - ros2_control プラグイン設定
  - wheel_left_joint, wheel_right_joint の velocity コマンドインターフェース設定

### 2. C++ 変換ノード
- **ファイル**: `src/can_to_joint_trajectory_node.cpp`
- **機能**:
  - `/can/tx` (CANArray) をサブスクライブ
  - motor_id を joint 名に変換:
    - motor_id=1 → wheel_left_joint
    - motor_id=2 → wheel_right_joint
  - JointTrajectoryコマンドに変換して publish
  - トピック: `/demorobot_joint_trajectory_controller/commands`

### 3. ros2_control コントローラ設定
- **ファイル**: `config/controller_config.yaml`
- **内容**:
  - `joint_trajectory_controller`: wheel joints を制御
  - `joint_state_broadcaster`: joint 状態を配信

### 4. Gazebo 統合
- **ファイル**: `src/models/world_ros2control.sdf`
- **プラグイン**: `gazebo_ros2_control::GazeboRos2ControlPlugin`
- **機能**: Gazebo と ros2_control を連結

### 5. Launch ファイル
- **ファイル**: `launch/gazebo_ros2_control.launch.py`
- **起動順序**:
  1. Gazebo (world_ros2control.sdf)
  2. Controller Manager
  3. Joint State Broadcaster
  4. Joint Trajectory Controller
  5. CAN to JointTrajectory Converter（C++）
  6. Teleop（オプション）

## 使用方法

### 環境設定
```bash
cd ~/Ubuntu_3/Private/simulator/ros2_ws
source install/setup.bash
export ROS2_WS=$PWD
```

### シミュレーション実行
```bash
ros2 launch gazebo_simulator gazebo_ros2_control.launch.py
```

### CANArray メッセージ送信テスト
別ターミナルで：
```bash
# 左輪を5 rad/s で回転
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 1, data: [5.0]}]}'

# 右輪を5 rad/s で回転
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 2, data: [5.0]}]}'

# 両輪同時に3 rad/s
ros2 topic pub /can/tx uec_msgs/CANArray '{array: [{id: 0, bulk_id: 1, data: [3.0]}, {id: 0, bulk_id: 2, data: [3.0]}]}'
```

### キーボード操作テスト
xterm がインストールされている場合、launch ファイルで自動起動されます。
- `q`: motor1（左輪）速度+1.0
- `z`: motor1（左輪）速度-1.0
- `w`: motor2（右輪）速度+1.0
- `x`: motor2（右輪）速度-1.0

### ジョイント状態確認
```bash
ros2 topic echo /joint_states
```

## ファイル構成
```
gazebo_simulator/
├── CMakeLists.txt          ← C++ビルド設定
├── package.xml             ← 依存パッケージ定義
├── config/
│   └── controller_config.yaml
├── src/
│   └── can_to_joint_trajectory_node.cpp
├── urdf/
│   └── demorobot.urdf.xacro
└── launch/
    ├── gazebo_ros2_control.launch.py (新規)
    └── ...（他の launch ファイル）
```

## 実機との統合について
ros2_control フレームワークを使用しているため、以下が簡単になります：
1. 実機の hardware plugin を作成（実機の sensor/actuator I/O）
2. URDF の ros2_control セクションを実機用に変更
3. コントローラ設定（controller_config.yaml）は共通利用可能
4. アプリケーション層は変更不要

## トラブルシューティング

### Gazebo が起動しない場合
```bash
# world_ros2control.sdf が正しく見つかるか確認
echo $ROS2_WS
ls src/models/world_ros2control.sdf
```

### Controller Manager が接続できない場合
```bash
# controller_manager が起動しているか確認
ros2 node list | grep controller_manager

# コントローラ状態確認
ros2 service list | grep list_controllers
```

### JointTrajectory コマンドが反応しない場合
```bash
# C++ ノードが起動しているか確認
ros2 node list | grep can_to_joint_trajectory

# CAN メッセージが送信されているか確認
ros2 topic echo /can/tx
```
