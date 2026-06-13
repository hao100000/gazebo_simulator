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