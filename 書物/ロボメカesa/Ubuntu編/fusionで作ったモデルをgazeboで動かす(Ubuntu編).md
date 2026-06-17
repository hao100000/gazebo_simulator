# Gazebo Simulator の使い方

## もくじ

1. GitHub から [`gazebo_simulator.git`](https://github.com/hao100000/gazebo_simulator.git) を clone して、`ros2_ws/src/` 配下に配置する
2. Fusion で URDF に変換したデータを `gazebo_simulator/models/` に配置する
3. `xterm` をインストールする
4. 必要な ROS / Gazebo 関連パッケージをインストールする
5. Ubuntu のバージョンに合わせて launch ファイルを選ぶ
6. モデル名・コントローラー・モーター設定を変更する
7. build / install を削除して再ビルドする

---

## 1. gazebo_simulator を clone する

```bash
cd ~/ros2_ws/src
git clone https://github.com/hao100000/gazebo_simulator.git
```

---

## 2. Fusion で変換したモデルを配置する

Fusion で URDF に変換したデータを、以下のディレクトリに配置します。

```bash
gazebo_simulator/models/
```

例：

```bash
gazebo_simulator/models/arm_2
```

---

## 3. xterm をインストールする

`xterm` は、launch 時に表示される小さいターミナルのようなものです。

```bash
sudo apt update
sudo apt install xterm
```

---

## 4. 必要なパッケージをインストールする

```bash
sudo apt update
sudo apt install -y ros-humble-ros-gz-bridge ros-humble-gz-ros2-control
```

---

## 5. モデル名を変更する

### `gazebo_simulator/launch/gazebo_22.04.launch.py`

または

### `gazebo_simulator/launch/gazebo_24.04.launch.py`

を編集してください。gazebo_のあとに続く数字は、Ubuntuのバージョン(Ubuntu22.04かUbuntu24.04)です。

12行目あたりの以下の部分を変更します。

```python
DEFAULT_MODEL_NAME = "arm_2"      # モデル名（xacroファイルとモデルディレクトリに対応）
DEFAULT_WORLD_FILE = "world.sdf" # ワールドファイル名
```

`MODEL_NAME` を自分のモデル名に変更してください。

例：

```python
DEFAULT_MODEL_NAME = "arm_2_v10"
DEFAULT_WORLD_FILE = "world.sdf"
```

ワールドファイルを変更したい場合は、`WORLD_FILE` も変更します。

---

## 6. コントローラー設定を変更する(新規のモデルを追加する場合のみ)

### `gazebo_simulator/config/controller_モデル名.yaml`

既存のcontroller_~~~_.yamlをコピペして、ファイル名を`controller_モデル名.yaml`
に変更したあと、19行目あたりの以下の部分を、自分のモデルのジョイント名に合わせて変更します。


```yaml
forward_velocity_controller:
  ros__parameters:
    joints:
      - motor_1
      - motor_2
```

例：

```yaml
forward_velocity_controller:
  ros__parameters:
    joints:
      - motor_1
      - motor_2
      - motor_3
```

---

## 7. モーター設定を変更する(新規のモデルを追加する場合のみ)

### `gazebo_simulator/config/motors_モデル名.yaml`

既存のmotors_~~~_.yamlをコピペして、ファイル名を`motors_モデル名.yaml`
に変更したあと、19行目あたりの以下の部分を、自分のモデルのジョイント名に合わせて変更します。

`can_id` は送信する `bulk_id` に対応します。

```yaml
motors:
  - can_id: 1
    joint_name: motor_1
    invert: false
    control_type: velocity

  - can_id: 2
    joint_name: motor_2
    invert: false
    control_type: velocity
```

例：

```yaml
motors:
  - can_id: 1
    joint_name: motor_1
    invert: false
    control_type: velocity

  - can_id: 2
    joint_name: motor_2
    invert: false
    control_type: velocity

  - can_id: 3
    joint_name: motor_3
    invert: false
    control_type: velocity    
```

---

## 注意事項

設定を変更した後は、`build` と `install` を一度削除してからビルドすることを推奨します。

```bash
cd ~/ros2_ws
rm -rf build install
cb
```

---

## 8. Ubuntu のバージョンに合わせて launch ファイルを使う

Ubuntu 22.04 の場合：

```bash
ros2 launch gazebo_simulator gazebo_22.04.launch.py
```

Ubuntu 24.04 の場合：

```bash
ros2 launch gazebo_simulator gazebo_24.04.launch.py
```

まずはarm_2_v10を動かすことを推奨。
xtermウィンドウを選択して、英語入力でqweキーを押したらモーターが回転、zxcキーを押したらモーターが回転、asdキーを押したらモーターが停止することを確認できたら成功です。