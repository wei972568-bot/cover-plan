#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面计划 · 像素测量分析器（读图链路的「辅」）
=================================================

本模块是 skill「读图 → 挑拓扑 → 定制」链路中的**像素辅助**：用纯像素（PIL）
客观测量照片的定量特征，产出 image_features 契约——与
scripts/topology_registry.py 的 topology_supports() **逐键对齐**，供挑拓扑使用。

【分工（用户拍板）】
  模型识图（主） = 智能体 read_image，负责题材/脸/气质/昼夜/场景等**定性**判断；
  像素测量（辅） = 本模块，负责主体位置/留白/亮度/构图/曝光等**客观数值**。
  二者合并为 image_features → topology_supports() 挑拓扑。

【image_features 契约（键名与 topology_registry docstring 严格一致）】
  subject_zone : {'h':'left|center|right','v':'top|center|bottom'}  主体位置
  whitespace   : {'top','bottom','left','right'} 各边带留白占比 0~1
  brightness   : {'top','bottom'} 顶部/底部平均亮度 0~255
  composition  : 'centered|vertical|horizontal|diagonal|symmetry'
  highkey      : bool          是否高调白（死白/白墙）
  exposure     : 'highkey|lowkey|normal'        曝光倾向
  height_ratio : float         主体/内容高度占比

【无第三方依赖】只用 PIL（selector.py 同款），不引 numpy。图像损坏/不可读时降级为中性特征
（PIL 本身是硬依赖：脚本顶部 `from PIL import Image`，缺 PIL 会直接 import 失败）。
"""
import argparse
import json
from PIL import Image

N = 64  # 测量网格分辨率（越大越细；64 已足够区分方位/留白/构图，且快）


# ------------------------------------------------------------------
# 底层：亮度场 + 边缘能量场
# ------------------------------------------------------------------
def _field(path):
    """返回 (edge_field, px, mean, std)。

    edge_field: N×N 二维数组，每格 = 相邻像素亮度差之和（度量「内容/细节」密度）。
    px: N*N 亮度列表；mean/std: 全图亮度均值/标准差。
    """
    im = Image.open(path).convert('L').resize((N, N))
    px = list(im.getdata())
    field = [[0.0] * N for _ in range(N)]
    for y in range(N):
        row = y * N
        nxt = (y + 1) * N if y + 1 < N else row
        for x in range(N):
            base = px[row + x]
            gx = abs(base - px[row + (x + 1 if x + 1 < N else x)])
            gy = abs(base - px[nxt + x])
            field[y][x] = gx + gy
    mean = sum(px) / len(px)
    std = (sum((v - mean) ** 2 for v in px) / len(px)) ** 0.5
    return field, px, mean, std


def _flat_threshold(field):
    """平坦阈值：低于此的格子视为「平坦」（留白/细节少）→ 相对阈值，随图自动适应。"""
    vals = [c for row in field for c in row]
    mean = sum(vals) / len(vals) if vals else 0.0
    return max(mean * 0.5, 3.0)


def _corr(a, b):
    """Pearson 相关系数（缺 numpy 的纯 Python 版）。n<2 或零方差返回 0。"""
    n = min(len(a), len(b))
    if n < 2:
        return 0.0
    ma = sum(a[:n]) / n
    mb = sum(b[:n]) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = (sum((a[i] - ma) ** 2 for i in range(n))) ** 0.5
    db = (sum((b[i] - mb) ** 2 for i in range(n))) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


# ------------------------------------------------------------------
# 测量
# ------------------------------------------------------------------
def measure(path):
    """测量一张图，返回 image_features 契约 dict（键全部对齐 topology_supports）。"""
    try:
        field, px, mean, std = _field(path)
    except Exception:
        # PIL 读不了/损坏 → 降级为中性特征（供挑拓扑的『保守』兜底，不透传异常）
        return {
            'subject_zone': {'h': 'center', 'v': 'center'},
            'whitespace': {'top': 0.25, 'bottom': 0.25, 'left': 0.25, 'right': 0.25},
            'brightness': {'top': 128, 'bottom': 128},
            'composition': 'centered',
            'highkey': False,
            'exposure': 'normal',
            'height_ratio': 0.5,
        }

    th = _flat_threshold(field)

    # ---- 内容格（细节密度 ≥ 阈值）＝ 主体/前景 ----
    content = []
    cx_s = cy_s = 0
    for y in range(N):
        for x in range(N):
            if field[y][x] >= th:
                content.append((x, y))
                cx_s += x
                cy_s += y
    if content:
        xs = [c[0] for c in content]
        ys = [c[1] for c in content]
        cx = cx_s / len(content)
        cy = cy_s / len(content)
        miny, maxy = min(ys), max(ys)
        height_ratio = (maxy - miny + 1) / N
    else:
        xs = [N // 2]
        ys = [N // 2]
        cx = cy = N // 2
        height_ratio = 0.0

    # ---- subject_zone：内容重心方位 ----
    h = 'center'
    if cx < N * 0.35:
        h = 'left'
    elif cx > N * 0.65:
        h = 'right'
    v = 'center'
    if cy < N * 0.35:
        v = 'top'
    elif cy > N * 0.65:
        v = 'bottom'

    # ---- whitespace：四边带「平坦格」占比 ----
    def band_flat(x0, x1, y0, y1):
        tot = flat = 0
        for yy in range(max(0, y0), min(N, y1)):
            for xx in range(max(0, x0), min(N, x1)):
                tot += 1
                if field[yy][xx] < th:
                    flat += 1
        return flat / tot if tot else 0.0

    top_w = band_flat(0, N, 0, int(N * 0.12))
    bot_w = band_flat(0, N, int(N * 0.88), N)
    left_w = band_flat(0, int(N * 0.12), 0, N)
    right_w = band_flat(int(N * 0.88), N, 0, N)

    # ---- brightness：上/下三分之一平均亮度 ----
    def band_mean(y0, y1):
        s = c = 0
        for yy in range(max(0, int(y0)), min(N, int(y1))):
            for xx in range(N):
                s += px[yy * N + xx]
                c += 1
        return s / c if c else 0.0

    bright_top = band_mean(0, int(N * 0.33))
    bright_bot = band_mean(int(N * 0.66), N)

    # ---- highkey / exposure ----
    highkey = mean > 180 and std < 78
    if mean > 185:
        exposure = 'highkey'
    elif mean < 82:
        exposure = 'lowkey'
    else:
        exposure = 'normal'

    # ---- composition（尽力而为的提示；低权重，挑拓扑主要用 subject/whitespace/brightness）----
    col_e = [sum(field[y][x] for y in range(N)) for x in range(N)]
    sym = _corr(col_e, col_e[::-1])

    comp = 'centered'
    if top_w > 0.30 and bot_w > 0.30 and h == 'center':
        comp = 'vertical'      # 上下留白、主体居中 → 天地呼应
    elif left_w > 0.25 and right_w > 0.25:
        comp = 'horizontal'    # 左右留白 → 横贯
    diag = abs(_corr(xs, ys)) if len(xs) > 1 else 0.0
    if diag > 0.55 and not (h == 'center' and v == 'center'):
        comp = 'diagonal'      # 内容沿对角线分布
    elif sym > 0.90 and h == 'center' and comp == 'centered':
        comp = 'symmetry'      # 左右镜像对称 + 主体居中

    return {
        'subject_zone': {'h': h, 'v': v},
        'whitespace': {'top': round(top_w, 3), 'bottom': round(bot_w, 3),
                       'left': round(left_w, 3), 'right': round(right_w, 3)},
        'brightness': {'top': round(bright_top, 1), 'bottom': round(bright_bot, 1)},
        'composition': comp,
        'highkey': bool(highkey),
        'exposure': exposure,
        'height_ratio': round(height_ratio, 3),
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='像素测量 → image_features 契约（读图辅路）')
    p.add_argument('--photo', required=True, help='照片路径')
    p.add_argument('--json-out', default=None, help='把结果写到该文件（可选；默认打 stdout）')
    a = p.parse_args()
    feat = measure(a.photo)
    text = json.dumps(feat, ensure_ascii=False)
    if a.json_out:
        with open(a.json_out, 'w', encoding='utf-8') as f:
            f.write(text)
        print('已写出:', a.json_out)
    else:
        print(text)
