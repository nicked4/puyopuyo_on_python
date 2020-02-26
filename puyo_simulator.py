import puyo_class

import numpy as np
import collections

"""
puyo_class.pyを継承したサブクラス
シミュレータとして用いる

ーーーぷよぷよ操作説明ーーー

Move    : 左移動 1
          右移動 2
          下移動 3
          
Rotation: 時計回転   1
          反時計回転 2
          
盤面のサイズは 6 * 13 がデフォルト
見えている範囲は WIDTH * (HEIGHT - 1)
"""

WIDTH = puyo_class.WIDTH
HEIGHT = puyo_class.HEIGHT


class Player(puyo_class.PuyoSuper):
    # カウンタ（step）を用いてフロー管理
    def flow_management(self):
        # print('puyo now', self.color_axis, self.color_rotate)
        # print('next', self.color_axis_next, self.color_rotate_next)
        # print('nexnex', self.color_axis_nexnex, self.color_rotate_nexnex)
        self.chigiri(self.can_chigiri())
        self.set_puyo()
        self.delete_14th_column()
        self.chain_number = 0
        self.score_turn = 0
        while self.can_fire():
            self.chain_number += 1
            score_current = self.score_calculation(self.chain_number, self.link_bonus_sum,
                                                   len(collections.Counter(self.color_list)), self.deleted_puyo_number)
            self.score += score_current
            self.score_turn += score_current
            self.fall()
            self.link_bonus_sum = 0
        if self.is_gameover():
            self.gameover = True
        elif self.is_all_clear():
            self.all_clear_flag = True
        self.tsumo()
        self.set_end = False

    # 動かしたぷよを配置する
    def set_puyo(self):
        self.field[self.x_axis][self.y_axis] = self.color_axis
        self.field[self.x_rotate][self.y_rotate] = self.color_rotate

    # 連結数が4を超えたものはfire_flagを立てる→fire_flagが立ったぷよを消す
    # self.color_deleteの部分がオーバーライドしたところ
    def flag_over4links(self, i, j):
        self.link_is_counted[i][j] = 0
        self.field[i][j] = 0
        self.deleted_puyo_number += 1
        if self.link_is_counted[i + 1][j] > 0 and self.color_delete == self.field[i + 1][j]:
            self.flag_over4links(i + 1, j)
        if self.link_is_counted[i][j + 1] > 0 and self.color_delete == self.field[i][j + 1]:
            self.flag_over4links(i, j + 1)
        if self.link_is_counted[i - 1][j] > 0 and self.color_delete == self.field[i - 1][j]:
            self.flag_over4links(i - 1, j)
        if self.link_is_counted[i][j - 1] > 0 and self.color_delete == self.field[i][j - 1]:
            self.flag_over4links(i, j - 1)

    # 発火判定，連結数が0のぷよを始点に連結数を計算する
    def can_fire(self):
        judge = False
        self.deleted_puyo_number = 0
        self.color_list = []
        for i in range(1, WIDTH + 1):
            for j in range(1, HEIGHT + 1):  # range(2, HEIGHT + 1)かも
                if self.field[i][j] != 0:
                    self.link_counter = 0
                    self.link_is_counted = np.zeros((WIDTH + 2) * (HEIGHT + 2), dtype=int)\
                        .reshape(WIDTH + 2, HEIGHT + 2).tolist()
                    self.color_delete = self.field[i][j]
                    self.link_calculation(i, j)
                    if self.link_counter >= 4:
                        self.flag_over4links(i, j)
                        self.link_bonus_sum += self.link_bonus(self.link_counter)
                        self.color_list.append(self.color_delete)
                        judge = True
        return judge

    # 発火による落下
    def fall(self):
        flag = True
        while flag:
            flag = False
            for i in range(1, WIDTH + 1):
                for j in range(1, HEIGHT):
                    if self.field[i][HEIGHT - j + 1] == 0 and self.field[i][HEIGHT - j] != 0:
                        self.field[i][HEIGHT - j + 1] = self.field[i][HEIGHT - j]
                        self.field[i][HEIGHT - j] = 0
                        flag = True

    # ランダムに行動する
    def random_action(self):
        random_act = np.random.randint(0, 21)
        self.auto_play(random_act)
        return True

    # 状態を返す
    def get_state(self):
        field_info = np.array(self.field)[1:WIDTH + 1, 2:HEIGHT + 1]
        puyo_info = np.array(self.color_axis)
        puyo_info = np.append(puyo_info, self.color_rotate)
        puyo_info = np.append(puyo_info, self.color_axis_next)
        puyo_info = np.append(puyo_info, self.color_rotate_next)
        puyo_info = np.append(puyo_info, self.color_axis_nexnex)
        puyo_info = np.append(puyo_info, self.color_rotate_nexnex)
        field_info = np.array(field_info, dtype=np.float32)
        puyo_info = np.array(puyo_info, dtype=np.float32)
        return field_info, puyo_info

    # 22種の行動のうちいずれかを与える
    def rl_step(self, num):
        done = False
        self.score_turn = 0
        self.auto_play(num)
        self.flow_management()
        if self.gameover:
            done = True
        return self.get_state(), self.score_turn, done, self.chain_number
        # return self.get_state(), self.chain_number, done, self.chain_number

    # def rl_step(self, num):
    #     done = False
    #     self.score_turn = 0
    #     self.auto_play(num)
    #     self.flow_management()
    #     if self.gameover:
    #         done = True
    #     # field_state, _ = self.get_state()
    #     # print(str(field_state.T))
    #     return self.get_state(), self.score_turn, done, self.chain
    #     # return self.get_state(), self.chain, done, self.chain

    # 22種類の行動をする
    def auto_play(self, num):
        cnt = 0
        self.set_end = False
        while not self.set_end:
            # そのまま落下
            if num == 0:
                if cnt <= 1:
                    self.move(1)
                else:
                    self.move(3)
            elif num == 1:
                if cnt == 0:
                    self.move(1)
                else:
                    self.move(3)
            elif num == 2:
                self.move(3)
            elif num == 3:
                if cnt == 0:
                    self.move(2)
                else:
                    self.move(3)
            elif num == 4:
                if cnt <= 1:
                    self.move(2)
                else:
                    self.move(3)
            elif num == 5:
                if cnt <= 2:
                    self.move(2)
                else:
                    self.move(3)

            # 反転して落下
            elif num == 6:
                if cnt <= 1:
                    self.rotate(2)
                    self.move(1)
                else:
                    self.move(3)
            elif num == 7:
                if cnt == 0:
                    self.rotate(2)
                    self.move(1)
                elif cnt == 1:
                    self.rotate(2)
                else:
                    self.move(3)
            elif num == 8:
                if cnt <= 1:
                    self.rotate(2)
                else:
                    self.move(3)
            elif num == 9:
                if cnt == 0:
                    self.rotate(1)
                    self.move(2)
                elif cnt == 1:
                    self.rotate(1)
                else:
                    self.move(3)
            elif num == 10:
                if cnt <= 1:
                    self.rotate(1)
                    self.move(2)
                else:
                    self.move(3)
            elif num == 11:
                if cnt <= 1:
                    self.rotate(1)
                    self.move(2)
                elif cnt == 2:
                    self.move(2)
                else:
                    self.move(3)

            # 時計回りで落下
            elif num == 12:
                if cnt == 0:
                    self.move(1)
                    self.rotate(1)
                else:
                    self.move(3)
            elif num == 13:
                if cnt == 0:
                    self.rotate(1)
                else:
                    self.move(3)
            elif num == 14:
                if cnt == 0:
                    self.move(2)
                    self.rotate(1)
                else:
                    self.move(3)
            elif num == 15:
                if cnt == 0:
                    self.move(2)
                    self.rotate(1)
                elif cnt == 1:
                    self.move(2)
                else:
                    self.move(3)
            elif num == 16:
                if cnt == 0:
                    self.move(2)
                    self.rotate(1)
                elif 0 < cnt <= 2:
                    self.move(2)
                else:
                    self.move(3)

            # 反時計回りで落下
            elif num == 17:
                if cnt == 0:
                    self.rotate(2)
                    self.move(1)
                else:
                    self.move(3)
            elif num == 18:
                if cnt == 0:
                    self.rotate(2)
                else:
                    self.move(3)
            elif num == 19:
                if cnt == 0:
                    self.rotate(2)
                    self.move(2)
                else:
                    self.move(3)
            elif num == 20:
                if cnt == 0:
                    self.rotate(2)
                    self.move(2)
                elif cnt == 1:
                    self.move(2)
                else:
                    self.move(3)
            elif num == 21:
                if cnt == 0:
                    self.move(2)
                    self.rotate(2)
                elif 0 < cnt <= 2:
                    self.move(2)
                self.move(3)
            cnt += 1
