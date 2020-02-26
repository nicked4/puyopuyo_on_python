import puyo_class

import sys
import collections
import pygame
from pygame.locals import *
import numpy as np

WIDTH = puyo_class.WIDTH
HEIGHT = puyo_class.HEIGHT
SCREEN_SIZE = puyo_class.SCREEN_SIZE
ROTATE_TIME = puyo_class.ROTATE_TIME
MOVE_TIME = puyo_class.MOVE_TIME
FIRE_TIME = puyo_class.FIRE_TIME
FALL_TIME = puyo_class.FALL_TIME
size = puyo_class.size


class Player(puyo_class.PuyoSuper):
    def __init__(self, agent):
        self.agent = agent
        self.ai_action = 0
        self.ai_action_controller = 0
        self.action_distribution = [0] * 22
        super().__init__()

    def reset(self, seed=False):
        self.ai_action = 0
        self.ai_action_controller = 0
        self.action_distribution = [0] * 22
        super().reset()

    # カウンタ（step）を用いてフロー管理
    def flow_management(self):
        # ツモを引く
        # AIの行動を決定する
        if self.step == 1:
            self.tsumo()
            self.ai_action = self.agent.act(self.get_state())
            self.action_distribution[self.ai_action] += 1
            print(self.ai_action)
            self.ai_action_controller = 0

        # AIに実際に行動をさせる
        elif self.step == 2:
            self.auto_play(self.ai_action, self.ai_action_controller)

        # ちぎり判定とぷよの配置
        elif self.step == 3:
            self.chigiri(self.can_chigiri())
            self.set_puyo()
            self.delete_14th_column()
            self.chain_number = 0
            self.score_turn = 0
            self.fire_flaged_puyo = self.field_np.tolist()

        # 発火処理とスコア計算
        elif self.step == 4:
            if self.can_fire() and self.fire_step == 1:
                self.chain_number += 1
                self.score_current = self.score_calculation(
                    self.chain_number, self.link_bonus_sum, len(collections.Counter(self.color_list)), self.deleted_puyo_number)
                self.score += self.score_current
                self.score_turn += self.score_current
                self.fire_flaged_puyo = self.field_np.tolist()
                self.link_bonus_sum = 0
                self.fire_step = 2
            elif self.fire_step == 2:
                if self.fire_counter < FIRE_TIME:
                    self.fire_counter += 1
                else:
                    self.fire()
                    self.fire_counter = 0
                    self.fire_step = 3
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

        # ゲームオーバー状態
        elif self.step == 5:
            if self.is_gameover():
                self.step = 9
            else:
                if self.is_all_clear():
                    self.all_clear_flag = True
                self.step = 1

        # ゲームオーバー時にRキーを押下された場合ニューゲーム
        elif self.step == 9:
            pressed = pygame.key.get_pressed()
            if pressed[K_r]:
                self.reset()

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

    # 22種類の行動をする
    # ごりごりに書くしかないためごりごりに実装
    def auto_play(self, num, cnt):
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

        # 時計回りして落下
        elif num == 12:
            if cnt == 0:
                self.move(1)
                self.rotate(1)
            elif cnt == 1:
                self.move(1)
            else:
                self.move(3)
        elif num == 13:
            if cnt == 0:
                self.move(1)
                self.rotate(1)
            else:
                self.move(3)
        elif num == 14:
            if cnt == 0:
                self.rotate(1)
            else:
                self.move(3)
        elif num == 15:
            if cnt == 0:
                self.move(2)
                self.rotate(1)
            else:
                self.move(3)
        elif num == 16:
            if cnt == 0:
                self.move(2)
                self.rotate(1)
            elif cnt == 1:
                self.move(2)
            else:
                self.move(3)

        # 反時計回りして落下
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
        self.ai_action_controller += 1


# 終了判定
def event_processing(event):
    if event.type == QUIT:
        sys.exit()


# ランダムな行動をするエージェント
class RandomAgent:
    def act(self, *arg):
        return np.random.randint(0, 22)


def main():
    pygame.init()
    global screen
    global graphic
    global sysfont
    screen = pygame.display.set_mode(SCREEN_SIZE)  # ウィンドウの大きさ
    graphic = puyo_class.Graphic()
    sysfont = pygame.font.SysFont(None, 40)

    # AIをロード（ここではサンプルのため完全にランダムな行動をするAIとしている）
    agent = RandomAgent()
    player1 = Player(agent)
    player1.reset()
    player1.step = 1

    # 画面更新時間を管理
    fps = pygame.time.Clock()

    while True:
        fps.tick(60)
        # ゲーム中
        screen.fill((0, 0, 200))
        player1.flow_management()  # ここでゲームの進行を行っている → AIの操作を行わせる
        score = sysfont.render("SCORE : " + str(player1.score), True, (255, 255, 255))
        player1.draw()
        screen.fill((0, 0, 0), Rect(10, 10, 300, 45))
        screen.blit(score, (20, 20))

        pygame.display.update()

        # イベントの取得
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()  # 閉じるボタンが押されたらプログラムを終了
                print(player1.action_distribution)
                sys.exit()


if __name__ == "__main__":
    main()
