# 注意事項
- このプログラムは、このfusion2urdfを少し修正したものです。
- 参考資料は[これ](https://qiita.com/sfc_nakanishi_lab/items/83c10533e3eadd7cac56)

# 大まかな流れ
### 機構班のしごと(Windousなど)
- [GitHub](https://github.com/hao100000/fusion2urdf.git)からfusion2urdfというアドインをダウンロード
- アドインをFusionの中にコピー
- 3Dモデルを作る
- URDF形式に変換
### 制御班のしごと(Ubuntu)
- 機構班から渡されたものは.xacroという形式なので、.urdfに変換
- gazeboが読み取れる形式にファイルを配置
- launchファイルやコントローラーを調整

# 機構班のしごと
## fusion2urdfをダウンロード
- [GitHub](https://github.com/hao100000/fusion2urdf.git)からダウンロード。がんばって。

## アドインをFusionの中にコピー

続けて、「URDF_Exporter」をFusion360のAPIにコピーする。  
Mac OSの場合
```
cp -r ./URDF_Exporter "$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/" 
```
Windows OSの場合、PowerShellとか使って
```
Copy-Item ".\URDF_Exporter\" -Destination "${env:APPDATA}\Autodesk\Autodesk Fusion 360\API\Scripts\" -Recurse
```
みたいな感じのコマンドで。

## 3Dモデルを作る
以下の事に注意してね。
- モデルは地面に固定しない。
- どれでもいいんだけど、なんとなく基幹となりそうなコンポーネントを「base_link」と名付ける。
- ジョイントするときは、base_linkじゃないやつ→base_linkの順でクリックしてジョイントする。
- ジョイントの名前はmotor_1, motor_2, ,,, と命名する。

## URDF形式に変換
- Fusion360の「ユーティリティ」→「アドイン(スクリプトとアドイン)」→「URDF_Exporter」の隣のセルの再生ボタンみたいなボタンを押す。  
- ROS1とROS2を選ぶウィンドウ(めちゃ小さい)がでるので、いい感じにウィンドウを大きくして、ROS2を選択  
- エクスポート先のフォルダをお好みで選択  
- errorが出た場合は、エラーメッセージに従う。チャッピーとか制御班とか使ってがんばって。  
- successした場合は、「モデル名_description」というフォルダにxacroファイルなどが入っていることを確認する


# 制御班のしごと



# 僕がfusion2urdfに施した修正
## core/Joint.pyを編集
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