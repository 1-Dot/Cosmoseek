import math


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
