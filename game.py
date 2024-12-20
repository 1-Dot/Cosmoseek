import math
import random
import sys
from decimal import Decimal
from math import cos, pi, sin, sqrt
from sys import exit

import pygame

from utils import *

screen_rect = [0.0, 0.0, 2400.0, 1350.0]
camera = [0.0, 0.0, 1.0]  # x,y,scale
is_dragging, last_mouse_pos = False, None
camera_animation_from = [0.0, 0.0, 1.0]
camera_animation_to = [0.0, 0.0, 1.0]
camera_animation_state = 1.0
camera_animation_frames = 8
time_start_drag = None
pos_start_drag = None
is_fullscreen = True  # 是否全屏，发布时设置为True
text_temp_tick = 0
G = 1

min_size = 4
pygame.font.init()
font_20 = pygame.font.Font('assets/Unifont-Minecraft.otf', 20)
font_24 = pygame.font.Font('assets/Unifont-Minecraft.otf', 24)


class Cosmoseek:
    # 创建游戏
    def __init__(self):
        self.NUM_PLANETS = 1000
        self.planets = []
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("assets/Stargazer (Planetarium).mp3")
        pygame.mixer.music.play(-1)
        self.score = 0

        # 全屏
        if is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_rect[2], screen_rect[3] = map(float, self.screen.get_size())
            self.WIDTH, self.HEIGHT = int(screen_rect[2]), int(screen_rect[3])
        else:
            self.WIDTH, self.HEIGHT = int(screen_rect[2]), int(screen_rect[3])
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        # self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Cosmoseek")
        pygame.display.set_icon(pygame.image.load("assets/ship_111_0.png"))
        self.clock = pygame.time.Clock()
        self.message = ""
        self.message2 = ""
        self.ship = Ship(self)
        self.rungame = True
        self.rate = 1
        self.key_minus = False
        self.key_plus = False
        self.locating_ship = False

        self.temp_message = ""
        self.mouse_pos = [0, 0]
        prizes = []

        self.is_click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

        for i in range(100):
            if i < 2:
                prizes.append([["fuel", 50], ["fuel", 60], ["fuel", 70]])
            elif i < 4:
                prizes.append(
                    [
                        ["fuel", 50],
                        ["fuel", 60],
                        ["fuel", 70],
                        ["thruster_efficiency", 1],
                    ]
                )
            elif i < 7:
                prizes.append(
                    [
                        ["fuel", 50],
                        ["fuel", 60],
                        ["fuel", 70],
                        ["thruster_efficiency", 1],
                        ["thruster_power", 2],
                    ]
                )
            elif i < 10:
                prizes.append(
                    [
                        ["fuel", 50],
                        ["fuel", 60],
                        ["fuel", 70],
                        ["thruster_efficiency", 1],
                        ["thruster_power", 2],
                        ["mass", -1],
                        ["prediction_nums", 1],
                        ["prediction_steps", 50],
                    ]
                )
            else:
                prizes.append(
                    [
                        ["fuel", 50],
                        ["fuel", 60],
                        ["fuel", 70],
                        ["thruster_efficiency", 1],
                        ["thruster_power", 2],
                    ]
                )

        def gen_terrestrial(x, y):

            typ = "terrestrial"
            radius = max(random.gauss(8000, 4000), 1000)
            mass = radius**2 * random.uniform(0.5, 2)  # 质量与半径平方成正比

            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            atmosphere = {
                "radius": radius * max(random.gauss(1.3, 0.3), 1),
                "density": sqrt(mass) * max(0.01, random.gauss(0.2, 3)),
                "type": "A",
            }
            # print(radius, mass)
            difficulty = (
                2000
                + radius
                + sqrt(mass)
                + sqrt(atmosphere["density"] * (atmosphere["radius"] - radius)) * 1e-3
            )
            # print(difficulty)
            t_difficulty = difficulty
            prize_tier = 0
            t_prize = []
            while t_difficulty > 0:
                t_difficulty -= 3000
                prize_tier += 1

                if random.uniform(0, 1) > 0.8:
                    t_prize.append(random.choice(prizes[prize_tier + 1]))
                else:
                    t_prize.append(random.choice(prizes[prize_tier]))
                while random.uniform(0, 1) > 0.8:
                    t_prize.append(random.choice(prizes[prize_tier]))
            rewards = {}
            for p in t_prize:
                if p[0] in rewards.keys():
                    rewards[p[0]] += p[1]
                else:
                    rewards[p[0]] = p[1]
            self.planets.append(
                Planet(
                    _,
                    x,
                    y,
                    radius,
                    mass,
                    color,
                    0,
                    0,
                    True,
                    atmosphere,
                    self.ship,
                    self,
                    rewards,
                    typ,
                )
            )

        def gen_gas_giant(x, y):

            typ = "gas_giant"
            radius = max(random.gauss(40000, 20000), 10000)
            mass = radius**2 * random.uniform(1, 4)  # 质量与半径平方成正比

            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            atmosphere = {
                "radius": radius * max(random.gauss(2.5, 1), 1),
                "density": sqrt(mass) * max(0.1, random.gauss(0.2, 3)),
                "type": "A",
            }
            difficulty = (
                radius
                + sqrt(mass)
                + sqrt(atmosphere["density"] * (atmosphere["radius"] - radius)) * 1e-3
            )
            rewards = {
                "fuel": max(1, int(random.gauss(difficulty // 30000 + 2, 1))) * 200
            }
            # print(radius, mass,difficulty)
            self.planets.append(
                Planet(
                    _,
                    x,
                    y,
                    radius,
                    mass,
                    color,
                    0,
                    0,
                    True,
                    atmosphere,
                    self.ship,
                    self,
                    rewards,
                    typ,
                )
            )

        for _ in range(int(self.NUM_PLANETS / 10 * 8)):
            # radius = random.randint(5000, 200000)
            # mass = radius**2  # 质量与半径平方成正比
            x = random.randint(-self.WIDTH * 1000000, self.WIDTH * 1000000)
            y = random.randint(-self.HEIGHT * 1000000, self.HEIGHT * 1000000)
            gen_terrestrial(x, y)

            # color = (
            #    random.randint(50, 255),
            #    random.randint(50, 255),
            #    random.randint(50, 255),
            # )
            # atmosphere = {
            #    "radius": radius * random.uniform(1, 3),
            #    "density": radius * random.uniform(1, 3),
            #    "type": "A",
            # }
            # self.planets.append(
            #    Planet(_, x, y, radius, mass, color, 0, 0, True, atmosphere,self.ship,self)
            # )

        for _ in range(_ + 1, _ + 1 + int(self.NUM_PLANETS / 10 * 2)):

            x = random.randint(-self.WIDTH * 1000000, self.WIDTH * 1000000)
            y = random.randint(-self.HEIGHT * 1000000, self.HEIGHT * 1000000)
            gen_gas_giant(x, y)
            # print(len(self.planets))

    def game_over(self):
        # 把游戏结束事件封装 可在其他游戏结束的情况时调用
        # 创建游戏结束提示
        background_image = pygame.image.load(
            "assets/game_over_background.png"
        ).convert()
        background_image = pygame.transform.scale(
            background_image, (self.WIDTH, self.HEIGHT)
        )
        background_rect = background_image.get_rect()
        self.screen.blit(background_image, background_rect)
        font = pygame.font.Font('assets/Unifont-Minecraft.otf', 84)
        text = font.render(f"你死了！", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.WIDTH // 2, self.HEIGHT // 2 - 112)
        self.screen.blit(text, text_rect)

        font = pygame.font.Font('assets/Unifont-Minecraft.otf', 32)
        text = font.render(
            '烟花火箭 ' + ('燃料耗尽' if self.ship.fuel <= 0 else '感受到了动能'),
            True,
            (255, 255, 255),
        )
        text_rect = text.get_rect()
        text_rect.center = (self.WIDTH // 2, self.HEIGHT // 2 - 24)
        self.screen.blit(text, text_rect)

        font = pygame.font.Font('assets/Unifont-Minecraft.otf', 32)
        text = font.render(f"分数: {self.score}", True, (252, 252, 84))
        text_rect = text.get_rect()
        text_rect.center = (self.WIDTH // 2, self.HEIGHT // 2 + 24)
        self.screen.blit(text, text_rect)

        # 创建重新开始提示
        restart_font = pygame.font.Font('assets/Unifont-Minecraft.otf', 32)
        restart_text = restart_font.render("点按 [R] 重新开始", True, (255, 255, 255))
        restart_rect = restart_text.get_rect()
        restart_rect.center = (self.WIDTH // 2, self.HEIGHT // 2 + 108)
        self.screen.blit(restart_text, restart_rect)
        # 创建退出提示
        quit_font = pygame.font.Font('assets/Unifont-Minecraft.otf', 32)
        quit_text = quit_font.render("点按 [Q] 退出", True, (255, 255, 255))
        quit_rect = quit_text.get_rect()
        quit_rect.center = (self.WIDTH // 2, self.HEIGHT // 2 + 160)
        self.screen.blit(quit_text, quit_rect)
        pygame.display.flip()
        waiting = True

        pygame.mixer.music.load("assets/Fade Out.mp3")
        pygame.mixer.music.play(-1)

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                        self.__init__()
                        game.locating_ship = True
                    if event.key == pygame.K_q:
                        exit()
        return None

    def camera_calculate(self):
        # 视角计算
        global camera, camera_animation_from, camera_animation_to, camera_animation_state
        # Ease-Out: 1-(1-t)^3
        if camera_animation_state < 1.0:
            camera_animation_state += 1.0 / camera_animation_frames
            if not self.locating_ship:
                camera[0] = camera_animation_from[0] + (
                    camera_animation_to[0] - camera_animation_from[0]
                ) * (1 - (1 - camera_animation_state) ** 3)
                camera[1] = camera_animation_from[1] + (
                    camera_animation_to[1] - camera_animation_from[1]
                ) * (1 - (1 - camera_animation_state) ** 3)
            camera[2] = camera_animation_from[2] + (
                camera_animation_to[2] - camera_animation_from[2]
            ) * (1 - (1 - camera_animation_state) ** 3)

    def planet_excution(self):
        planets_to_show_info_i = None
        planets_to_show_info_distance = None
        for i, planet in enumerate(self.planets):
            # planet.info_display()
            planet.crash()  # 处理坠毁
            planet.update_position()
            draw_x = (planet.x - planet.radius - camera[0]) / camera[
                2
            ] + planet.radius / camera[2]
            draw_y = (planet.y - planet.radius - camera[1]) / camera[
                2
            ] + planet.radius / camera[2]
            planet.calc_render_position(draw_x, draw_y, camera[2])
            planet.draw_atmosphere(self.screen)
            planet.draw2(self.screen)
            if planet.p_id in self.ship.closest_planets:
                planet.name_render(self.screen)
            distance = sqrt(
                (planet.render_x - self.mouse_pos[0]) ** 2
                + (planet.render_y - self.mouse_pos[1]) ** 2
            )

            if (
                distance < max(min_size, planet.radius / planet.render_scale) + 24
                and 0 <= planet.render_x <= self.WIDTH
                and 0 <= planet.render_y <= self.HEIGHT
            ):
                if planets_to_show_info_i is None or (
                    planets_to_show_info_i and distance < planets_to_show_info_distance
                ):
                    planets_to_show_info_distance = distance
                    planets_to_show_info_i = i

        if planets_to_show_info_i:
            self.planets[planets_to_show_info_i].draw_info()
            # print(distance,max(min_size,planet.radius / camera[2]))
            # self.is_click=False
        # else:
        #    planet.draw_info_condition = False
        # if 0<=planet.render_x<=self.WIDTH and 0<=planet.render_y<=self.HEIGHT:
        # print(distance,max(min_size,planet.radius / camera[2]),planet.p_id)

    def runing_info(self):
        # 运行信息显示
        info_offset = 32
        font = font_24
        info2 = f'分数 {self.score}   燃料 {self.ship.fuel:.2f}'
        text2 = font.render(info2, True, (255, 255, 255))
        self.screen.blit(text2, (info_offset + 20, info_offset + 20))

        info5 = f'受力X {self.ship.force_x:.2f}   受力Y {self.ship.force_y:.2f}   推进效率 {self.ship.thruster_efficiency:.2f}   推进力 {self.ship.thruster_power:.2f}'
        text5 = font.render(info5, True, (255, 255, 255))
        self.screen.blit(text5, (info_offset + 20, info_offset + 70))

        info = f'角度 {self.ship.angle:.2f}   转速 {self.ship.rotation_speed:.2f}   方向 {self.ship.direction[0]:.2f}, {self.ship.direction[1]:.2f}   加速度 {self.ship.acceleration:.2f}   速率 {self.ship.velocity[0]:.2f}, {self.ship.velocity[1]:.2f}, {self.ship.velocity[2]:.2f}'
        text = font.render(info, True, (255, 255, 255))
        self.screen.blit(text, (info_offset + 20, info_offset + 120))

        # self.message = f'燃料 {self.ship.fuel:.2f}   受力x {self.ship.force_x:.2f}   受力y {self.ship.force_y:.2f}, {self.ship.direction[1]:.2f}'
        # print(self.message2)
        text4 = font.render(self.message2, True, (255, 255, 255))  # 星球信息
        self.screen.blit(text4, (info_offset + 20, info_offset + 170))

        text3 = font.render(self.message, True, (255, 255, 255))  # 降落消耗燃料信息
        self.screen.blit(text3, (info_offset + 20, info_offset + 220))

        rate_info = f'变速 {self.rate:.0f}x'
        rate_text = font.render(rate_info, True, (255, 255, 255))
        self.screen.blit(rate_text, (info_offset + 20, info_offset + 270))

        if pygame.time.get_ticks() - text_temp_tick < 600:
            text_temp = font.render(self.temp_message, True, (255, 255, 255))
            self.screen.blit(text_temp, (info_offset + 20, info_offset + 320))

    def draw_grid(self, grid_size_original, color):
        color = (color, color + 9, color + 16)
        grid_size = grid_size_original / camera[2]
        if grid_size < 64:
            return
        grid_nx = math.ceil(camera[0] / grid_size_original)
        grid_ox = (-camera[0] + grid_size_original * grid_nx) / camera[2]
        grid_ny = math.ceil(camera[1] / grid_size_original)
        grid_oy = (-camera[1] + grid_size_original * grid_ny) / camera[2]
        for i in range(math.ceil(self.WIDTH / grid_size)):
            pygame.draw.line(
                self.screen,
                color,
                (grid_ox + i * grid_size, 0),
                (grid_ox + i * grid_size, self.HEIGHT),
                1,
            )
        for i in range(math.ceil(self.HEIGHT / grid_size)):
            pygame.draw.line(
                self.screen,
                color,
                (0, grid_oy + i * grid_size),
                (self.WIDTH, grid_oy + i * grid_size),
                1,
            )

    def _check_event(self):
        global text_temp_tick, camera_animation_frames, pos_start_drag, time_start_drag, camera, is_dragging, last_mouse_pos, camera_animation_from, camera_animation_to, camera_animation_state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            # 鼠标操作
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                if event.button == 1 and self.locating_ship != True:  # 左键按下开始拖动
                    self.is_click = True
                    is_dragging = True
                    camera_animation_state = 1.0
                    time_start_drag = pygame.time.get_ticks()
                    last_mouse_pos = event.pos
                    pos_start_drag = event.pos
                elif event.button == 4:  # 滚轮向上缩放
                    camera_animation_from = camera[:]
                    delta = 0.25
                    camera_animation_to = [
                        camera[0] + camera[2] * screen_rect[2] * delta / 2,
                        camera[1] + camera[2] * screen_rect[3] * delta / 2,
                        camera[2] * (1 - delta),
                    ]
                    camera_animation_frames = 8
                    camera_animation_state = 0.0
                    # camera[0] += camera[2] * 0.05 / 2
                    # camera[1] += camera[3] * 0.05 / 2
                    # camera[2] *= 0.95
                    # camera[3] *= 0.95
                elif event.button == 5:  # 滚轮向下缩放
                    camera_animation_from = camera[:]
                    delta = 0.25
                    camera_animation_to = [
                        camera[0] - camera[2] * screen_rect[2] * delta / 2,
                        camera[1] - camera[2] * screen_rect[3] * delta / 2,
                        camera[2] * (1 + delta),
                    ]
                    camera_animation_frames = 8
                    camera_animation_state = 0.0
                    # camera[0] -= camera[2] * 0.05 / 2
                    # camera[1] -= camera[3] * 0.05 / 2
                    # camera[2] *= 1.05
                    # camera[3] *= 1.05
                else:
                    self.is_click = False
            if event.type == pygame.MOUSEBUTTONUP:
                if (
                    event.button == 1 and self.locating_ship != True and pos_start_drag
                ):  # 左键松开停止拖动
                    camera_animation_from = camera[:]
                    camera_animation_to = [
                        camera[0]
                        - (event.pos[0] - pos_start_drag[0])
                        * 100
                        * camera[2]
                        / (pygame.time.get_ticks() - time_start_drag),
                        camera[1]
                        - (event.pos[1] - pos_start_drag[1])
                        * 100
                        * camera[2]
                        / (pygame.time.get_ticks() - time_start_drag),
                        camera[2],
                    ]
                    # print(
                    #     (event.pos[0] - pos_start_drag[0])
                    #     / (pygame.time.get_ticks() - time_start_drag)
                    # )
                    camera_animation_frames = 64
                    camera_animation_state = 0.0
                    is_dragging = False

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if is_dragging and last_mouse_pos:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera[0] -= dx * camera[2]
                    camera[1] -= dy * camera[2]
                    last_mouse_pos = event.pos

            if event.type == pygame.KEYDOWN:
                # 退出游戏
                if event.key == pygame.K_q:
                    exit()

                # y键视角跟随飞船
                if event.key == pygame.K_y:
                    self.locating_ship = not self.locating_ship
                    camera_animation_state = 1.0
                    # camera[0] = self.ship.center[0] - 0.5 * camera[2]
                    # camera[1] = self.ship.center[1] - 0.5 * camera[3]

                # 重新开始游戏
                if event.key == pygame.K_r:
                    self.__init__()
                    self.locating_ship = True

                # 监测用户操作
                if event.key == pygame.K_w:
                    self.ship.push_middle = True
                if event.key == pygame.K_s:
                    self.ship.stop = True
                if event.key == pygame.K_a:
                    self.ship.push_left = True
                if event.key == pygame.K_d:
                    self.ship.push_right = True

                if event.key == pygame.K_EQUALS:
                    if self.key_plus == False:
                        if self.rate < 59049:
                            self.rate *= 3
                            play_sound(f'{self.rate:.0f}.ogg')
                        elif self.rate < 59049 * 9:
                            self.rate *= 3
                            play_sound(f'59049.ogg')
                        else:
                            play_sound('plus.ogg')
                    self.key_plus = True
                if event.key == pygame.K_MINUS:
                    if self.key_minus == False:
                        if self.rate > 1:
                            self.rate /= 3
                            try:
                                play_sound(f'{self.rate:.0f}.ogg')
                            except:
                                play_sound('59049.ogg')
                        else:
                            play_sound('minus.ogg')
                    self.key_minus = True
                if event.key == pygame.K_l:
                    self.ship.land()
                    # 更新为ship的成员函数
                    # if self.ship.landing_condition == "may land":
                    #     play_sound('challenge_complete.ogg')
                    #     self.land = True
                    # elif self.ship.landing_condition == "too far":
                    #     play_sound('buzzer.ogg')
                    #     text_temp_tick = pygame.time.get_ticks()
                    #     self.temp_message = "距离太远，无法降落"
                    # elif self.ship.landing_condition == "already landed":
                    #     play_sound('buzzer.ogg')
                    #     text_temp_tick = pygame.time.get_ticks()
                    #     self.temp_message = "已经降落在这个星球上过了"

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.ship.push_middle = False
                if event.key == pygame.K_s:
                    self.ship.stop = False
                if event.key == pygame.K_a:
                    self.ship.push_left = False
                if event.key == pygame.K_d:
                    self.ship.push_right = False
                if event.key == pygame.K_EQUALS:
                    self.key_plus = False
                if event.key == pygame.K_MINUS:
                    self.key_minus = False

    def run_game(self):
        global camera, camera_animation_from, camera_animation_to, camera_animation_state
        # 主循环
        while self.rungame:
            self._check_event()
            self.screen.fill((3, 12, 19))
            self.clock.tick(60)

            self.camera_calculate()
            self.ship.A_V()
            self.ship.calc_closest_planets(self.planets)
            self.ship.calc_main_planets(self.planets)
            self.ship.gravity_pull(self.planets)
            self.ship.atmosphere_drag(self.planets)
            self.ship.move(self.rate)

            if self.locating_ship == True:
                camera[0] = self.ship.center[0] - 0.5 * camera[2] * screen_rect[2]
                camera[1] = self.ship.center[1] - 0.5 * camera[2] * screen_rect[3]

            self.draw_grid(4000 * 5**1, 15)
            self.draw_grid(4000 * 5**2, 20)
            self.draw_grid(4000 * 5**3, 25)
            self.draw_grid(4000 * 5**4, 30)
            self.draw_grid(4000 * 5**5, 35)

            # 遍历星球列表并执行相关操作
            self.planet_excution()

            self.ship.predict(self.planets, self.rate, camera[2])
            self.ship.draw_prediction(self.screen, camera, screen_rect)
            self.ship.check_landing_conditions()
            self.ship.attempt_land(self.planets[self.ship.main_planets[0]])

            self.ship.blit_me()
            # 运行信息显示
            self.runing_info()
            pygame.display.flip()
            # 处理燃料耗尽
            if self.ship.fuel <= 0:
                self.game_over()


class Planet:
    def __init__(
        self,
        p_id,
        x,
        y,
        radius,
        mass,
        color,
        vx,
        vy,
        is_still,
        atmosphere,
        ship,
        game,
        provisions,
        typ,
    ):
        self.p_id = p_id
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.vx = vx  # 初始X速度
        self.vy = vy  # 初始Y速度
        self.is_still = is_still
        self.atmosphere = atmosphere
        self.ship = ship
        self.game = game
        self.have_achieved = False
        self.provisions = provisions
        self.typ = typ
        self.render_x = 0
        self.render_y = 0
        self.render_scale = 1
        self.draw_info_condition = False
        self.got = False

    def calc_render_position(self, draw_x, draw_y, scale):
        self.render_x = draw_x
        self.render_y = draw_y
        self.render_scale = scale
        side_factor = max(min_size, self.atmosphere["radius"] / scale)
        if self.p_id in self.ship.closest_planets and not (
            (0 - side_factor < self.render_x < self.game.WIDTH + side_factor)
            and (0 - side_factor < self.render_y < self.game.HEIGHT + side_factor)
        ):

            dx = -self.x + self.ship.center[0]
            dy = -self.y + self.ship.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            self.render_scale = distance / sqrt(self.game.HEIGHT * self.game.WIDTH) * 2
            if (self.game.WIDTH / 2 - self.render_x) != 0:
                k = (self.game.HEIGHT / 2 - self.render_y) / (
                    self.game.WIDTH / 2 - self.render_x
                )

                left_y = k * (0) - self.game.WIDTH / 2 * k + self.game.HEIGHT / 2
                right_y = (
                    k * (self.game.WIDTH)
                    - self.game.WIDTH / 2 * k
                    + self.game.HEIGHT / 2
                )
            else:
                left_y = -1
                right_y = -1
            if (self.game.HEIGHT / 2 - self.render_y) != 0:
                m = (self.game.WIDTH / 2 - self.render_x) / (
                    self.game.HEIGHT / 2 - self.render_y
                )

                up_x = m * (0) - self.game.HEIGHT / 2 * m + self.game.WIDTH / 2
                down_x = (
                    m * (self.game.HEIGHT)
                    - self.game.HEIGHT / 2 * m
                    + self.game.WIDTH / 2
                )
            else:
                up_x = -1
                down_x = -1
            # print(f"left_y{left_y,right_y,up_x,down_x,self.render_x,self.render_y}")
            if 0 <= left_y <= self.game.HEIGHT:
                if self.render_x < 0:
                    self.render_x = 0
                    self.render_y = left_y
                else:
                    self.render_x = self.game.WIDTH
                    self.render_y = right_y
            else:
                if self.render_y < 0:
                    self.render_y = 0
                    self.render_x = up_x
                else:
                    self.render_y = self.game.HEIGHT
                    self.render_x = down_x

    def draw_atmosphere(self, screen):
        draw_x = self.render_x
        draw_y = self.render_y
        if (
            draw_x < -self.atmosphere["radius"]
            or draw_x > screen_rect[2] + self.atmosphere["radius"]
            or draw_y < -self.atmosphere["radius"]
            or draw_y > screen_rect[3] + self.atmosphere["radius"]
        ):
            return
        scale = self.render_scale
        draw_x = self.render_x
        draw_y = self.render_y
        thickness = max(2, (6 - self.atmosphere["density"] / self.radius))
        colors = (
            min([int(self.color[0] / (thickness)), 255]),
            min([int(self.color[1] / (thickness)), 255]),
            min([int(self.color[2] / (thickness)), 255]),
        )
        # print(colors,thickness)
        try:
            pygame.draw.circle(
                screen,
                colors if not self.have_achieved else gray(colors),
                (int(draw_x), int(draw_y)),
                max(
                    min_size,
                    int(self.atmosphere["radius"] / scale),
                ),
            )
        except:
            pass
            # print(scale)

    def draw2(self, screen):
        scale = self.render_scale
        draw_x = self.render_x
        draw_y = self.render_y
        if (
            draw_x < -self.radius
            or draw_x > screen_rect[2] + self.radius
            or draw_y < -self.radius
            or draw_y > screen_rect[3] + self.radius
        ):
            return
        pygame.draw.circle(
            screen,
            self.color if not self.have_achieved else gray(self.color),
            (int(draw_x), int(draw_y)),
            max(min_size, int(self.radius / scale)),
        )

    def update_position(self):
        self.x += self.vx
        self.y += self.vy

    def name_render(self, screen):
        scale = self.render_scale
        if (
            0 <= self.render_x <= self.game.WIDTH
            and 0 <= self.render_y <= self.game.HEIGHT
        ):
            info = f'{self.p_id}'
            x = self.render_x - 6 * len(info)
            y = self.render_y + max(min_size, int(self.radius / scale)) + 5
            if y > self.game.HEIGHT:
                y -= 40
            if x < 0:
                x += 6 * len(info)
            if x + 12 * len(info) > self.game.WIDTH:
                x -= 6 * len(info)

            text = font_20.render(info, True, (255, 255, 255))
            screen.blit(text, (x, y))

    def crash(self):
        distance = sqrt(
            (self.x - self.ship.center[0]) ** 2 + (self.y - self.ship.center[1]) ** 2
        )
        # if self.ship.is_landed==True:
        #     if distance>=50:
        #         self.ship.is_landed=False

        if distance <= self.radius:
            # 坠机
            play_sound(f'blast1.ogg')
            self.game.game_over()
        # 进入大气圈
        # if distance<=self.radius+100:
        # if self.have_achieved == False:
        #    self.game.score+=1
        #    self.have_achieved = True

    def draw_info(self):
        # information = f"星球信息: id:{self.p_id} 半径:{int(self.radius)} 质量:{int(self.mass)} 大气层半径:{int(self.atmosphere["radius"])}"
        if not self.got:
            check_dic = {
                "fuel": "补充燃料",
                "mass": "减轻飞船质量",
                "prediction_nums": "强化预测系统",
                "prediction_steps": "增加预测步数",
                "thruster_efficiency": "引擎效率提升",
                "thruster_power": "引擎功率提升",
            }
            show_info = []
            for k in self.provisions.keys():
                show_info.append(f"{check_dic[k]} {self.provisions[k]}")

            random.shuffle(show_info)
            information2 = f"可能补给: {', '.join(show_info[:2])}"
            self.got = information2

        draw_x = (self.x - camera[0]) / camera[2]
        draw_y = (self.y - camera[1]) / camera[2] - self.radius / camera[2]
        font = font_20
        text = font.render(
            f"半径 {self.radius:.0f}({int(self.atmosphere['radius'])})",
            True,
            (255, 255, 255),
        )
        text_rect = text.get_rect()
        text_rect.center = (draw_x, draw_y - 24)
        self.game.screen.blit(text, text_rect)

        text = font.render(f"质量 {self.mass:.0f}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (draw_x, draw_y - 48)
        self.game.screen.blit(text, text_rect)

        if self.have_achieved:
            text = font.render(f"已探索", True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (draw_x, draw_y - 96)
            self.game.screen.blit(text, text_rect)

        text = font.render(self.got, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (draw_x, draw_y - 72)
        self.game.screen.blit(text, text_rect)
        # information = f"星球信息: id:{self.p_id} 半径:{int(self.radius)} 质量:{int(self.mass)} 大气层半径:{int(self.atmosphere["radius"])}"
        # self.game.temp_message = information

        # print(information)
        # draw_x = (self.x - self.radius - camera[0]) / camera[
        #     2
        # ] + self.radius / camera[2]
        # draw_y = (self.y - self.radius - camera[1]) / camera[
        #     2
        # ] + self.radius / camera[2]
        # font = pygame.font.Font(None, 24)
        # text = font.render(f"radius:{self.radius:.2f} mass:{self.mass:.2f}", True, (30, 100, 60))
        # text_rect = text.get_rect()
        # text_rect.center = (draw_x,draw_y)
        # self.game.screen.blit(text, text_rect)


class Ship:
    def __init__(self, game):
        # 获取屏幕状态
        self.s_f = 0.001
        self.game = game
        self.screen = game.screen
        self.screen_rect = game.screen.get_rect()
        self.image = pygame.image.load("assets/ship_000_0.png")
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.center = [
            self.screen_rect.width / 2,
            self.screen_rect.height / 2,
        ]

        # 各推进器状态
        self.stop = False
        self.push_middle = False
        self.push_left = False
        self.push_right = False

        self.angle = 0.0  # 表示飞船角度
        self.rotation_speed = 0.0  # 飞船旋转速度
        self.direction = [0.0, 0.0]  # 依次为x y轴方向
        self.acceleration = 0.0  # 加速度
        self.velocity = [0.0, 0.0, 0.0]  # 依次为v v_x v_y
        self.main_planets = [0] * 5
        self.closest_planets = [0] * 5
        self.mass = 100  # 质量，用于计算加速度
        self.mass_balance = 100
        self.friction_factor = 1e-8  # 大气层的摩擦系数
        self.air_s = 1  # 受到空气摩擦力的飞船面积
        self.force_x = 0
        self.force_y = 0
        self.fuel = 10000  # 燃料
        self.thruster_power = 100
        self.thruster_efficiency = 100
        self.thruster_efficiency_balance = self.thruster_efficiency
        self.prediction_steps = 600
        self.prediction_nums = 16
        self.landing_pod_weight = 5
        self.landing_condition = "too far"
        self.is_land = False
        self.other_forces = [0, 0]
        # 避免重新启动时找不到new_image
        self.new_image = pygame.transform.scale(
            self.image,
            (
                # 避免在宇宙视角下过小
                max([self.width / 3, self.width / camera[2]]),
                max([self.height / 3, self.height / camera[2]]),
            ),
        )
        self.new_image = pygame.transform.rotate(
            self.new_image, self.angle * 180.0 / pi
        )

    def A_V(self):
        # 响应用户输入
        self.image = pygame.image.load(
            f"assets/ship_{int(self.push_left)}{int(self.push_middle)}{int(self.push_right)}_{int(self.stop)}.png"
        )

        s_f = self.s_f * self.thruster_power
        if self.push_middle == True:
            if self.push_left == True and self.push_right == True:
                self.acceleration = 0.5 * s_f
                self.rotation_speed = 0.0
            elif self.push_left == True and self.push_right == False:
                self.acceleration = 0.4 * s_f
                self.rotation_speed = 0.03
            elif self.push_left == False and self.push_right == True:
                self.acceleration = 0.4 * s_f
                self.rotation_speed = -0.03
            elif self.push_left == False and self.push_right == False:
                self.acceleration = 0.3 * s_f
                self.rotation_speed = 0.0
        else:
            if self.push_left == True and self.push_right == True:
                self.acceleration = 0.2 * s_f
                self.rotation_speed = 0.0
            elif self.push_left == True and self.push_right == False:
                self.acceleration = 0.0 * s_f
                self.rotation_speed = 0.03
            elif self.push_left == False and self.push_right == True:
                self.acceleration = 0.0 * s_f
                self.rotation_speed = -0.03
            elif self.push_left == False and self.push_right == False:
                self.acceleration = 0.0 * s_f
                self.rotation_speed = 0.0
        if self.stop == True:
            if self.velocity[0] >= 0:
                # self.velocity[1]*=0.95
                # self.velocity[2]*=0.95
                self.acceleration = -0.2 * s_f

        self.force_x += self.direction[1] * self.acceleration
        self.force_y += self.direction[0] * self.acceleration
        self.fuel -= self.rotation_speed / (
            self.thruster_efficiency / self.thruster_efficiency_balance
        )
        if self.acceleration > 0:
            self.fuel -= (
                self.acceleration
                / (self.thruster_efficiency / self.thruster_efficiency_balance)
                * self.game.rate
            )
        elif self.acceleration < 0:
            self.fuel += (
                self.acceleration
                / (self.thruster_efficiency / self.thruster_efficiency_balance)
                * self.game.rate
            )
        self.velocity[0] = sqrt(self.velocity[1] ** 2 + self.velocity[2] ** 2.0)

        # 调整飞船姿态
        self.angle += self.rotation_speed
        self.direction = [cos(self.angle), sin(self.angle)]
        # self.new_image = pygame.transform.rotate(self.image, self.angle * 180.0 / pi)
        self.new_image = pygame.transform.scale(
            self.image,
            (
                # 避免在宇宙视角下过小
                max([self.width / 3, self.width / camera[2]]),
                max([self.height / 3, self.height / camera[2]]),
            ),
        )
        self.new_image = pygame.transform.rotate(
            self.new_image, self.angle * 180.0 / pi
        )

    def move(self, rate):
        self.velocity[2] += self.force_x / (self.mass / self.mass_balance) * rate
        self.velocity[1] += self.force_y / (self.mass / self.mass_balance) * rate
        # 更新飞船位置
        self.velocity[0] = sqrt(self.velocity[2] ** 2 + self.velocity[1] ** 2)
        self.center[0] -= self.velocity[2] * rate  # x
        self.center[1] -= self.velocity[1] * rate  # y
        self.force_x = 0
        self.force_y = 0

    def blit_me(self):
        if camera[2] > 3:
            rect_ship = get_bounding_rect(
                self.width / 3 * camera[2], self.height / 3 * camera[2], self.angle
            )
        else:
            rect_ship = get_bounding_rect(self.width, self.height, self.angle)
        display_rect = pygame.Rect(
            self.center[0] + rect_ship[0],
            self.center[1] + rect_ship[1],
            rect_ship[2],
            rect_ship[3],
        )
        x = Decimal((display_rect[0] - camera[0]) / camera[2])
        y = Decimal((display_rect[1] - camera[1]) / camera[2])
        display_rect[0] = float(x)
        display_rect[1] = float(y)
        display_rect[2] /= camera[2]
        display_rect[3] /= camera[2]
        self.screen.blit(self.new_image, display_rect)

    def gravity_pull(self, planets):
        for j, planet in enumerate(planets):

            dx = -planet.x + self.center[0]
            dy = -planet.y + self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:  # 避免除以零

                force = (
                    G * planet.mass * (self.mass / self.mass_balance) / (distance**2)
                )

                ax = force * dx / distance
                ay = force * dy / distance
                self.force_x += ax
                self.force_y += ay

    def calc_closest_planets(self, planets, nums="use_default"):  # 最近星球的编号
        nums = 15
        # print(self.main_planets)

        nums = min(nums, len(planets))
        temp_closes = [[1e15, 0].copy() for i in range(nums)]
        for j, planet in enumerate(planets):

            dx = -planet.x + self.center[0]
            dy = -planet.y + self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:  # 避免除以零

                for i in range(nums):
                    if distance < temp_closes[i][0]:
                        # print(force)
                        temp_closes.insert(i, [distance, planet.p_id])
                        temp_closes.pop(-1)
                        break

        self.closest_planets = [t[1] for t in temp_closes]

    def calc_main_planets(
        self, planets, nums="use_default"
    ):  # 得到主要影响的星球的编号
        if nums == "use_default":
            nums = self.prediction_nums
        # print(self.main_planets)
        total_forces = [0, 0]
        nums = min(nums, len(planets))
        temp_mains = [[0, 0, 0, 0].copy() for _ in range(nums)]
        for j, planet in enumerate(planets):

            dx = -planet.x + self.center[0]
            dy = -planet.y + self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:  # 避免除以零

                force = (
                    G * planet.mass * (self.mass / self.mass_balance) / (distance**2)
                )
                x_force = force * dx / distance
                y_force = force * dy / distance
                total_forces[0] += x_force
                total_forces[1] += y_force
                for i in range(nums):
                    if force > temp_mains[i][0]:
                        # print(force)
                        temp_mains.insert(i, [force, planet.p_id, x_force, y_force])
                        temp_mains.pop(-1)
                        break
        self.other_forces = [
            total_forces[0] - sum([t[2] for t in temp_mains]),
            total_forces[1] - sum([t[3] for t in temp_mains]),
        ]

        self.main_planets = [t[1] for t in temp_mains]

    def predict(self, planets, rate, scale, steps="use_default"):
        enhance_factor = 5
        if steps == "use_default":
            steps = self.prediction_steps
        v_x = self.center[0]
        v_y = self.center[1]
        v_force_x = self.force_x
        v_force_y = self.force_y
        v_x_v = self.velocity[2]
        v_y_v = self.velocity[1]
        v_x_v += (
            v_force_x / (self.mass / self.mass_balance) * sqrt(scale) * enhance_factor
        )
        v_y_v += (
            v_force_y / (self.mass / self.mass_balance) * sqrt(scale) * enhance_factor
        )
        v_x -= v_x_v * sqrt(scale) * enhance_factor  # x
        v_y -= v_y_v * sqrt(scale) * enhance_factor  # y
        v_force_x = 0
        v_force_y = 0
        temp_predictions = []
        temp_predictions.append((v_x, v_y))
        end = False
        for i in range(steps):
            if end:
                break
            v_force_x += self.other_forces[0]
            v_force_y += self.other_forces[1]
            for j, planet in enumerate([planets[t] for t in self.main_planets]):

                dx = -planet.x + v_x
                dy = -planet.y + v_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < planet.atmosphere["radius"]:
                    end = True
                if distance > 0:  # 避免除以零

                    force = (
                        G
                        * planet.mass
                        * (self.mass / self.mass_balance)
                        / (distance**2)
                    )

                    ax = force * dx / distance
                    ay = force * dy / distance
                    v_force_x += ax
                    v_force_y += ay
            v_x_v += (
                v_force_x
                / (self.mass / self.mass_balance)
                * sqrt(scale)
                * enhance_factor
            )
            v_y_v += (
                v_force_y
                / (self.mass / self.mass_balance)
                * sqrt(scale)
                * enhance_factor
            )
            v_x -= v_x_v * sqrt(scale) * enhance_factor  # x
            v_y -= v_y_v * sqrt(scale) * enhance_factor  # y
            v_force_x = 0
            v_force_y = 0
            temp_predictions.append((v_x, v_y))
        self.prediction = temp_predictions

    def draw_prediction(self, screen, camera, screen_rect):
        for pre in self.prediction:
            x1 = pre[0]
            y1 = pre[1]
            draw_x = (x1 - camera[0]) / (camera[2])
            draw_y = (y1 - camera[1]) / (camera[2])
            try:
                pygame.draw.circle(
                    screen, (160, 164, 167), (int(draw_x), int(draw_y)), 1
                )
            except:
                pass

    def atmosphere_drag(self, planets):
        planet = planets[self.main_planets[0]]
        atmosphere_radius = planet.atmosphere["radius"]
        atmosphere_density = planet.atmosphere["density"]
        atmosphere_type = planet.atmosphere["type"]
        distance_2 = (self.center[0] - planet.x) ** 2 + (self.center[1] - planet.y) ** 2
        if atmosphere_radius - planet.radius == 0:  # 无大气
            return
        place_factor = 1 - (math.sqrt(distance_2) - planet.radius) / (
            atmosphere_radius - planet.radius
        )  # 深入大气层程度
        if distance_2 < atmosphere_radius**2:
            if atmosphere_type == "A":  # 大气层密度线性衰减
                force_x = (
                    self.velocity[2]
                    * self.air_s
                    * self.friction_factor
                    * atmosphere_density
                    * place_factor
                )
                force_y = (
                    self.velocity[1]
                    * self.air_s
                    * self.friction_factor
                    * atmosphere_density
                    * place_factor
                )
                self.force_x += -force_x
                self.force_y += -force_y

    # def stats_change(self,stats):
    #     # dic={
    #     "thruster_power":self.thruster_power,
    #     "mass":self.mass,
    #     "friction_factor":self.friction_factor,
    #     "fuel":self.fuel,
    #     "air_s":self.air_s,
    #     "thruster_efficiency":self.thruster_efficiency
    # }
    # for k in stats.keys():
    #     dic[k]+=stats[k]

    def land(self):
        global text_temp_tick
        if self.landing_condition == "may land":
            play_sound('challenge_complete.ogg')
            self.is_land = True
        elif self.landing_condition == "too far":
            play_sound('buzzer.ogg')
            text_temp_tick = pygame.time.get_ticks()
            self.game.temp_message = "距离太远，无法降落"
        elif self.landing_condition == "already landed":
            play_sound('buzzer.ogg')
            text_temp_tick = pygame.time.get_ticks()
            self.game.temp_message = "已经降落在这个星球上过了"

    def check_landing_conditions(self):
        planet = self.game.planets[self.main_planets[0]]
        dx = -planet.x + self.center[0]
        dy = -planet.y + self.center[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 2 * planet.radius:
            self.landing_condition = "too far"
        elif planet.have_achieved:
            self.landing_condition = "already landed"
        else:
            self.landing_condition = "may land"

    def attempt_land(self, planet: Planet):
        global text_temp_tick
        if planet.typ == "terrestrial":
            dx = -planet.x + self.center[0]
            dy = -planet.y + self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            takeoff_gravity_cost = (
                planet.mass
                * G
                * self.landing_pod_weight
                * (distance - planet.radius)
                / 1e11
                / 3
            )
            takeoff_speed_cost = (
                self.velocity[0] ** 2 * self.landing_pod_weight / 1e3 / 3
            )
            takeoff_friction_cost = (
                (planet.atmosphere["radius"] - planet.radius)
                * self.velocity[0]
                * planet.atmosphere["density"]
                / 1e11
            )
            msg_provisions = []
            for k in planet.provisions.keys():
                match k:
                    case 'fuel':
                        msg_provisions.append(f"燃料 {planet.provisions[k]:.2f}")
                    case 'thruster_power':
                        msg_provisions.append(f"引擎功率 {planet.provisions[k]:.2f}")
                    case 'thruster_efficiency':
                        msg_provisions.append(f"引擎效率 {planet.provisions[k]:.2f}")
                    case 'mass':
                        msg_provisions.append(f"飞船质量 {planet.provisions[k]:.0f}")
                    case 'prediction_steps':
                        msg_provisions.append(f"预测步数 {planet.provisions[k]:.0f}")
                    case 'prediction_nums':
                        msg_provisions.append(f"强化预测 {planet.provisions[k]:.0f}")
            self.game.message2 = f"最近的星球:  {'类地行星' if planet.typ=='terrestrial' else '气体巨行星'}   半径: {planet.radius:.2f}   补给: [{', '.join(msg_provisions)}]   PID: {planet.p_id}"
            # self.game.message=f"takeoff_gravity_cost{takeoff_gravity_cost:.2f}takeoff_speed_cost{takeoff_speed_cost:.2f},takeoff_friction_cost{takeoff_friction_cost:.2f}"
            if self.landing_condition == "may land":
                self.game.message = f"降落消耗燃料: {takeoff_gravity_cost+takeoff_speed_cost+takeoff_friction_cost:.2f}"
            elif self.landing_condition == "already landed":
                self.game.message = f"已经降落过了"
            else:
                self.game.message = f"无法降落"

            if not self.is_land:
                return
            self.fuel -= takeoff_gravity_cost
            self.fuel -= takeoff_speed_cost
            self.fuel -= takeoff_friction_cost

            planet.have_achieved = True

            stats = planet.provisions

            if len(stats.keys()) > 0:
                for k in stats.keys():
                    exec(f"self.{k}+={stats[k]}")
                # print(stats)

            planet.provisions = {}
            self.is_land = False
            text_temp_tick = pygame.time.get_ticks()
            self.game.temp_message = f"降落成功，获得[{', '.join(msg_provisions)}]"
            self.game.score += 1
            planet.got = ""

        elif planet.typ == "gas_giant":
            dx = -planet.x + self.center[0]
            dy = -planet.y + self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            takeoff_gravity_cost = max(
                10,
                planet.mass
                * G
                * self.landing_pod_weight
                * (distance - planet.atmosphere["radius"])
                / 1e11
                / 3,
            )
            # takeoff_speed_cost = self.velocity[0] ** 2 * self.landing_pod_weight / 1e3 / 3
            # takeoff_friction_cost = (planet.atmosphere["radius"] - planet.radius) * self.velocity[0] * \
            #                       planet.atmosphere["density"] / 1e11
            msg_provisions = []
            for k in planet.provisions.keys():
                match k:
                    case 'fuel':
                        msg_provisions.append(f"燃料 {planet.provisions[k]:.2f}")
                    case 'thruster_power':
                        msg_provisions.append(f"引擎功率 {planet.provisions[k]:.2f}")
                    case 'thruster_efficiency':
                        msg_provisions.append(f"引擎效率 {planet.provisions[k]:.2f}")
                    case 'mass':
                        msg_provisions.append(f"飞船质量 {planet.provisions[k]:.0f}")
                    case 'prediction_steps':
                        msg_provisions.append(f"预测步数 {planet.provisions[k]:.0f}")
                    case 'prediction_nums':
                        msg_provisions.append(f"强化预测 {planet.provisions[k]:.0f}")
            self.game.message2 = f"最近的星球:  {'类地行星' if planet.typ=='terrestrial' else '气体巨行星'}   半径: {planet.radius:.2f}   补给: [{', '.join(msg_provisions)}]   PID: {planet.p_id}"
            # self.game.message=f"takeoff_gravity_cost{takeoff_gravity_cost:.2f}takeoff_speed_cost{takeoff_speed_cost:.2f},takeoff_friction_cost{takeoff_friction_cost:.2f}"
            if self.landing_condition == "may land":
                self.game.message = f"大气层采集消耗燃料: {takeoff_gravity_cost :.2f}"
            elif self.landing_condition == "already landed":
                self.game.message = f"已经采集过了"
            else:
                self.game.message = f"无法采集"

            if not self.is_land:
                return
            self.fuel -= takeoff_gravity_cost

            planet.have_achieved = True

            stats = planet.provisions

            if len(stats.keys()) > 0:
                for k in stats.keys():
                    exec(f"self.{k}+={stats[k]}")
                # print(stats)

            planet.provisions = {}
            self.is_land = False
            text_temp_tick = pygame.time.get_ticks()
            self.game.temp_message = f"降落成功，获得[{', '.join(msg_provisions)}]"
            self.game.score += 1
            planet.got = ""


if sys.platform == 'win32':
    # 避免高分屏下缩放导致的模糊
    # Sources included from:
    # lines 63 to 71 of pyscreeze/__init__.py
    import ctypes

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

if __name__ == "__main__":
    game = Cosmoseek()
    game.run_game()
