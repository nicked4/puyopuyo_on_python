# Implement puyopuyo on python.  

## For my master research.  

I research deep reinforcement learning as a master student.  
My research theme is applying RL for puyopuyo to create strong game AI.  
I develop with python, so I had to implement puyopuyo simulator on python.  

This program has tokoton puyopuyo mode only(for one person).  
So, I should implement battle mode sometime.  
**puyo_environment.py** is for play.  
**puyo_simulator.py** is specialized for experiment instead of puyo_environment.py.  
Special library used on this program is pygame only.  



# python上でのぷよぷよ開発

## 修士研究用のプログラムです

私は修士研究のテーマとして、ぷよぷよに深層強化学習を応用して強いAIをつくる、といったことを扱っています。  
開発はpythonで行っているため、pythonでぷよぷよのシミュレータを作成する必要がありました（それ以外の方法もありますが）。  

このプログラムは一人用モードのとことんぷよぷよのみしか実装していません。  
いずれは対戦なども見据えているため、そちらの開発もする必要があります。  
しかし、まずは一人用で強いAIができることが大前提のため、そちらの方は追々の実装になります。  
**puyo_environment.py**がゲームプレーをするファイル、**puyo_simulator.py**が学習の際に用いるシミュレータ、**puyo_class.py**はそれぞれのスーパークラスです。  
ちなみに、このプログラムで用いている特別なライブラリはpygameくらいです。  

