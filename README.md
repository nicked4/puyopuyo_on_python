# Implement puyopuyo on python.  

## For my master research.  

I research deep reinforcement learning as a master student.  
My research theme is applying RL for puyopuyo to create strong game AI.  
I develop with python, so I had to implement puyopuyo simulator on python.  

This program has tokoton puyopuyo mode only(for one person).  
So, I should implement battle mode sometime.  
Special library used on this program is pygame only.  

| File name | Use |
|---|---|
| **puyo_class.py** | Super class of following 3 files |
| **puyo_environment.py** | For play |
| **puyo_simulator.py** | Simulator specialized for experiment |
| **puyo_AIplay.py** | Demonstration by AI |

## Explanation about "puyo_simulator.py" operation
| Method | Operation |
|---|---|
| **get_state** | Get field and tsumo states |
| **rl_step(num)** | Command agent to act in response to the num |
| **random_action** | Command agent to act randomly |

![puyoAIdemo200116gif](https://user-images.githubusercontent.com/51912962/74588418-a9ca7180-503f-11ea-9864-b0723a8152b7.gif)

# python上でのぷよぷよ開発

## 修士研究用のプログラムです

私は修士研究のテーマとして、ぷよぷよに深層強化学習を応用して強いAIをつくる、といったことを扱っている。  
開発はpythonで行っているため、pythonでぷよぷよのシミュレータを作成する必要があった（それ以外の方法もあるが）。  

このプログラムは一人用モードのとことんぷよぷよのみしか実装していない。  
いずれは対戦なども見据えているため、そちらの開発もする必要がある。  
しかし、まずは一人用で強いAIができることが大前提のため、そちらの方は追々の実装になる。  
このプログラムで用いている特別なライブラリはpygameくらいである。  

| ファイル名 | 用途 |
|---|---|
| **puyo_class.py** | 次の3つのファイルのスーパークラス |
| **puyo_environment.py** | ゲームをプレーできるクラス |
| **puyo_simulator.py** | 学習に用いるシミュレータ |
| **puyo_AIplay.py** | AIによるデモンストレーション |
 
 ## "puyo_simulator.py"の操作方法についての説明
| メソッド | 動作 |
|---|---|
| **get_state** | フィールドとツモの状態を取得する |
| **rl_step(num)** | numの値に応じた行動をAgentに行わせる |
| **random_action** | ランダムな行動をAgentに行わせる |
