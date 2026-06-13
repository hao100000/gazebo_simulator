# 大まかな流れ
### Windousでやること(Macも可)
1. Fusionで3Dモデルを作る
1. 3Dモデルのデータの重さを評価する
1. [GitHub](https://github.com/hao100000/fusion2urdf.git)からfusion2urdfというアドインをダウンロード
1. アドインをFusionのAPIにコピー
1. URDF形式に変換
1. Ubuntuに送信
### Ubuntuでやること
1. Windousで出力したものは.xacroという形式なので、.urdfに変換
1. gazeboが読み取れる形式にファイルを配置
1. launchファイルやコントローラーを調整

## 前提知識
- Gazebo = シミュレーションソフトの名前。
- アドイン = もともとあるプログラムを改良するプログラム。マイクラのMODみたいやつ。
- URDF = Gazeboが扱えるファイル形式の名前。fusionの形式そのままだとGazeboは扱えないから、URDFという形式に変換してほしい。
- コンポーネント = fusionで作る1つの物体の名前?(たぶん)
- link = コンポーネントのこと。Gazeboではコンポーネントのことをlinkという。
- joint = linkどうしを接続するやつ。Gazeboでは、このJointの角度とか速度を指定して動かす。

# Windousでやること
## Fusionで3Dモデルを作る
注意すべきポイントは**地面の存在**、**命名規則**、**ジョイントの構成**、**データ量**です。

### 地面の存在
Fusionではモデルが自動で地面の上に自立しますが、Gazeboでは自立してくれません。なので自分で地面を作って、地面とジョイントさせながらモデルを構築しましょう。

### 命名規則
- Gazeboは日本語厳禁です。文字化けしてエラーの原因になります。コンポーネントもジョイントもファイル名も、全て英語でお願いします。
- コンポーネント名は英語なら自由なのですが、どれか1つはbase_linkという名前にしてください。Gazeboはこのbase_linkを基準にモデルを構築します。個人的には地面の名前をbase_linkとするのを推奨します。
- ジョイントの名前はmotor_1, motor_2, ,,, と命名することをおすすめします。

### ジョイントの構成
Fusion2URDF では、ジョイントの順番が重要です。
そのため、ジョイントは次のように根元から先端へ向かうツリー構造になるように作成してください。
```
base_link
└─ arm_link_1
   └─ arm_link_2
      └─ arm_link_3
```
また、ジョイントするとき

## 3Dモデルの重さを評価する
- URDFに変換するとき、3Dモデルは大量の三角形(ポリゴン)をはって表示するらしい。
- このポリゴンが多すぎるとPCのGPUの処理能力を超えてしまうので、なるべく抽象化して軽いモデルの作成をお願いします。
- ポリゴンの多さの目安は以下の通り  

| ポリゴン数           | 評価   |
| -------------- | ---- |
| ～5,000         | 軽い   |
| 5,000～20,000   | 普通   |
| 20,000～100,000 | やや重い |
| 100,000以上      | 重い   |

- ちなみに、2025F³RCのAチームの足回りのポリゴン数は120万でした(！？！？！？！？！？)
- さすがにこれはGazeboが起動しませんでした。なるべく抽象化して、軽めのモデルの作成をお願いします。
### 評価のやりかた
- 次にやり方を説明します。普段のfusionのデータだとそもそもポリゴンという概念がないので、
    - FusionデータをSTLに変換して保存
    - 保存したSTLをFusionで開く
    - モデルを右クリック。(すべてのコンポーネントがひとまとまりになってます。)
    - プロパティ>メッシュを開く
- というようにしてポリゴン数を調べてください。「ファセットの数」っていうのがポリゴン数です。  
- 複数のSTLを組み合わせてジョイントの情報を加えたものがURDFです。(補足)(たぶん)
- 以下に画面遷移のスクショ置いときます。

### 画面遷移
- FusionデータをSTLに変換して保存
![](size_1.png)
![](size_2.png)

- 保存したSTLをFusionで開く
![](size_3.png)
![](size_4.png)
![](size_5.png)

- モデルを右クリック。
![](size_6.png)

- プロパティのメッシュの中の「ファセットの数」がポリゴン数
![](size_7.png)
![](size_8.png)
- 狂気のポリゴン数120万
![](size_9.png)

## fusion2urdfをダウンロード
- [GitHub](https://github.com/hao100000/fusion2urdf.git)にアクセス。
- Code>Download Zipでダウンロード(ほかのやり方でも可)
![12](fusion2urdf_12.png)

- お好みのフォルダで展開。以下のような画面になってればOK
![13](fusion2urdf_13.png)


## アドインをFusionのAPIにコピー
- 「URDF_Exporter」をコピーする。「fusion2urdf」ではないことに注意。  
- 表示>表示>隠しファイル にチェックをつける。(こうしないと次に出てくるAppDataが表示されない)
- PC/Windous/ユーザー/「ご自分のユーザー名」/AppData/Roaming/Autodesk/Autodesk/Fusion 360/API/Scripts/まで移動して「URDF_Expoter」を張り付ける。
### 画面遷移
- 「URDF_Exporter」をコピーする。「fusion2urdf」ではないことに注意。  
- PC>Windousに移動
![14](fusion2urdf_14.png)
- 表示>表示>隠しファイル にチェックをつける。
- PC/Windous/ユーザー/「ご自分のユーザー名」/AppData/Roaming/Autodesk/Autodesk/Fusion 360/API/Scripts/まで移動して「URDF_Expoter」を張り付ける。
![15](fusion2urdf_15.png)
- こういう画面になってたらOK
![16](fusion2urdf_16.png)

## URDF形式に変換
- Fusion360の「ユーティリティ>アドイン(スクリプトとアドイン)>URDF_Exporter」の隣のセルの再生ボタンみたいなボタンを押す。  
- エクスポート先のフォルダをお好みで選択。  
- ROS1とROS2を選ぶウィンドウ(めちゃ小さい)がでるので、いい感じにウィンドウを大きくして、ROS2を選択  
- successした場合は、「モデル名/urdf」というフォルダにモデル名.xacroファイルが入ってたり「モデル名/meshes」というフォルダにコンポーネント名.stlみたいなファイルが入ってることを確認する。
- うまくいかない場合は、「ファイルボタンの右の小さい三角>表示>テキストコマンドを表示」でエラーメッセージを表示させて、解読するなりチャッピーにエラーメッセージ投げるなりしてエラーを解決する。
- ↑この説明きいてもよくわからんという場合は以下の画像たちを参照
### 画面遷移
- Fusion360の「ユーティリティ」→「アドイン(スクリプトとアドイン)」→「URDF_Exporter」の隣のセルの再生ボタンみたいなボタンを押す。
![1](fusion2urdf_1.png)
![2](fusion2urdf_2.png)
![3](fusion2urdf_3.png)
- エクスポート先のフォルダをお好みで選択。
![4](fusion2urdf_4.png)
- ROS1とROS2を選ぶウィンドウ(めちゃ小さい)がでるので、いい感じにウィンドウを大きくして、ROS2を選択  
![5](fusion2urdf_5.png)
![6](fusion2urdf_6.png)
- 変換が成功したらこういう画面になる。OKを押す。
![7](fusion2urdf_7.png)

- 一応確認として、「モデル名/urdf」というフォルダにモデル名.xacroファイルが入ってたり「モデル名/meshes」というフォルダにコンポーネント名.stlみたいなファイルが入ってることを確認する。以下のような感じになってたらOK
![17](fusion2urdf_17.png)
![18](fusion2urdf_18.png)

- たまにこういうエラー画面になる。解読するなりチャッピーにエラーメッセージ投げるなりしてエラーを解決する。
![10](fusion2urdf_10.png)
- 正しく操作したはずなのにうまくいかなくて、エラーメッセージも出ない場合は以下のようにしたらエラーメッセージを出せる場合がある。「ファイルボタンの右の小さい三角>表示>テキストコマンドを表示」でエラーを表示。エラーメッセージ出たら解読して頑張って解決する。
![8](fusion2urdf_8.png)
![9](fusion2urdf_9.png)

## Ubuntuを使う人に送信
- お疲れさまでした。これでWindousでやる操作は終了です。
- 最後に、Ubuntuを使う人にこのデータを送信しましょう。
- 送信できればなんでもいいのですが、Google Driveを使うのを推奨しときます。
- ギガファイル便は推奨しません。フォルダとして送ることができないので。
- ドライブにフォルダごとアップロードして権限変更したあとURLをUbuntuを操作する人に送りましょう。

### 画面遷移
いちおう画面遷移も置いときます。
![](drive_1.png)
![](drive_2.png)
![](drive_3.png)
![](drive_4.png)
![](drive_5.png)
![](drive_6.png)
![](drive_7.png)


# Ubuntuでやること



# 僕がfusion2urdfに施した修正
## URDF_Exporter/core/Joint.pyを編集
- make_joints_dict()関数の前に以下の関数を追加  


```python  
def normalize(name):
    name = re.sub('[ :()]', '_', name)

    if 'base_link' in name:
        return 'base_link'

    return name
```

- make_joints_dict()関数の最後のreturnの直前の

```python
joints_dict[joint.name] = joint_dict
```

を

```python
parent_occ = get_parent(joint.occurrenceTwo)
child_occ  = get_parent(joint.occurrenceOne)

joint_dict['parent'] = normalize(parent_occ.name)
joint_dict['child']  = normalize(child_occ.name)

joints_dict[joint.name] = joint_dict
```

に変更。ネストの深さがそろうように注意してね。

# 参考文献
- 参考資料は[これ](https://qiita.com/sfc_nakanishi_lab/items/83c10533e3eadd7cac56)