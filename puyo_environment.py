import puyo_class

import sys
import pygame
from pygame.locals import *
import numpy as np
import collections

WIDTH = puyo_class.WIDTH
HEIGHT = puyo_class.HEIGHT
SCREEN_SIZE = puyo_class.SCREEN_SIZE
ROTATE_TIME = puyo_class.ROTATE_TIME
MOVE_TIME = puyo_class.MOVE_TIME
FIRE_TIME = puyo_class.FIRE_TIME
FALL_TIME = puyo_class.FALL_TIME
size = puyo_class.size


class Player(puyo_class.PuyoSuper):
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
                score_current = self.score_calculation(self.chain_number, self.link_bonus_sum,
                                                       len(collections.Counter(self.color_list)),
                                                       self.deleted_puyo_number)
                self.score += score_current
                self.score_turn += score_current
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
            screen.blit(graphic.puyo_graphic[self.color_axis],
                        [self.x_axis * size + SCREEN_SIZE[0] / 2 - 200, self.y_axis * size + SCREEN_SIZE[1] / 2 - 375])
            screen.blit(graphic.puyo_graphic[self.color_rotate],
                        [self.x_rotate * size + SCREEN_SIZE[0] / 2 - 200, self.y_rotate * size + SCREEN_SIZE[1] / 2 - 375])

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
        screen.fill((0, 50, 50), Rect(SCREEN_SIZE[0] / 2 - 200, SCREEN_SIZE[1] / 2 - 375, (WIDTH + 1) * size, (HEIGHT + 1) * size))
        screen.fill((200, 200, 200), Rect(SCREEN_SIZE[0] / 2 - 200, SCREEN_SIZE[1] / 2 - 375, (WIDTH + 1) * size, 2 * size))
        screen.fill((0, 50, 50), Rect(SCREEN_SIZE[0] / 2 + 4.5 * size, SCREEN_SIZE[1] / 2 - 7.5 * size, 3 * size, 5 * size))
        self.draw_puyo()
        self.draw_tsumo()
        self.draw_next()
        screen.fill((0, 50, 50), Rect(100, 100, 240, 450))
        for i in range(1, WIDTH + 1):
            for j in range(1, HEIGHT + 1):
                field = sysfont.render(str(self.field[i][j]), True, (255, 255, 255))
                screen.blit(field, (100 + 30 * i, 100 + 30 * j))


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
    graphic = puyo_class.Graphic()
    sysfont = pygame.font.SysFont(None, 40)

    # 画面更新時間を管理
    fps = pygame.time.Clock()
    player1 = Player()
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
            screen.blit(graphic.title, (0, 0))
        elif game_mode == 2:
            screen.blit(graphic.gameover, (0, 0))

        # エンターキーでリセット＆スタート
        pressed = pygame.key.get_pressed()
        if pressed[K_RETURN] and game_mode == 0:
            player1.reset()
            game_mode = 1
        # ゲームオーバーはRキーで解除
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
