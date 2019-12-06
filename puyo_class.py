import numpy as np
from abc import ABCMeta
from abc import abstractmethod

"""
ぷよぷよのプレー用、学習用、AIデモ用のスーパークラス
それぞれにおいて必要な根幹となる部分を記述
これを継承して、必要な部分を追々記述する
"""

WIDTH = 6
HEIGHT = 13


class PuyoSuper(metaclass=ABCMeta):
    def __init__(self):
        # axisは回転の軸となるぷよ、rotateは回転するぷよ
        self.x_axis = 0
        self.y_axis = 0
        self.x_rotate = 0
        self.y_rotate = 0
        self.color_axis = 0
        self.color_rotate = 0

        # ネクスト、ネクネクの色
        self.color_axis_next = 0
        self.color_rotate_next = 0
        self.color_axis_nexnex = 0
        self.color_rotate_nexnex = 0

        # ゲーム部分と制御用変数
        self.step = 0
        self.field = []
        self.field_np = np.zeros((WIDTH + 2, HEIGHT + 2), dtype=int)
        self.reset_field()
        self.droptime = 0
        self.rotate_time = 0
        self.move_time = 0

        # 発火判定やスコア計算に用いる
        self.fire_flaged_puyo = []
        self.link_is_counted = []
        self.link_counter = 0
        self.link_bonus_sum = 0
        self.chain_number = 0
        self.color_list = []
        self.color_delete = 0
        self.deleted_puyo_number = 0
        self.all_clear_flag = False
        self.score = 0
        self.score_current = 0
        self.score_turn = 0

        # 発火と落下時の挙動（連鎖の過程を見せるための制御）
        self.fire_counter = 0
        self.fire_step = 0
        self.fall_counter = 0
        self.set_end = False
        self.gameover = False

    # ゲーム開始時のリセット
    def reset(self, seed=False):
        # シードの設定（デフォルトでは時間をシードにする）
        if seed:
            np.random.seed(seed=seed)

        # ツモしたぷよを指定した位置に配置
        self.x_axis = 3
        self.y_axis = 2
        self.x_rotate = 3
        self.y_rotate = 1
        self.color_axis = 0
        self.color_rotate = 0

        # ランダムなツモ
        self.color_axis_next = np.random.randint(1, 5)
        self.color_rotate_next = np.random.randint(1, 5)
        self.color_axis_nexnex = np.random.randint(1, 5)
        self.color_rotate_nexnex = np.random.randint(1, 5)
        self.tsumo()

        # フィールドと制御用変数初期化
        self.step = 1
        self.field_np = np.zeros((WIDTH + 2, HEIGHT + 2), dtype=int)
        self.reset_field()
        self.droptime = 0
        self.rotate_time = 0
        self.move_time = 0

        # 発火判定、スコア計算回りリセット
        self.link_counter = 0
        self.link_bonus_sum = 0
        self.chain_number = 0
        self.color_list = []
        self.color_delete = 0
        self.deleted_puyo_number = 0
        self.all_clear_flag = False
        self.score = 0
        self.score_turn = 0

        self.fire_counter = 0
        self.fire_step = 1
        self.fall_counter = 0
        self.set_end = False
        self.gameover = False
        return self.get_state()

    # フィールドのリセット，ndarrayを通してlistを作る
    def reset_field(self):
        self.field_np[0, 0:] = 9
        self.field_np[WIDTH + 1, 0] = 9
        self.field_np[WIDTH + 1, 1:] = 9
        self.field_np[1:WIDTH + 1, HEIGHT + 1] = 9
        self.field = self.field_np.tolist()
        self.link_is_counted = self.field_np.tolist()
        self.fire_flaged_puyo = self.field_np.tolist()

    # ツモ、ネクストとネクネクを前にずらして操作するぷよの座標をリセット
    def tsumo(self):
        self.x_axis, self.y_axis = 3, 2
        self.x_rotate, self.y_rotate = 3, 1
        self.color_axis = self.color_axis_next
        self.color_rotate = self.color_rotate_next
        self.color_axis_next = self.color_axis_nexnex
        self.color_rotate_next = self.color_rotate_nexnex
        self.color_axis_nexnex = np.random.randint(1, 5)
        self.color_rotate_nexnex = np.random.randint(1, 5)
        self.step = 2

    # 移動用関数
    def move(self, way):
        if way == 1:        # 左移動
            if self.field[self.x_axis - 1][self.y_axis] == 0 and self.field[self.x_rotate - 1][self.y_rotate] == 0:
                self.x_axis += -1
                self.x_rotate += -1

        elif way == 2:      # 右移動
            if self.field[self.x_axis + 1][self.y_axis] == 0 and self.field[self.x_rotate + 1][self.y_rotate] == 0:
                self.x_axis += 1
                self.x_rotate += 1

        elif way == 3:      # 下移動
            if self.field[self.x_axis][self.y_axis + 1] == 0 and self.field[self.x_rotate][self.y_rotate + 1] == 0:
                self.y_axis += 1
                self.y_rotate += 1
            elif self.field[self.x_axis][self.y_axis + 1] != 0 or self.field[self.x_rotate][self.y_rotate + 1] != 0:
                self.step = 3
                self.set_end = True

    # 回転用関数
    def rotate(self, way):
        if way == 1:    # 時計回り（数値の大きいほど盤面において右下を示す）
            # 軸ぷよより上に回転ぷよがある
            if [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [0, 1]:
                if self.field[self.x_axis - 1][self.y_axis] != 0 and self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.y_axis += -1
                    self.y_rotate += 1
                # 回転先にぷよか壁がある
                elif self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.x_axis += -1
                    self.y_rotate += 1
                else:
                    self.x_rotate += 1
                    self.y_rotate += 1

            # 軸ぷよより下に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [0, -1]:
                if self.field[self.x_axis - 1][self.y_axis] != 0 and self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.y_axis += 1
                    self.y_rotate += -1
                elif self.field[self.x_axis - 1][self.y_axis] != 0:
                    self.x_axis += 1
                    self.y_rotate += -1
                else:
                    self.x_rotate += -1
                    self.y_rotate += -1

            # 軸ぷよより右に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [-1, 0]:
                if self.field[self.x_axis][self.y_axis + 1] != 0:
                    self.y_axis += -1
                    self.x_rotate += -1
                else:
                    self.x_rotate += -1
                    self.y_rotate += 1

            # 軸ぷよより左に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [1, 0]:
                self.x_rotate += 1
                self.y_rotate += -1

        elif way == 2:    # 反時計回り
            # 軸ぷよより上に回転ぷよがある
            if [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [0, 1]:
                if self.field[self.x_axis - 1][self.y_axis] != 0 and self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.y_axis += -1
                    self.y_rotate += 1
                # 回転先にぷよか壁がある
                elif self.field[self.x_axis - 1][self.y_axis] != 0:
                    self.x_axis += 1
                    self.y_rotate += 1
                else:
                    self.x_rotate += -1
                    self.y_rotate += 1

            # 軸ぷよより下に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [0, -1]:
                if self.field[self.x_axis - 1][self.y_axis] != 0 and self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.y_axis += 1
                    self.y_rotate += -1
                elif self.field[self.x_axis + 1][self.y_axis] != 0:
                    self.x_axis += -1
                    self.y_rotate += -1
                else:
                    self.x_rotate += 1
                    self.y_rotate += -1

            # 軸ぷよより右に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [-1, 0]:
                self.x_rotate += -1
                self.y_rotate += -1

            # 軸ぷよより左に回転ぷよがある
            elif [self.x_axis - self.x_rotate, self.y_axis - self.y_rotate] == [1, 0]:
                if self.field[self.x_axis][self.y_axis + 1] != 0:
                    self.y_axis += -1
                    self.x_rotate += 1
                else:
                    self.x_rotate += 1
                    self.y_rotate += 1

    # ちぎり判定
    def can_chigiri(self):
        if self.y_axis == self.y_rotate and self.field[self.x_rotate][self.y_rotate + 1] != 0:
            return "axis"
        elif self.y_axis == self.y_rotate and self.field[self.x_axis][self.y_axis+ 1] != 0:
            return "rotate"
        else:
            return "None"

    # ちぎり発生
    def chigiri(self, which):
        if which == "None":
            pass
        elif which == "axis":
            while self.field[self.x_axis][self.y_axis + 1] == 0:
                self.y_axis += 1
        elif which == "rotate":
            while self.field[self.x_rotate][self.y_rotate + 1] == 0:
                self.y_rotate += 1

    # 動かしたぷよを配置する
    def set_puyo(self):
        self.field[self.x_axis][self.y_axis] = self.color_axis
        self.field[self.x_rotate][self.y_rotate] = self.color_rotate
        self.color_axis = self.color_rotate = 0
        self.step = 4

    # 連結数計算
    def link_calculation(self, i, j):
        self.link_counter += 1
        self.link_is_counted[i][j] = self.link_counter
        if self.field[i + 1][j] == self.field[i][j] and self.link_is_counted[i + 1][j] == 0:
            self.link_calculation(i + 1, j)
        if self.field[i][j + 1] == self.field[i][j] and self.link_is_counted[i][j + 1] == 0:
            self.link_calculation(i, j + 1)
        if self.field[i - 1][j] == self.field[i][j] and self.link_is_counted[i - 1][j] == 0:
            self.link_calculation(i - 1, j)
        if self.field[i][j - 1] == self.field[i][j] and self.link_is_counted[i][j - 1] == 0:
            self.link_calculation(i, j - 1)

    # 連結数が4を超えたものはfire_flagを立てる→fire_flagが立ったぷよを消す
    def flag_over4links(self, i, j):
        self.link_is_counted[i][j] = 0
        self.fire_flaged_puyo[i][j] = 1
        self.deleted_puyo_number += 1
        if self.link_is_counted[i + 1][j] > 0 and self.field[i][j] == self.field[i + 1][j]:
            self.flag_over4links(i + 1, j)
        if self.link_is_counted[i][j + 1] > 0 and self.field[i][j] == self.field[i][j + 1]:
            self.flag_over4links(i, j + 1)
        if self.link_is_counted[i - 1][j] > 0 and self.field[i][j] == self.field[i - 1][j]:
            self.flag_over4links(i - 1, j)
        if self.link_is_counted[i][j - 1] > 0 and self.field[i][j] == self.field[i][j - 1]:
            self.flag_over4links(i, j - 1)

    # 発火判定，連結数が0のぷよを始点に連結数を計算する
    '''
    まだ未調査のぷよがあったらlink_counter=0でlink_calculation(i,j)を回す
    link_calculationは呼ばれるたびlink_counter++をしてlink_is_counted=link_counter
    同じ色かつ未調査（link_is_counted==0）のぷよに移動
    連結数計算の結果、link_counter>=4でflag_over4linksをして消すぷよにマーキングする
    最後にfireで一斉に除去
    '''
    def can_fire(self):
        judge = False
        self.deleted_puyo_number = 0
        self.color_list = []
        for i in range(1, WIDTH + 1):
            for j in range(1, HEIGHT + 1):
                if self.field[i][j] != 0 and self.fire_flaged_puyo[i][j] == 0:
                    self.link_counter = 0
                    self.link_is_counted = (np.array(self.link_is_counted) * 0).tolist()
                    self.color_delete = self.field[i][j]
                    self.link_calculation(i, j)
                    if self.link_counter >= 4:
                        self.flag_over4links(i, j)
                        self.link_bonus_sum += self.link_bonus(self.link_counter)
                        self.color_list.append(self.color_delete)
                        judge = True
        return judge

    # fire_flagが立ってるものは消す
    def fire(self):
        for i in range(1, WIDTH + 1):
            for j in range(1, HEIGHT + 1):
                if self.fire_flaged_puyo[i][j] == 1:
                    self.field[i][j] = 0

    # ぷよを消したことによるスコアを計算する
    def score_calculation(self, chain, link_bonus_sum, color_number, del_puyo_number):
        summation = self.chain_bonus(chain) + link_bonus_sum + self.color_bonus(color_number)
        if summation == 0:
            summation = 1
        return del_puyo_number * summation * 10 + self.all_clear_bonus()

    # _bonusは基本ボーナスの計算
    def chain_bonus(self, chain):
        if 1 <= chain <= 3:
            return (chain - 1) * 8
        elif 4 <= chain <= 20:
            return (chain - 3) * 32
        else:
            print("chain is out of range")
            return 0

    def link_bonus(self, link):
        if link <= 4:
            return 0
        elif 5 <= link <= 10:
            return link - 3
        elif 11 <= link <= 6 * 12:
            return 10
        else:
            print("link is out of range")
            return 0

    def color_bonus(self, color_number):
        if color_number == 1:
            return 0
        elif 2 <= color_number <= 3:
            return (color_number - 1) * 3
        elif 4 <= color_number <= 5:
            return (color_number - 3) * 12
        else:
            print("color number is out of range")
            return 0

    def all_clear_bonus(self):
        if self.all_clear_flag:
            self.all_clear_flag = False
            return 2100
        else:
            return 0

    # 発火による落下
    def fall(self):
        flag = False
        for i in range(1, WIDTH + 1):
            for j in range(1, HEIGHT):
                if self.field[i][HEIGHT - j + 1] == 0 and self.field[i][HEIGHT - j] != 0:
                    self.field[i][HEIGHT - j + 1] = self.field[i][HEIGHT - j]
                    self.field[i][HEIGHT - j] = 0
                    flag = True
        return flag

    # 14行目に置けてしまうことがありバグの発生源のため、14行目に置かれたぷよは消去する
    def delete_14th_column(self):
        for i in range(1, WIDTH + 1):
            self.field[i][0] = 0

    def is_gameover(self):
        if self.field[3][2] != 0:
            return True
        else:
            return False

    def is_all_clear(self):
        if np.sum(np.array(self.field)[1:WIDTH + 1, HEIGHT]) == 0:
            return True
        else:
            return False

    # 状態を返す
    def get_state(self):
        field_info = np.array(self.field)[1:WIDTH + 1, 2:HEIGHT + 1]  # .flatten()
        puyo_info = np.array(self.color_axis)
        puyo_info = np.append(puyo_info, self.color_rotate)
        puyo_info = np.append(puyo_info, self.color_axis_next)
        puyo_info = np.append(puyo_info, self.color_rotate_next)
        puyo_info = np.append(puyo_info, self.color_axis_nexnex)
        puyo_info = np.append(puyo_info, self.color_rotate_nexnex)
        field_info = np.array(field_info, dtype=np.float32)
        puyo_info = np.array(puyo_info, dtype=np.float32)
        return field_info, puyo_info

    @abstractmethod
    def flow_management(self):
        pass
