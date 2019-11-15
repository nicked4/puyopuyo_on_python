import pygame
from pygame.locals import *
import sys
import numpy as np
import collections
import time

# 画面サイズ、盤面サイズ、移動速度などの設定
SCREEN_SIZE = (1200, 900)
WIDTH = 6
HEIGHT = 13
ROTATE_TIME = 40
MOVE_TIME = 4
FIRE_TIME = 30
FALL_TIME = 5
size = 50


# ゲームグラフィック
class Graphic():
    def __init__(self):
        # puyo_graphicが表示するぷよの画像
        self.puyo_graphic = [0] * 10
        self.puyo_graphic[0] = pygame.image.load("picture/blue.png")
        self.puyo_graphic[1] = pygame.image.load("picture/puyo_red.png")
        self.puyo_graphic[2] = pygame.image.load("picture/puyo_blu.png")
        self.puyo_graphic[3] = pygame.image.load("picture/puyo_ylw.png")
        self.puyo_graphic[4] = pygame.image.load("picture/puyo_grn.png")
        self.puyo_graphic[5] = pygame.image.load("picture/puyo_ppl.png")
        self.puyo_graphic[6] = pygame.image.load("picture/puyo_jam.png")
        self.puyo_graphic[7] = pygame.image.load("picture/puyo_jam.png")
        self.puyo_graphic[8] = pygame.image.load("picture/puyo_jam.png")
        self.puyo_graphic[9] = pygame.image.load("picture/black.jpg")

        # その他タイトルの画像と整形
        self.background = pygame.image.load("picture/puyo_background.png")
        self.title = pygame.image.load("picture/puyo_esports.jpg")
        self.gameover = pygame.image.load("picture/gameover.png")
        self.peke = pygame.image.load("picture/peke.png")
        self.background = pygame.transform.smoothscale(self.background, SCREEN_SIZE)
        self.title = pygame.transform.smoothscale(self.title, SCREEN_SIZE)
        self.gameover = pygame.transform.smoothscale(self.gameover, SCREEN_SIZE)
        self.peke = pygame.transform.smoothscale(self.peke, (size, size))
        for i in range(10):
            self.puyo_graphic[i] = pygame.transform.smoothscale(self.puyo_graphic[i], (size, size))


# ゲーム本体
class Player():
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
        self.fall_speed = 6
        self.falltime = 0
        self.droptime = 0
        self.dtime = 0
        self.time = 0
        self.rotate_time = 0
        self.move_time = 0
        self.actiontime = 100

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
        self.score_now = 0
        self.score_turn = 0

        # 発火と落下時の挙動（連鎖の過程を見せるための制御）
        self.fire_counter = 0
        self.fire_step = 0
        self.fall_counter = 0

    # ゲーム開始時のリセット
    def reset(self):
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

        # フィールドと制御用変数初期化
        self.step = 1
        self.field_np = np.zeros((WIDTH + 2, HEIGHT + 2), dtype=int)
        self.reset_field()
        self.falltime = 20
        self.droptime = 5
        self.dtime = self.falltime
        self.time = self.dtime

        # 発火判定、スコア計算回りリセット
        self.fire_flaged_puyo = []
        self.link_counter = 0
        self.link_bonus_sum = 0
        self.chain_number = 0
        self.color_list = []
        self.color_delete = 0
        self.deleted_puyo_number = 0
        self.all_clear_flag = False
        self.score = 0
        self.score_now = 0
        self.score_turn = 0

        self.fire_counter = 0
        self.fire_step = 1
        self.fall_counter = 0

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
                self.actiontime = 0
                self.step = 3

    # 回転用関数
    def rotate(self, way):
        if way == 1:    # 時計回り（右下の方が数が大きい）
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
            # 軸ぷよより上に回転ぷよがある（右下の方が数が大きい）
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
        elif 11 <= link:
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

    # 個々の描画を行う、後半のdraw()で全体を管理
    def draw_puyo(self):
        for i in range(0, WIDTH + 2):
            for j in range(0, HEIGHT + 2):
                if self.field[i][j] != 0:
                    screen.blit(graphic.puyo_graphic[self.field[i][j]],
                                [i * size + SCREEN_SIZE[0] / 2 - 200, j * size + SCREEN_SIZE[1] / 2 - 375])
        screen.blit(graphic.peke, [3 * size + SCREEN_SIZE[0] / 2 - 200, 2 * size + SCREEN_SIZE[1] / 2 - 375])

    def draw_tsumo(self):
        if self.color_axis != 0 and self.color_rotate != 0:
            screen.blit(graphic.puyo_graphic[self.color_axis], [self.x_axis * size + SCREEN_SIZE[0] / 2 - 200,
                                                                self.y_axis * size + SCREEN_SIZE[1] / 2 - 375])
            screen.blit(graphic.puyo_graphic[self.color_rotate], [self.x_rotate * size + SCREEN_SIZE[0] / 2 - 200,
                                                                  self.y_rotate * size + SCREEN_SIZE[1] / 2 - 375])

    def draw_next(self):
        screen.blit(graphic.puyo_graphic[self.color_axis_next],
                    [SCREEN_SIZE[0] / 2 + 5 * size, SCREEN_SIZE[1] / 2 - 6 * size])
        screen.blit(graphic.puyo_graphic[self.color_rotate_next],
                    [SCREEN_SIZE[0] / 2 + 5 * size, SCREEN_SIZE[1] / 2 - 7 * size])
        screen.blit(graphic.puyo_graphic[self.color_axis_nexnex],
                    [SCREEN_SIZE[0] / 2 + 6 * size, SCREEN_SIZE[1] / 2 - 4 * size])
        screen.blit(graphic.puyo_graphic[self.color_rotate_nexnex],
                    [SCREEN_SIZE[0] / 2 + 6 * size, SCREEN_SIZE[1] / 2 - 5 * size])

    # 描画全体
    def draw(self):
        screen.blit(graphic.background, (0, 0))  # 背景（画像）
        screen.fill((0, 50, 50), Rect(SCREEN_SIZE[0] / 2 - 200, SCREEN_SIZE[1] / 2 - 375,
                                      (WIDTH + 1) * size, (HEIGHT + 1) * size))
        screen.fill((200, 200, 200), Rect(SCREEN_SIZE[0] / 2 - 200, SCREEN_SIZE[1] / 2 - 375,
                                          (WIDTH + 1) * size, 2 * size))
        screen.fill((0, 50, 50),
                    Rect(SCREEN_SIZE[0] / 2 + 4.5 * size, SCREEN_SIZE[1] / 2 - 7.5 * size, 3 * size, 5 * size))
        self.draw_puyo()
        self.draw_tsumo()
        self.draw_next()
        screen.fill((0, 50, 50), Rect(100, 100, 240, 450))
        for i in range(1, WIDTH+1):
            for j in range(1, HEIGHT + 1):
                field = sysfont.render(str(self.field[i][j]), True, (255, 255, 255))
                screen.blit(field, (100 + 30 * i, 100 + 30 * j))

    # カウンタ（step）を用いてゲームフロー管理
    def flow_management(self):
        # ツモをする
        if self.step == 1:
            self.tsumo()

        # ぷよを操作する
        elif self.step == 2:
            pressed = pygame.key.get_pressed()
            # 操作性をよくするために一定時間ボタンを押されたら動くようにしている
            if pressed[K_x] or pressed[K_z]:
                self.rotate_time += 1
            else:
                self.rotate_time = ROTATE_TIME - 1
            if pressed[K_LEFT] or pressed[K_RIGHT] or pressed[K_DOWN]:
                self.move_time += 1
            else:
                self.move_time = MOVE_TIME - 1

            # 回転
            if self.rotate_time >= ROTATE_TIME:
                self.rotate_time = 0
                if pressed[K_x]:
                    self.rotate(1)
                elif pressed[K_z]:
                    self.rotate(2)

            # 移動
            if self.move_time >= MOVE_TIME:
                self.move_time = 0
                if pressed[K_LEFT]:
                    self.move(1)
                elif pressed[K_RIGHT]:
                    self.move(2)
                elif pressed[K_DOWN]:
                    self.move(3)
            else:
                self.dtime = self.droptime
                self.actiontime = 0

        # ぷよの設置
        elif self.step == 3:
            self.chigiri(self.can_chigiri())
            self.set_puyo()
            self.delete_14th_column()
            self.chain_number = 0
            self.score_turn = 0
            self.fire_flaged_puyo = self.field_np.tolist()

        # 発火とスコア計算
        elif self.step == 4:
            if self.can_fire() and self.fire_step == 1:
                self.chain_number += 1
                self.score_now = self.score_calculation(self.chain_number, self.link_bonus_sum,
                                                        len(collections.Counter(self.color_list)),
                                                        self.deleted_puyo_number)
                self.score += self.score_now
                self.score_turn += self.score_now
                self.fire_flaged_puyo = self.field_np.tolist()
                self.link_bonus_sum = 0
                self.fire_step = 2

            # 一定時間経過したら発火（ゲーム演出）
            elif self.fire_step == 2:
                if self.fire_counter < FIRE_TIME:
                    self.fire_counter += 1
                else:
                    self.fire()
                    self.fire_counter = 0
                    self.fire_step = 3

            # 落下させる、次に発火するものがなかったら次のステップへ
            elif self.fire_step == 3:
                if self.fall_counter < FALL_TIME:
                    self.fall_counter += 1
                else:
                    if not self.fall():
                        self.fire_flaged_puyo = (np.array(self.fire_flaged_puyo) * 0).tolist()
                        self.fire_step = 1
                    self.fall_counter = 0
            else:
                self.fire_step = 1
                self.step = 5

        # ゲームオーバー判定
        elif self.step == 5:
            if self.is_gameover():
                self.step = 9
            else:
                if self.is_all_clear():
                    self.all_clear_flag = True
                self.step = 1


# 終了判定
def event_processing(event):
    if event.type == QUIT:
        sys.exit()


def main():
    pygame.init()
    global screen
    global graphic
    global sysfont
    screen = pygame.display.set_mode(SCREEN_SIZE)  # ウィンドウの大きさ
    sysfont = pygame.font.SysFont(None, 40)

    # 画面更新時間を管理
    fps = pygame.time.Clock()
    player1 = Player()
    graphic = Graphic()
    player1.reset()
    game_mode = 0

    while True:
        fps.tick(60)

        # ゲーム中
        if game_mode == 1:
            screen.fill((0, 0, 200))
            player1.flow_management()
            if player1.step == 9:
                game_mode = 2
            score = sysfont.render("SCORE : " + str(player1.score), True, (255, 255, 255))
            player1.draw()
            screen.fill((0, 0, 0), Rect(10, 10, 300, 45))
            screen.blit(score, (20, 20))

        # スタート待機中
        elif game_mode == 0:
            screen.blit(graphic.title, (0, 0))  # タイトル（画像）
        elif game_mode == 2:
            screen.blit(graphic.gameover, (0, 0))  # タイトル（画像）

        # エンターキーでリセット＆スタート
        pressed = pygame.key.get_pressed()
        if pressed[K_RETURN] and game_mode == 0:
            player1.reset()
            game_mode = 1
        # ゲームオーバーはスペースキーで解除
        if pressed[K_r] and game_mode == 2:
            game_mode = 0
        # 全部終了
        if pressed[K_ESCAPE]:
            break

        # 画面の更新
        pygame.display.update()

        # イベントの取得
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()  # 閉じるボタンが押されたらプログラムを終了
                sys.exit()


if __name__ == "__main__":
    main()
