import math

import pygame


def get_bounding_rect(width, height, angle):
    # 矩形的初始顶点（以中心为原点）
    corners = [
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    ]
    # 旋转角度的正弦和余弦
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # 旋转顶点
    rotated_corners = [
        (x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in corners
    ]
    # 计算最小外接矩形
    min_x = min(p[0] for p in rotated_corners)
    max_x = max(p[0] for p in rotated_corners)
    min_y = min(p[1] for p in rotated_corners)
    max_y = max(p[1] for p in rotated_corners)
    # 新矩形的宽高
    new_width = max_x - min_x
    new_height = max_y - min_y
    return (min_x, min_y, new_width, new_height)


def play_sound(name):
    sound = pygame.mixer.Sound(f'assets/{name}')
    sound.play()


def gray(color):
    # 获取一个颜色的灰度 (稍微压暗)
    r, g, b = color
    gray = int((r * 299 + g * 587 + b * 114) / 1000.0 * 0.67)
    return (gray, gray, gray)
