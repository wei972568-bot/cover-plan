#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面计划 · 共享排版守卫（type_guard）
=====================================
被四个渲染器（engine_v2 / matting_engine / metaphor_engine / blueprint_engine）共同 import，
把三类排版兜底的计算逻辑集中到一处（见 `docs/引擎排版健壮性-设计.md`）：

  ① 宽度/高度自适应字号  `fit_title_fs` —— 长标题不右缘溢出；配合 `max_h` 不被 band 的
     `overflow:hidden` 上下裁。
  ② 落点亮度感知对比守卫  `readability` —— 按文字落区背景亮度自动选亮/暗字 + 足够可读的
     描边/阴影，修"深字压深底（stone 夜景）"这类历史问题。
  ③ clip-safe 安全边距   `clip_safe` —— 把定位值夹到画布安全区间，防 footer/标题触画布边/被裁。

另附 `luma`（亮度 0~255）与 `_is_cjk`（CJK 判定，供 fit 估算字宽）。

**边界（设计 §3）**：本模块只收敛"守卫函数"的计算逻辑；`FONTS_CSS / _serif_cn / _sans_cn`
等 5 份字体串**不在本期收敛范围**（影响面大，设计明文列入后续清理）。
本模块不依赖 PIL / 无第三方依赖，可被任意引擎 import。
"""

import math

# ---- CJK 判定（同 engine_v2._is_cjk；fit_title_fs 按 CJK≈1.0em、其它≈0.55em 估算宽）----
_RANGE_CJK = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF))


def _is_cjk(ch):
    """是否为 CJK 汉字（扩展A / 统一表意 / 兼容区）。"""
    o = ord(ch)
    return any(a <= o <= b for a, b in _RANGE_CJK)


# ------------------------------------------------------------------
# ① 宽度/高度自适应字号
# ------------------------------------------------------------------
def luma(hexcolor):
    """0-255 亮度（Rec.601 加权：0.2126R+0.7152G+0.0722B）。

    支持 '#'/#/无#' 的 rrggbb / rgb 简写，以及 'rgb(r,g,b)' / 'rgba(r,g,b,a)' 形式
    （rgba 只取 rgb 三分量，忽略 alpha——用于 gold 等半透明色）。非法输入视为黑（0）。
    """
    s = str(hexcolor).strip()
    # rgba/rgb 形式
    if s.lower().startswith('rgb'):
        inner = s[s.index('(') + 1:s.index(')')]
        parts = inner.split(',')[:3]
        try:
            r, g, b = (float(p) for p in parts)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        except (ValueError, IndexError):
            return 0.0
    # hex 形式
    try:
        h = s.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    except (ValueError, IndexError):
        return 0.0


def _letter_px(letter, fs):
    """letter-spacing 字符串（'0.3em'）转 px；非 '..em' 形式返回 0。"""
    if not letter:
        return 0.0
    s = str(letter).strip()
    if s.endswith('em'):
        try:
            return float(s[:-2]) * fs
        except ValueError:
            return 0.0
    return 0.0


def fit_title_fs(title, container_w, base_fs, letter='0em', pad=0.0, max_h=None, line_h=1.0):
    """自适应标题字号（把 engine_v2._fit_title_fs 收敛到共享守卫，并加可选 `max_h` 垂直收敛）。

    估算 title 在 base_fs 下的渲染宽（保守从宽）：CJK≈1.0em、西文/数字/空格≈0.65em
    （2026-09-04 评审 #4 钉死：0.55 对宽体/粗黑 display 字体不保守，估窄会漏缩放 → 溢出；
    0.65 偏保守只多缩不漏缩。逐字体宽度表列为后续。）
    每字符另加 letter-spacing；外边框再留 `pad`。超 `container_w` → 按比例缩字号（下限 12px，
    **⑨ 接受现状**，超长标题以实测兜底，不加 wrap/elide/截断）。

    `max_h`（可选）：对固定在 `band_h` 内的文字（如 matting `.band`），按
    "字符行数 × 行高 ≤ max_h"再收敛一次，防垂直裁切（配合 `overflow:hidden`）。
    `line_h`：行高倍数（matting `.t` 用 1.14；默认 1.0）。

    返回 int 字号（下限 12px）。估算偏保守（宁可略小）。
    """
    def _w(fs):
        ls = _letter_px(letter, fs)
        total = 0.0
        for ch in title:
            total += (fs if _is_cjk(ch) else 0.65 * fs) + ls
        return total + pad

    if base_fs <= 10:
        return int(base_fs)
    if _w(base_fs) <= container_w:
        fs = int(base_fs)
    else:
        scale = container_w / _w(base_fs)
        fs = max(int(base_fs * scale), 12)

    if max_h is not None and max_h > 0:
        # 垂直收敛：_w 随 fs 线性，按比例缩一次即可收敛到 max_h 内（再夹 12px 下限）。
        avail = max(float(container_w), 1.0)
        lines = max(1, int(math.ceil(_w(fs) / avail)))
        h = lines * fs * line_h
        if h > max_h:
            fs = max(int(fs * (max_h / h)), 12)
    return fs


# ------------------------------------------------------------------
# ② 落点亮度感知对比守卫
# ------------------------------------------------------------------
_DARK_BG = 70.0      # 暗底阈值：bg_luma < 70 → 用亮字 + 发光/暗描边
_BRIGHT_BG = 185.0   # 亮底阈值：bg_luma > 185 → 用深字 + 柔影
_LIGHT_INK = 140.0   # 基准 ink 亮度：>140 视为浅字（中间调用暗影），否则视为深字（用亮影）

# 暗底需亮字 / 亮底需深字时的锚点色（暖白/暖黑，兼顾多数素描基调；不依赖各 palette）
_LIGHT_ANCHOR = '#f6f2e8'
_DARK_ANCHOR = '#1f2328'

# bg_luma 未知时的"双影兜底"：白描边 + 黑阴影叠加，任意深浅底都保底可读
_UNKNOWN_SHADOW = '0 0 4px rgba(255,255,255,.85),0 0 8px rgba(0,0,0,.8),0 1px 2px rgba(0,0,0,.85)'


def readability(ink, bg_luma=None):
    """落点亮度感知的对比守卫。返回 `{'color': 文字色, 'shadow': CSS text-shadow 值}`。

    - `ink`：基准文字色（hex）。
    - `bg_luma`：文字落点背景亮度（0~255）。**None = 未知**（无像素数据），走双影兜底。
    - bg_luma 已知：
        暗底（< ~70）→ 亮字 + 发光/暗描边（基准 ink 本身也暗则翻成亮字 `_LIGHT_ANCHOR`）；
        亮底（> ~185）→ 深字 + 柔影（基准 ink 本身也亮则翻成深字 `_DARK_ANCHOR`）；
        中间（70~185）→ 保持基准 ink，按 ink 明暗加对比影（同原 `_ct` 逻辑）。
    - bg_luma 未知 → 保持基准 ink + 足够强的双影兜底（不"白字压白/黑字压黑"）。
    """
    i = luma(ink)
    if bg_luma is None:
        return {'color': ink, 'shadow': _UNKNOWN_SHADOW}
    if bg_luma < _DARK_BG:
        # 暗底：亮字 + 发光/暗描边；基准 ink 也是深字 → 翻成亮字锚点
        color = ink if i > _LIGHT_INK else _LIGHT_ANCHOR
        shadow = '0 0 5px rgba(255,255,255,.35),0 0 14px rgba(0,0,0,.85),0 1px 3px rgba(0,0,0,.9)'
        return {'color': color, 'shadow': shadow}
    if bg_luma > _BRIGHT_BG:
        # 亮底：深字 + 柔影；基准 ink 也是浅字 → 翻成深字锚点
        color = ink if i < 100.0 else _DARK_ANCHOR
        shadow = '0 1px 3px rgba(0,0,0,.5),0 0 10px rgba(255,255,255,.5)'
        return {'color': color, 'shadow': shadow}
    # 中间调：保持基准 ink，按 ink 明暗加对比影
    if i > _LIGHT_INK:
        shadow = '0 0 6px rgba(0,0,0,.85),0 0 14px rgba(0,0,0,.55)'
    else:
        shadow = '0 0 6px rgba(255,255,255,.7),0 0 14px rgba(255,255,255,.4)'
    return {'color': ink, 'shadow': shadow}


# ------------------------------------------------------------------
# ③ clip-safe 安全边距
# ------------------------------------------------------------------
def clip_safe(v, edge, pad):
    """把定位值 `v`（相对画布，px）夹到安全区间 `[pad, edge-pad]`。

    用于把 footer/标题/文字带的定位值拉到画布内安全边距（防触边/被 `overflow:hidden` 裁）。
    - `edge`：相关画布方向尺寸（如 H）。
    - `pad`：安全边距（px）。
    - `v` 为负数或超边（如 `bottom` 定位值过大）时同样夹回。
    """
    try:
        lo, hi = float(pad), float(edge) - float(pad)
    except (TypeError, ValueError):
        return int(v)
    if hi <= lo:
        return int(edge / 2)
    return int(max(lo, min(v, hi)))


if __name__ == '__main__':
    # 自检：几个代表性断言（供工程回归）
    assert luma('#000000') == 0
    assert luma('#ffffff') > 250
    assert luma('#1c150c') < 70          # stone 深墨
    assert fit_title_fs('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 500, 100) >= 12
    assert fit_title_fs('短', 500, 100) == 100
    assert fit_title_fs('北京', 500, 100, '0em') == 100      # 2 CJK × 100 = 200 < 500 → 不缩
    # CJK×10 字 × 100px = 1000 → 500 宽 → fs≈50
    assert 45 <= fit_title_fs('中华人民共和国万岁', 500, 100, '0em') <= 55
    # max_h 垂直收敛：超长英文在窄容器、高度受限时再缩
    _fs = fit_title_fs('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 200, 60, '0em', max_h=90, line_h=1.14)
    assert 12 <= _fs <= 60
    r = readability('#1c150c', 30)        # 暗底深墨 → 翻亮字 + 发光
    assert r['color'] != '#1c150c' and r['shadow']
    assert readability('#1c150c', None)['color'] == '#1c150c'   # 未知底 → 保持 ink + 双影
    assert clip_safe(-10, 1000, 50) == 50
    assert clip_safe(2000, 1000, 50) == 950
    assert clip_safe(300, 1000, 50) == 300
    print('type_guard self-check OK')
