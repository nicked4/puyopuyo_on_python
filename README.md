# Implement puyopuyo on python.  

## For my master research.  

I research deep reinforcement learning as a master student.  
My research theme is applying RL for puyopuyo to create strong game AI.  
I develop with python, so I had to implement puyopuyo simulator on python.  

This program has tokoton puyopuyo mode only(for one person).  
So, I should implement battle mode sometime.  
Special library used on this program is pygame only.  

| File name | use |
|---|---|
| **puyo_class.py** | super class of following 3 files |
| **puyo_environment.py** | for play |
| **puyo_simulator.py** | simulator specialized for experiment |
| **puyo_AIplay.py** | demonstration by AI |

![puyoAIdemo200116gif](https://user-images.githubusercontent.com/51912962/74588418-a9ca7180-503f-11ea-9864-b0723a8152b7.gif)

# python上でのぷよぷよ開発

## 修士研究用のプログラムです

私は修士研究のテーマとして、ぷよぷよに深層強化学習を応用して強いAIをつくる、といったことを扱っています。  
開発はpythonで行っているため、pythonでぷよぷよのシミュレータを作成する必要がありました（それ以外の方法もありますが）。  

このプログラムは一人用モードのとことんぷよぷよのみしか実装していません。  
いずれは対戦なども見据えているため、そちらの開発もする必要があります。  
しかし、まずは一人用で強いAIができることが大前提のため、そちらの方は追々の実装になります。  
このプログラムで用いている特別なライブラリはpygameくらいです。  

| ファイル名| 使用する|
| --- | ---- |
| ** puyo_class.py ** | 次の3つのファイルのスーパークラス |
| ** puyo_environment.py ** | ゲームをプレーできるクラス |
| ** puyo_simulator.py ** | 学習に用いるシミュレータ |
| ** puyo_AIplay.py ** | AIによるデモンストレーション |
