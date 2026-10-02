#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 新设计语言六款 + 彩活四款 + 构图三款 + 撕纸手帐（torn_journal） + 展览海报（exhibition_poster） + 撕纸破洞窥视（torn_peephole） + 撕纸双层（torn_deckle） + 新款两款（modern_spread / cultural_journal） · 设计语言族渲染器（design canonical · 19 款异构模板）
=====================================================================
设计稿：docs/批量设计-新设计语言六款-设计.md（v3，§1 终值 = 实现契约）。
render(photo_path, config, title, sub, date, location, meta_extra='', bg_luma=None,
       photo_focus_y=None, words=None) -> html_str（签名对齐 blueprint_engine.render：传 config）。
meta_extra（可选）：镜头参数等补充注脚信息（如 '35MM F1.4'），经 _meta 拼在 date·location 之后
（本族落点：pop/swiss/tv 的 meta 位；kinfolk/museum/super 款无 meta 位则不渲）。
按 config['template_id'] 分发到 19 个构建函数；mode='DESIGN' 仅为家族标记（非分发键）。
新款两款（2026-09-16，docs/新款入库批-设计.md §2）：模板落新模块 design_templates_b.py
（模板数分档 ≤ 10/文件，§1.4 表 D/D-14）；字体新增注入走 config 声明式
layout['extra_fonts']（§1.3 表 C/D-4：现有 17 款无该键 ⇒ 不匹配款字节零变化）。
文字一律来自参数（不硬编码演示文案）；仅装饰性固定小字/结构标签按款标注：
  · super_index：右上 001、右下 VOL.001（VOL 号固定）；目录行 01–04 编号（v3 单行结构：
    编号+值同行，01→date / 02→location / 03→sub / 04→lens(meta_extra)，缺省 "—"）。
  · retro_tv：SIG.01001101 // CH.09（二进制小字）、BROADCAST（词头，date 参数化）。
  · swiss_red_grid：№ 编号由参数派生（确定性 seed，01–24，blueprint _derive 先例）；右上=日期。
  · museum_frame：顶部信息条 = date · location（参数化）；框色 _frame_palette 确定性。
彩活四款（2026-09-07，docs/批量设计-彩活四款-设计.md §1 终值）固定装饰文案逐款入 config：
  · street_zine：本週注目 ★ 街頭速報 / editors pick ✂ / VOL.12 · STREET EDITION / 看這裡!
  · duo_pop：DUOTONE POP SERIES（词头，date 参数化）
  · doodle_summer：綠野 · 晚風 · 逃跑計畫 / SKETCH DIARY（date 参数化）
  · collage_man：NEW ✦ / APPROVED / 限定 → / CHECK ✓ / GO!! / WALK THIS WAY ↑↓ / 看這裡!! /
    型不设防城市展；词墙三层词池（§0.5）：款格词 A+B 24 词（config 写死）+ 真实元数据词
    （date/location/lens，每图天然不同）+ words 参数（--words 注入）；seed=照片内容哈希
    （非 mtime，防重渲漂移）→ 同图可复现、异图不重样。
构图三款（2026-09-08，docs/批量设计-构图三款-设计.md §1 终值）固定装饰文案逐款入 config，
  fg_texts **dict 形态**（{layout键: font_family}）——按文案**自身 font** 逐字 cmap 预检
  （§0.5 覆盖口径；不限 title_font 白名单）：
  · branch_magazine：一枝探出瓶外 / 余幅皆為留白 / 折枝入畫 · 餘幅皆白（宋体系文案）
  · pop_lichtenstein：太可愛了！（LXGWWenKai 对话框文案）
  · pop_press：網點城市（宋）/ 每一個網點，都是一扇亮著的窗。（LXGWWenKai）
  pop_lichtenstein 黑条星群 12 颗坐标+转角（seed=7 预计算）写死 config，引擎内不跑 random。

画幅：WP-A 分桶 _canvas_for（3:4=900×1200 / 4:3=1200×900 / 16:9=1200×675 / 9:16=675×1200 /
1:1=1080×1080；阈值同 engine_v2/matting_engine，异常回退 3:4）。几何一律 int(round(v*fs))。
  §1 全部数值为 3:4 基准；横版按 fs 等比，气质不偏移由验收 4 人工核兜底。
字体：@font-face 基础 7 常量（同 blueprint FONTS_CSS 路径）+ 11 个按需注入常量
（6 现役 + 新款入库批 5 个，D-5；路径盘上 os.path.exists 实测 ✓）：
  _SS_HEAVY_CSS      → SourceHanSansHeavy（思源黑 Heavy：super 刊名 / tv 主标 / pop 底部大字 /
                       street_zine 刊名红块 name_font / duo_pop·collage_man 主标共用）
  _SS_SERIF_MED_CSS  → SourceHanSerifMedium（思源宋 Medium：super 目录行 / kinfolk 底部中文）
  _CAVEAT_CSS        → CaveatBold（tv 左上手写英文；探针的 Segoe Script 为系统字体不入引擎）
  _QSSS1_CSS         → ZhuoKaiKai（清松手写体1：street_zine/doodle_summer 主标+繁体装饰文案；
                       彩活四款楷体选型，选型依据见 font_guard.py 注释）
  _PRATA_CSS         → Prata（modern_spread 西文主标，R8）
  _SS_BOLD_CSS       → SourceHanSansBold（modern_spread 元数据条 + ISSUED）
  _SS_REG_CSS        → SourceHanSansRegular（modern_spread 页脚细字；路径 v2 实读盘上文件
                       钉死 = SiYuanHeiTi-Regular/SourceHanSansSC-Regular-2.otf，设计档 §2.6）
  _SS_SERIF_REG_CSS  → SourceHanSerifRegular（cultural_journal 手记中文小字）
  _LXGW_REG_CSS      → LXGWWenKaiReg（cultural_journal 手写注记；独立 family——既有
                       LXGWWenKai 常量指向 Bold 文件，改其路径 = 改既有款产物，D-5）
照 _BODONI_CSS 按需注入先例：仅匹配款拼入，不匹配款字节零变化。
兜底字体 @font-face（font_guard.FALLBACK_FONT_FAMILY）仅实际兜底时拼入。
缺字预检（§4-5）：title_font ∈ font_guard.FONT_GUARD_WHITELIST（SourceHanSansHeavy /
ZhuoKaiKai）→ 主标先 fit 后包（matting_engine 接入点 A 先例：fit 按纯文本估宽，
兜底 span 只在最终 HTML 上包裹），缺字→思源宋兜底 span + <!-- font-fallback: --> 注释；
兜底字体也缺→<!-- font-uncoverable: -->。彩活四款固定装饰文案的繁体字随所在款
title_font 一起被预检（config.layout['fg_texts'] 逐款声明，缺字同样兜底 span+注释）。
照片：file:/// 绝对路径；object-fit:cover；WP-B photo_focus_y（0=保顶裁脚；50/缺省不输出属性）。
"""
import hashlib
import math
import os
import random
import html as _html
from pathlib import Path

# ---- 共享排版守卫（收敛宽度自适应 / 落点亮度对比）----
from type_guard import fit_title_fs, luma, readability, _is_cjk
# ---- 缺字预检共享模块（接入点 A，《字体驱动与缺字预检-设计.md》§3 先例）----
import font_guard

FONTS_DIR = 'D:/dsh/fonts'

# 画幅分桶（WP-A，同 engine_v2 / matting_engine._canvas_for 口径）：宽x高。
_SIZES = {'3:4': (900, 1200), '4:3': (1200, 900), '16:9': (1200, 675),
          '9:16': (675, 1200), '1:1': (1080, 1080)}

_serif_cn = "'Songti SC','Source Han Serif SC','SimSun','Noto Serif CJK SC',serif"
_sans_cn = "'PingFang SC','Source Han Sans SC','Noto Sans CJK SC','Microsoft YaHei',sans-serif"

# 7 款基础字体（@font-face，路径同 matting_engine/blueprint_engine）
FONTS_CSS = f'''
@font-face {{ font-family:"SourceSerifHeavy"; src:url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Heavy-4.otf"); }}
@font-face {{ font-family:"LXGWWenKai"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf"); }}
@font-face {{ font-family:"SpaceMono"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/SpaceMono-Bold.ttf"); }}
@font-face {{ font-family:"CormorantItalic"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/CormorantGaramond-Italic.ttf"); }}
@font-face {{ font-family:"PlayfairItalic"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/PlayfairDisplay-Italic.ttf"); }}
@font-face {{ font-family:"CinzelBold"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Cinzel-Bold.ttf"); }}
@font-face {{ font-family:"BebasNeue"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BebasNeue-Regular.ttf"); }}
'''

# ---- 本批新增 3 个 @font-face 按需注入常量（§2 逐一枚举，别无其它；盘上实名 ls 实证）----
# 思源黑 Heavy（super_index 刊名 / retro_tv 主标 / pop_halftone 底部大字共用）
_SS_HEAVY_CSS = f'@font-face {{ font-family:"SourceHanSansHeavy"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源黑体/思源黑体-简体中文/SourceHanSansCN-Heavy.otf"); }}'
# 思源宋 Medium（super_index 目录行 / kinfolk_air 底部中文）
_SS_SERIF_MED_CSS = f'@font-face {{ font-family:"SourceHanSerifMedium"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源宋体/思源宋体-简体中文/SourceHanSerifCN-Medium.otf"); }}'
# Caveat-Bold（retro_tv 左上手写英文）
_CAVEAT_CSS = f'@font-face {{ font-family:"CaveatBold"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Caveat-Bold.ttf"); }}'
# 清松手写体1（彩活四款楷体选型，2026-09-07：street_zine/doodle_summer 主标+固定繁体文案；
# 选型探针实测（font_covers 同口径，记录见 docs/交接摘要.md 2026-09-07 批交付段）——
# 对繁体装饰字覆盖最全的真字重文件）
_QSSS1_CSS = f'@font-face {{ font-family:"ZhuoKaiKai"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/清松手写体1.ttf"); }}'
# 霞鹜文楷（构图三款 2026-09-08：pop_lichtenstein 对话框/pop_press 底部楷体句；探针
# _gen_popart_c.py 的 LXGWWenKai-Bold 同款盘上文件——基础 7 常量已有同款，此处独立
# 常量保持"按需注入"先例：不匹配款字节零变化）
_LXGW_CSS = f'@font-face {{ font-family:"LXGWWenKai"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf"); }}'
# BebasNeue（构图三款 2026-09-08：pop_lichtenstein 爆炸星内嵌 WOW!/POP!；基础 7 常量
# 已有同款文件——独立常量照 _LXGW_CSS 同口径按需注入）
_BEBAS_CSS = f'@font-face {{ font-family:"BebasNeue"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BebasNeue-Regular.ttf"); }}'

# ---- 新款入库批 2026-09-16：+5 个 @font-face 按需注入常量（设计档 §2.6 表；盘上
# os.path.exists 实测 ✓；经 config.layout['extra_fonts'] 声明式注入，D-4/D-5）----
# Prata（modern_spread 西文主标，R8）
_PRATA_CSS = f'@font-face {{ font-family:"Prata"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Prata-Regular.ttf"); }}'
# 思源黑 Bold（modern_spread 元数据条 + ISSUED）
_SS_BOLD_CSS = f'@font-face {{ font-family:"SourceHanSansBold"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源黑体/思源黑体-简体中文/SourceHanSansCN-Bold.otf"); }}'
# 思源黑 Regular（modern_spread 页脚细字；路径 = 设计档 §2.6 v2 实读盘上文件钉死，
# 与批次 §1.6/探针 SANS-R 同一文件——十套同目录的 SourceHanSansCN-Regular.otf 盘上也在但非本款所指）
_SS_REG_CSS = f'@font-face {{ font-family:"SourceHanSansRegular"; src:url("file:///{FONTS_DIR}/SiYuanHeiTi-Regular/SourceHanSansSC-Regular-2.otf"); }}'
# 思源宋 Regular（cultural_journal 手记中文小字）
_SS_SERIF_REG_CSS = f'@font-face {{ font-family:"SourceHanSerifRegular"; src:url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Regular-1.otf"); }}'
# 霞鹜文楷 Regular（cultural_journal 手写注记；独立 family LXGWWenKaiReg——既有 LXGWWenKai
# 常量指向 Bold 文件被 pop 二款/torn_deckle 使用，改其路径 = 改既有款产物，D-5）
_LXGW_REG_CSS = f'@font-face {{ font-family:"LXGWWenKaiReg"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Regular.ttf"); }}'
# 兜底字体 @font-face（font_guard.FALLBACK_FONT_FAMILY）：仅实际发生缺字兜底时拼入
_FALLBACK_SONG_CSS = f'@font-face {{ font-family:"思源宋体"; src:url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Regular-1.otf"); }}'


# ---------------------------------------------------------------
# 比例检测（WP-A 分桶；复用 engine_v2 / matting_engine 的阈值 + fs）
# ---------------------------------------------------------------
def _canvas_for(photo_path):
    """PIL 读照片宽高比 → 5 档分桶（阈值同 engine_v2），异常回退 3:4。
    返回 (W, H, fs)：fs=min(W/900, H/1200)（横档 min(W/1200, H/900)），几何全乘 fs 等比缩放。"""
    ratio = None
    try:
        from PIL import Image as _PILImage
        with _PILImage.open(photo_path) as im:
            w, h = im.size
        ratio = w / h
    except Exception:
        ratio = None
    if ratio is None:
        key = '3:4'
    elif ratio >= 1.6:
        key = '16:9'
    elif ratio >= 1.25:
        key = '4:3'
    elif ratio > 0.9:
        key = '1:1'
    elif ratio > 0.6:
        key = '3:4'
    else:
        key = '9:16'
    W, H = _SIZES[key]
    if W > H:
        fs = min(W / 1200, H / 900)
    else:
        fs = min(W / 900, H / 1200)
    return W, H, fs


# ---------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------
def _photo_uri(photo_path):
    return Path(os.path.abspath(photo_path)).as_uri()


def _meta(date, location, meta_extra=''):
    # date/location 已在 render 内 esc()；meta_extra 未转义，须在此补齐（与 blueprint 一致）
    return ' · '.join(x for x in [date, location, _html.escape(meta_extra)] if x)


def _shadow(color, bg=None):
    """落点亮度感知对比守卫：返回 text-shadow 值。"""
    return readability(color, bg)['shadow']


def _seed(*parts):
    _s = '|'.join(str(p) for p in parts if p)
    return int(hashlib.md5(_s.encode('utf-8')).hexdigest(), 16)


# ---------------------------------------------------------------
# museum_frame · 框色判定（§1.3：确定性函数，同图同色，可单测）
# PIL 下采样均值 → 暖度 = R−B；≥ 阈值（默认 12）→ 暖调描金，否则银灰。
# 不引第三方色彩库。
# ---------------------------------------------------------------
def _frame_palette(photo_or_uri, cfg):
    """museum 框色判定（确定性）。入参可为盘路径或 file:/// URI（模板侧只有 uri——
    先还原盘路径再开图，否则 PIL 打不开 URI → 恒走兜底，冷暖判定失效）。"""
    lay = cfg['layout']
    p = photo_or_uri
    if p.startswith('file:///'):
        from urllib.parse import unquote
        p = unquote(p[len('file:///'):])
    r_mean = b_mean = None
    try:
        from PIL import Image as _PI
        with _PI.open(p) as im:
            im = im.convert('RGB')
            # 下采样 64×64 均值（确定性：resize 默认核 BICUBIC 固定，同图同结果）
            px = list(im.resize((64, 64)).getdata())
            r_mean = sum(q[0] for q in px) / (64 * 64)
            b_mean = sum(q[2] for q in px) / (64 * 64)
    except Exception:
        r_mean = b_mean = None
    if r_mean is None:                      # PIL 不可用 → 冷调兜底（确定性，不掷随机）
        return lay['cool_color']
    warm = (r_mean - b_mean) >= lay.get('warm_threshold', 12)
    return lay['warm_color'] if warm else lay['cool_color']


# ---------------------------------------------------------------
# 基础 CSS（W/H 按源图比例动态给出）
# ---------------------------------------------------------------
def _BASE_CSS(bg, W, H, focus_css=';object-position:center'):
    return f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}
.stage{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}
.ph{{display:block;width:100%;height:100%;object-fit:cover{focus_css}}}
'''


def _img(uri, tf=''):
    return f'<img class="ph" src="{uri}" style="{tf}">'


# ===============================================================
# 各模板构建函数（返回 body 片段 = 一个 .stage 容器）
# 签名统一：fn(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None)
#   §1 数值为 3:4 基准像素；横量 → int(round(v*fx))，纵量 → int(round(v*fy))，
#   字号/线宽/圆角/正圆 → int(round(v*fs))；flex/% 保持相对。
#   所有文字（T/S/D/L）为已转义字符串，**不硬编码演示文案**（装饰性固定小字除外，逐款标注）。
# ===============================================================
def _tpl_pop_halftone(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """孟菲斯波点（§1.1 v3，按探针终图 A_pop_halftone__suz.png 重写）：黑底 #111 +
    黄波点纹 + 四角青/粉/黄点缀块 + 粉#e8447a/青#23c4a7 双色边框照片（外粉内青双线框间
    留白，方正规整不斜置）+ 顶部斜贴纸 EN 标题块（粉底 rotate -2° + 硬偏移青影，--sub
    Impact 系粗体黄字字距拉开）+ 底部中文大字（--title 黄字思源黑 Heavy 居中 + 粉/青
    双色硬偏移阴影）。标题全落黑底区（text_on_photo=False 护脸）；超长 fit 一行不折行。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 波点纹（radial-gradient 圆点阵列；装饰无文案）
    dots = (f'background-image:radial-gradient(circle,{lay["dot_color"]} {_s(lay["dot_px"])}px,'
            f'transparent {_s(lay["dot_px"]) + 0.5:.1f}px);background-size:'
            f'{_x(lay["dot_gap"])}px {_y(lay["dot_gap"])}px;background-position:'
            f'{_x(8)}px {_y(8)}px;opacity:{lay["dot_opacity"]}')
    # 四角点缀块（装饰，无文案；位置为 §1 v3 定稿装饰位，随画幅缩放）
    blocks = ''
    for b in lay['blocks']:
        blocks += (f'<div style="position:absolute;left:{_x(b["x"])}px;top:{_y(b["y"])}px;'
                   f'width:{_x(b["w"])}px;height:{_y(b["h"])}px;background:{b["color"]};'
                   f'transform:rotate({b["rot"]}deg);z-index:3"></div>')
    # 双色边框照片框（外粉内青双线、框间黑底留白，方正规整不斜置——探针 A 定稿；
    # 双框色/黑底透出色均入 config，模板不藏魔数）
    ph_left = (W - _x(lay['photo_w'])) // 2
    photo = (f'<div style="position:absolute;top:{_y(lay["photo_top"])}px;left:{ph_left}px;'
             f'width:{_x(lay["photo_w"])}px;height:{_y(lay["photo_h"])}px;overflow:hidden;'
             f'border:{_s(lay["frame_outer_px"])}px solid {lay["frame_outer_color"]};'
             f'box-shadow:inset 0 0 0 {_s(lay["frame_gap_px"])}px {cfg["palette"]["primary"]},'
             f'inset 0 0 0 {_s(lay["frame_gap_px"] + lay["frame_inner_px"])}px {lay["frame_inner_color"]},'
             f'{lay["frame_shadow"]};z-index:4">{_img(uri, cfg["tone_filter"])}</div>')
    # 斜贴纸标题块（本款灵魂，v3 复活）：粉底 rotate -2° + 硬偏移青影（贴纸伪厚边），
    # 内放 --sub EN Impact 系粗体黄字字距拉开；居中偏左，黑底区上部
    _pink = lay['frame_outer_color']
    _teal = lay['frame_inner_color']
    _yellow = lay['accent_yellow']
    sticker = ''
    if S:
        _fs_st = _s(lay['sticker_px'])
        _st_w = fit_title_fs(S, _s(lay['sticker_max_w']) - 2 * _s(lay['sticker_pad_x']), _fs_st,
                             lay['sticker_letter'])
        # min-width 兜底：短 sub 时贴纸不退化成细条（探针 A 观感：块明显宽于文字）
        sticker = (f'<div style="position:absolute;top:{_y(lay["sticker_top"])}px;left:50%;'
                   f'transform:translateX(-52%) rotate({lay["sticker_rot"]}deg);z-index:10;'
                   f'background:{_pink};padding:{_y(lay["sticker_pad_y"])}px '
                   f'{_x(lay["sticker_pad_x"])}px;min-width:{_s(lay["sticker_min_w"])}px;'
                   f'box-sizing:border-box;box-shadow:{_x(lay["sticker_dx"])}px '
                   f'{_y(lay["sticker_dy"])}px 0 {_teal};text-align:center">'
                   f'<span style="font-family:Impact,&quot;{cfg["fonts"]["emotion"]}&quot;,'
                   f'monospace;font-weight:700;font-size:{_st_w}px;'
                   f'letter-spacing:{lay["sticker_letter"]};color:{_yellow};'
                   f'white-space:nowrap;text-transform:uppercase">{S}</span></div>')
    # 底部中文大字（--title 黄字思源黑 Heavy 居中 + 粉/青双色硬偏移阴影，孟菲斯式）；
    # 超长 fit 缩字号一行（黑底区横排，不折行不叠照片）
    hero_px = _s(cfg['scale']['hero_px'])
    hero_fs = fit_title_fs(T, W - 2 * _x(lay['hero_left']), hero_px, cfg['scale']['hero_letter'])
    hero_html = ''
    if T:
        hero_html = (f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
                     f'font-weight:900;font-size:{hero_fs}px;'
                     f'line-height:{cfg["scale"]["hero_lh"]};letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'color:{_yellow};text-align:center;text-shadow:{cfg["scale"]["hero_shadow"]};'
                     f'white-space:nowrap">{T}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{lay["frame_outer_color"]};'
                     f'letter-spacing:.3em;margin-top:{_y(8)}px">{_m}</div>')
    # 底部文字块 = 单一容器 + 单一纵锚 hero_bottom（主标行 + meta 行同属一块 → 改锚即两行整体位移）
    # 微调批3 A#3（2026-09-15）：hero_bottom 96→86（×0.90）= 整体下移，行间 margin-top:8px 不变
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{cfg["palette"]["primary"]}"></div>
  <div style="position:absolute;inset:0;{dots}"></div>
  {blocks}
  {photo}
  {sticker}
  <div style="position:absolute;left:{_x(lay["hero_left"])}px;right:{_x(lay["hero_left"])}px;bottom:{_y(lay["hero_bottom"])}px;z-index:20">
    {hero_html}
    {meta_html}
  </div>
</div>'''


def _tpl_kinfolk_air(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """素白金线（§1.2 v3，按探针终图 B_kinfolk_air__suz.png 补刊头）：米白极简大留白 +
    顶部刊头带（EN 刊名 --sub 衬线 34px 字距 .35em 全大写；2026-09-14 微调批2 #48 删
    小字行 NO.{n}·月份中文）+ 居中照片窗（+10% 满）+ 金色渐隐分界线 + 底部文字带
    （中文 29px 思源宋 Medium / EN 13px mono / meta 行细字距大写 mono）。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 顶部刊头带（v3 补）：**2026-09-14 微调批2 #48 已删小字行**（原 NO.{n} · 月份中文派生行，
    # 即用户所指"上面英文标题的日期元素"；相应死键 head_no_* / month_names / head_en_gap 一并联删）。
    # EN 刊名行取绝对锚 head_en_top（= 56+14），渲染位置零位移。
    head_en = ''
    if S:
        head_en = (f'<div style="position:absolute;top:{_y(lay["head_en_top"])}px;'
                   f'left:0;right:0;text-align:center;font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                   f'font-size:{_s(lay["head_en_px"])}px;letter-spacing:.35em;text-indent:.35em;'
                   f'color:{cfg["palette"]["accent"]};text-transform:uppercase;white-space:nowrap;'
                   f'overflow:hidden">{S}</div>')
    photo_bottom = _y(lay['photo_top'] + lay['photo_h'])
    photo = (f'<div style="position:absolute;top:{_y(lay["photo_top"])}px;left:{_x(lay["photo_inset_x"])}px;'
             f'right:{_x(lay["photo_inset_x"])}px;height:{_y(lay["photo_h"])}px;overflow:hidden;'
             f'z-index:4;box-shadow:{lay["photo_shadow"]}">{_img(uri, cfg["tone_filter"])}</div>')
    # 金色渐隐线（照片与文字区交界；90deg 透明→金→透明，1px；内缩/站点入 config）
    _lf = lay['line_fade']
    line = (f'<div style="position:absolute;top:{photo_bottom + _y(lay["line_gap"])}px;'
            f'left:{_x(lay["line_inset_x"])}px;right:{_x(lay["line_inset_x"])}px;'
            f'height:{_s(lay["line_px"])}px;'
            f'background:linear-gradient(90deg,transparent,{cfg["palette"]["point"]} {_lf}%,'
            f'{cfg["palette"]["point"]} {100 - _lf}%,transparent);z-index:5"></div>')
    text = ''
    if T:
        text = (f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                f'font-size:{_s(cfg["scale"]["hero_px"])}px;letter-spacing:{cfg["scale"]["hero_letter"]};'
                f'color:{cfg["palette"]["accent"]}">{T}</div>')
    sub_html = ''
    if S:
        sub_html = (f'<div style="margin-top:{_y(12)}px;font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,monospace;'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;letter-spacing:.34em;'
                    f'color:{cfg["palette"]["point"]};text-transform:uppercase">{S}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="margin-top:{_y(10)}px;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;letter-spacing:.34em;'
                     f'color:{cfg["palette"]["point"]};text-transform:uppercase">{_m}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{cfg["palette"]["primary"]}"></div>
  {head_en}
  {photo}
  {line}
  <div style="position:absolute;bottom:{_y(lay["text_bottom"])}px;left:0;right:0;text-align:center;z-index:5">
    {text}
    {sub_html}
    {meta_html}
  </div>
</div>'''


def _tpl_museum_frame(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """馆签双框（§1.3）：双线展签框（框色 _frame_palette 随图自动·确定性）+ 顶部信息条
    （mono 大写 date·location）+ 底部文字块下移加深。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    frame = _frame_palette(uri, cfg)
    # 双线展签框：外框线 + 框间距留白 + 内框线（inset box-shadow 双环，间距透出底色）
    frame_div = (f'<div style="position:absolute;inset:{_y(lay["frame_inset"])}px;'
                 f'border:{_s(lay["frame_outer_px"])}px solid {frame};'
                 f'box-shadow:inset 0 0 0 {_s(lay["frame_gap_px"])}px {cfg["palette"]["primary"]},'
                 f'inset 0 0 0 {_s(lay["frame_gap_px"] + lay["frame_inner_px"])}px {frame};'
                 f'z-index:3"></div>')
    info = ' · '.join(x for x in [D, L] if x)
    info_html = ''
    if info:
        info_html = (f'<div style="position:absolute;top:{_y(lay["info_top"])}px;left:{_x(lay["info_x"])}px;'
                     f'right:{_x(lay["info_x"])}px;display:flex;justify-content:space-between;'
                     f'z-index:5;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;letter-spacing:.2em;'
                     f'color:{cfg["palette"]["point"]};text-transform:uppercase"><span>{D}</span>'
                     f'<span>{L}</span></div>')
    rule = (f'<div style="position:absolute;top:{_y(lay["rule_top"])}px;left:{_x(lay["info_x"])}px;'
            f'right:{_x(lay["info_x"])}px;height:{_s(1)}px;background:{frame};z-index:5"></div>')
    photo = (f'<div style="position:absolute;top:{_y(lay["photo_top"])}px;left:{_x(lay["photo_x"])}px;'
             f'right:{_x(lay["photo_x"])}px;bottom:{_y(lay["photo_bottom"])}px;overflow:hidden;'
             f'z-index:4;box-shadow:{lay["photo_shadow"]}">{_img(uri, cfg["tone_filter"])}</div>')
    ct = _shadow(cfg['palette']['accent'], luma(cfg['palette']['primary']))
    hero_html = ''
    if T:
        hero_html = (f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};font-weight:900;'
                     f'font-size:{fit_title_fs(T, int(W * 0.8), _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};text-indent:{cfg["scale"]["hero_letter"]};'
                     f'color:{cfg["palette"]["accent"]};text-shadow:{ct}">{T}</div>')
    sub_html = ''
    if S:
        sub_html = (f'<div style="margin-top:{_y(10)}px;font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,monospace;'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;letter-spacing:.4em;'
                    f'color:{cfg["palette"]["point"]}">{S}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{cfg["palette"]["primary"]}"></div>
  {frame_div}
  {info_html}
  {rule}
  {photo}
  <div style="position:absolute;bottom:{_y(lay["hero_bottom"])}px;left:0;right:0;text-align:center;z-index:5">
    {hero_html}
    {sub_html}
  </div>
</div>'''


def _tpl_swiss_red_grid(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """红格瑞士（§1.4）：去色满幅照片 + 红细网格（径向蒙版：中心 40% 无网格、向四角渐显，
    方向勿反）+ 左下白衬线主标 + EN 副标（浅红）+ 角标 № 编号行/白日期。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    photo = f'<div style="position:absolute;inset:0">{_img(uri, cfg["tone_filter"])}</div>'
    # 红色细网格 + 径向蒙版（transparent 在中心 40%——探针返工两次的教训，勿反）
    grid = (f'<div style="position:absolute;inset:0;background:'
            f'repeating-linear-gradient(0deg,rgba(196,28,28,{lay["grid_alpha"]}) 0 {_s(lay["grid_line_px"])}px,'
            f'transparent {_s(lay["grid_line_px"])}px {_s(lay["grid_px"])}px),'
            f'repeating-linear-gradient(90deg,rgba(196,28,28,{lay["grid_alpha"]}) 0 {_s(lay["grid_line_px"])}px,'
            f'transparent {_s(lay["grid_line_px"])}px {_s(lay["grid_px"])}px);'
            f'-webkit-mask-image:radial-gradient(ellipse {lay["mask_ex"]}% {lay["mask_ey"]}% at '
            f'{lay["mask_cx"]}% {lay["mask_cy"]}%,transparent {lay["mask_transparent"]}%,#000 {lay["mask_full"]}%);'
            f'mask-image:radial-gradient(ellipse {lay["mask_ex"]}% {lay["mask_ey"]}% at '
            f'{lay["mask_cx"]}% {lay["mask_cy"]}%,transparent {lay["mask_transparent"]}%,#000 {lay["mask_full"]}%)"></div>')
    # 主标：白衬线 + EN 副标浅红 + text-shadow 保读（readability 落点感知，bg=照片底部亮度）
    ct = _shadow('#ffffff', bg)
    hero_html = ''
    if T:
        hero_html = (f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};font-weight:700;'
                     f'font-size:{fit_title_fs(T, int(W * 0.86), _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                     f'line-height:{cfg["scale"]["hero_lh"]};letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'color:#fff;text-shadow:{ct}">{T}</div>')
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-size:{_s(cfg["scale"]["lead_px"])}px;line-height:1.15;'
                    f'color:{cfg["palette"]["point"]};letter-spacing:.02em;margin-top:{_y(lay["en_gap"])}px;'
                    f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};text-shadow:{ct}">{S}</div>')
    # 角标：左上红 № 编号行（seed 派生 01–24，确定性结构标签）＋右上白日期
    _no = 1 + (_seed('no', T, D, L) % lay['no_max'])
    corner = (f'<div style="position:absolute;left:{_x(lay["corner_x"])}px;top:{_y(lay["corner_top"])}px;'
              f'color:{cfg["palette"]["accent"]};font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
              f'font-size:{_s(cfg["scale"]["micro_px"])}px;letter-spacing:.3em">№ {_no:02d} / 图版记录</div>'
              f'<div style="position:absolute;right:{_x(lay["corner_x"])}px;top:{_y(lay["corner_top"])}px;'
              f'color:#fff;opacity:.85;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
              f'font-size:{_s(lay["date_px"])}px">{D}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {photo}
  {grid}
  {corner}
  <div style="position:absolute;left:{_x(lay["hero_left"])}px;bottom:{_y(lay["hero_bottom"])}px;right:{_x(lay["hero_left"])}px;z-index:20">
    {hero_html}
    {sub_html}
  </div>
</div>'''


def _tpl_super_index(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """刊头索引（§1.5）：奶白刊头带 + 满幅照片；刊名思源黑 Heavy + " :" 冒号贴上沿；
    右上 001；副标行；四栏目录行 20px 思源宋 Medium（栏内容参数化映射，缺省 "—"）；
    照片右下白 mono 日期 · VOL.001。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 刊名（--title）思源黑 Heavy + " :" 冒号贴字面上沿
    head = ''
    if T:
        head = (f'<div style="position:absolute;top:{_y(lay["head_top"])}px;left:{_x(lay["head_x"])}px;'
                f'color:{cfg["palette"]["accent"]};font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
                f'font-weight:900;font-size:{fit_title_fs(T, int(W * 0.72), _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                f'letter-spacing:{cfg["scale"]["hero_letter"]};white-space:nowrap">{T}'
                f'<span style="font-size:{_s(lay["colon_px"])}px;vertical-align:{lay["colon_va"]}"> :</span></div>')
    num = (f'<div style="position:absolute;top:{_y(lay["num_top"])}px;right:{_x(lay["head_x"])}px;'
           f'color:{cfg["palette"]["accent"]};font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
           f'font-size:{_s(lay["num_px"])}px;font-weight:700">001</div>')
    sub_html = ''
    if S:
        sub_html = (f'<div style="position:absolute;top:{_y(lay["sub_top"])}px;left:{_x(lay["head_x"])}px;'
                    f'right:{_x(lay["head_x"])}px;color:{cfg["palette"]["point"]};'
                    f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_sans_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;letter-spacing:.14em;white-space:nowrap;'
                    f'overflow:hidden">{S}</div>')
    # 四栏目录行（v3 单行结构，§1.5：每栏"编号+值"同行——`01 {date} / 02 {location} /
    # 03 {sub} / 04 {lens}`；缺省栏 "—"；值过长 fit 缩字号〔fit_title_fs〕；
    # v2"栏头=值、副行=值"双层结构作废）。D/L/S 已在 render 内 esc()（防双转义，
    # font_guard 接入点 A 同口径），此处不再 escape；仅 meta_extra（未转义）在拼接前 esc。
    _cols = [D or lay['dir_default'], L or lay['dir_default'],
             S or lay['dir_default'], _html.escape(meta_extra) or lay['dir_default']]
    _dir_fs = _s(lay['dir_px'])
    _col_w = (int(W) - 2 * _x(lay['dir_x']) - 3 * _x(lay['dir_gap'])) // 4
    # 2026-09-25 用户修单：①编号后加"："（01：{date} …）②四栏**统一字号**（原逐栏独立 fit
    # 缩字号 → 四栏大小不一 = 用户所指"字体不统一"）→ 取四栏 fit 的 min 整行统一。
    # 审查修复 F6：fit 按**显示文本**估（html.unescape 还原实体——按转义串计宽会过缩）；
    # 编号段渲染 700 粗体比 fit 估宽略肥 → 列宽预留 **0.15×字号**（≈3px@20px）作余量
    # （nowrap 溢出防护，溢出最多数像素入 gap 不撞栏；复审 #3 口径核定：按字号计，非按编号宽）。
    _fs_cands = [fit_title_fs(f'{i + 1:02d}：{_html.unescape(v)}',
                              _col_w - int(_dir_fs * 0.15), _dir_fs) for i, v in enumerate(_cols)]
    _dir_fs_uni = min(_fs_cands)
    col_html = ''
    for i, v in enumerate(_cols):
        # 每栏独立 white-space:nowrap 兜底不折行；字号 = 整行统一值。
        col_html += (f'<div style="flex:1;min-width:0;font-size:{_dir_fs_uni}px;white-space:nowrap">'
                     f'<span style="font-weight:700">{i + 1:02d}：</span>{v}</div>')
    dire = (f'<div style="position:absolute;top:{_y(lay["dir_top"])}px;left:{_x(lay["dir_x"])}px;'
            f'right:{_x(lay["dir_x"])}px;display:flex;gap:{_x(lay["dir_gap"])}px;'
            f'color:{cfg["palette"]["point"]};font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
            f'font-size:{_dir_fs_uni}px;line-height:1.6">{col_html}</div>')
    rule = (f'<div style="position:absolute;top:{_y(lay["band_h"] - lay["rule_lift"])}px;left:{_x(lay["dir_x"])}px;'
            f'right:{_x(lay["dir_x"])}px;height:{_s(lay["rule_px"])}px;'
            f'background:{lay["rule_color"]}"></div>')
    band = _y(lay['band_h'])
    photo = (f'<div style="position:absolute;top:{band}px;left:0;right:0;bottom:0;overflow:hidden">'
             f'{_img(uri, cfg["tone_filter"])}</div>')
    foot = (f'<div style="position:absolute;bottom:{_y(lay["foot_bottom"])}px;right:{_x(lay["foot_right"])}px;'
            f'color:#fff;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
            f'font-size:{_s(lay["foot_px"])}px;letter-spacing:.24em;'
            f'text-shadow:0 1px 8px rgba(0,0,0,.6)">{D} · VOL.001</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;top:0;left:0;right:0;height:{band}px;background:{cfg["palette"]["primary"]}"></div>
  {head}
  {num}
  {sub_html}
  {dire}
  {rule}
  {photo}
  {foot}
</div>'''


def _tpl_retro_tv(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """复古电视（§1.6）：深炭底 + 大圆角照片窗（居中偏上）+ 左上手写英文（Caveat-Bold）+
    右上红/黄圆点 + 右下主标思源黑 Heavy + RGB 故障错位 text-shadow（**单元素多层
    shadow，禁三层 span 叠法**）+ 故障带 + SIG 二进制小字 + 左下 BROADCAST · date。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    sub_html = ''
    if S:
        sub_html = (f'<div style="position:absolute;top:{_y(lay["sub_top"])}px;left:{_x(lay["sub_left"])}px;'
                    f'color:{cfg["palette"]["point"]};font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,cursive;'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px">{S}</div>')
    dots = ''.join(
        f'<div style="position:absolute;top:{_y(d["top"])}px;right:{_x(d["right"])}px;width:{_s(d["d"])}px;'
        f'height:{_s(d["d"])}px;border-radius:50%;background:{d["color"]}"></div>'
        for d in (lay['dot1'], lay['dot2']))
    photo = (f'<div style="position:absolute;top:{_y(lay["photo_top"])}px;left:{_x(lay["photo_x"])}px;'
             f'right:{_x(lay["photo_x"])}px;height:{_y(lay["photo_h"])}px;border-radius:{_s(lay["radius"])}px;'
             f'overflow:hidden;border:{_s(lay["border_px"])}px solid {lay["border_color"]};'
             f'box-shadow:{lay["photo_shadow"]}">{_img(uri, cfg["tone_filter"])}</div>')
    # 主标：单元素多层 text-shadow（RGB 故障错位 + 底部硬影）；右下角落在深底上（不压照片）
    dx, dy = lay['glitch_dx'], lay['glitch_dy']
    ct = _shadow(cfg['palette']['accent'], luma(cfg['palette']['primary']))
    glitch = (f'-{_s(dx)}px -{_s(dy)}px 0 {lay["glitch_red"]},{_s(dx)}px {_s(dy)}px 0 {lay["glitch_cyan"]},'
              f'0 {_s(4)}px 0 rgba(232,68,63,.35),{ct}')
    hero_html = ''
    if T:
        hero_html = (f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"])}px;right:{_x(lay["hero_right"])}px;'
                     f'color:{cfg["palette"]["accent"]};font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
                     f'font-weight:900;font-size:{fit_title_fs(T, int(W * 0.62), _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                     f'line-height:{cfg["scale"]["hero_lh"]};letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'text-shadow:{glitch};white-space:nowrap;z-index:6">{T}</div>')
    # 故障带：标题上方红青渐变细线 + SIG.01001101 // CH.09（固定装饰文案；细线贴标题上缘，
    # SIG 小字在细线上方——探针终稿排布）
    sig = (f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"] + 116)}px;right:{_x(lay["hero_right"])}px;'
           f'color:#9a9aa6;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
           f'font-size:{_s(lay["sig_px"])}px;letter-spacing:.3em;z-index:6;text-align:right">'
           f'SIG.01001101 // CH.09</div>'
           f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"] + 94)}px;right:{_x(lay["hero_right"])}px;'
           f'height:{_s(lay["glitch_line_h"])}px;width:{_x(lay["glitch_line_w"])}px;z-index:5;'
           f'background:linear-gradient(90deg,transparent,{lay["glitch_red"]} 30%,'
           f'{lay["glitch_cyan"]} 55%,transparent);opacity:.8"></div>')
    _m = _meta(D, '', meta_extra)   # 左下 BROADCAST · date（location 不进此位；date 参数化）
    bcast = (f'<div style="position:absolute;bottom:{_y(lay["broadcast_bottom"])}px;left:{_x(lay["sub_left"])}px;'
             f'color:#9a9aa6;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
             f'font-size:{_s(cfg["scale"]["micro_px"])}px;letter-spacing:.2em">BROADCAST · {_m or ""}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{cfg["palette"]["primary"]}"></div>
  {sub_html}
  {dots}
  {photo}
  {sig}
  {hero_html}
  {bcast}
</div>'''


def _tpl_street_zine(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """街头小志（§1.1，探针 P1_street_zine__*.png）：照片满幅原色 + 顶部渐变黑带内
    EN 刊名红块白字（--sub；#e8443f 底黑体 Heavy 74px）+ 黄字副行（固定文案）+
    黄贴纸 editors pick ✂ + 底部右对齐中文大字楷体白字 96px rotate(2°)（--title，
    阴影镜像红/黑）+ VOL 行 + 日期青块 + 黄箭头 ➜ rotate(-45°) 指右上 + 红标"看這裡!"。
    hero=bottom_right 槽；text_on_photo=True（标题压照片下部，需人工核，不护脸）。
    楷体=ZhuoKaiKai（真字重文件，font_guard 白名单——缺字走思源宋兜底）。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 照片满幅原色（无滤镜）
    photo = f'<div style="position:absolute;inset:0">{_img(uri, cfg["tone_filter"])}</div>'
    # 顶部渐变黑带：180deg rgba(0,0,0,.55)→transparent，padding 26/30
    # （EN 刊名红块 = **黑体 Heavy**〔design §1.1 契约：name_font 入 config，
    # 复用 _SS_HEAVY_CSS 按需注入链〕；黄副行 = title_font〔设计稿 §2：繁体装饰文案
    # 随 title_font 渲染+预检〕）
    band_pad = (f'padding:{_y(lay["band_pad_y"])}px {_x(lay["band_pad_x"])}px;')
    name = ''
    if S:
        name = (f'<div style="display:inline-block;background:{cfg["palette"]["accent"]};'
                f'color:#fff;font-family:&quot;{lay["name_font"]}&quot;,{_sans_cn};'
                f'font-weight:900;font-size:{_s(lay["name_px"])}px;line-height:1.12;'
                f'padding:{_y(lay["name_pad_y"])}px {_x(lay["name_pad_x"])}px;'
                f'letter-spacing:{lay["name_letter"]}">{S}</div>')
    subline = (f'<div style="margin-top:{_y(lay["subline_gap"])}px;color:{cfg["palette"]["point"]};'
               f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};font-weight:900;'
               f'font-size:{_s(lay["subline_px"])}px;letter-spacing:{lay["subline_letter"]}">'
               f'{lay["subline_text"]}</div>')
    band = (f'<div style="position:absolute;top:0;left:0;right:0;{band_pad}'
            f'background:linear-gradient(180deg,{lay["band_color"]},transparent);z-index:10">'
            f'{name}{subline}</div>')
    # 黄贴纸 editors pick ✂（rotate -6°，硬阴影；固定装饰文案）
    sticker = (f'<div style="position:absolute;top:{_y(lay["sticker_top"])}px;'
               f'left:{_x(lay["sticker_left"])}px;background:{cfg["palette"]["point"]};'
               f'color:#111;font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_sans_cn};'
               f'font-weight:900;font-size:{_s(lay["sticker_px"])}px;'
               f'padding:{_y(lay["sticker_pad_y"])}px {_x(lay["sticker_pad_x"])}px;'
               f'transform:rotate({lay["sticker_rot"]}deg);z-index:11;'
               f'box-shadow:3px 3px 0 rgba(0,0,0,.4)">{lay["sticker_text"]}</div>')
    # 底部右对齐（v2 调整：右移）：中文大字楷体白字 rotate(2°)，阴影镜像（-4px 4px 0 红，
    # -8px 8px 0 黑 45%）；下排右对齐 VOL 行 + 日期青块 rotate(1.5°)（date_bg 入 config）
    hero_html = ''
    if T:
        hero_px = _s(cfg['scale']['hero_px'])
        # fit 收敛（探针口径 96px；右下角落区宽 ≈ W-左右内缩，超长一行缩档不折行）
        hero_fs = fit_title_fs(T, int(W * 0.86), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="color:#fff;font-family:&quot;{cfg["fonts"]["hero"]}&quot;,'
                     f'{_serif_cn};font-weight:700;font-size:{hero_fs}px;'
                     f'line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'transform:rotate(2deg);text-shadow:{cfg["scale"]["hero_shadow"]};'
                     f'white-space:nowrap">{T}</div>')
    vol_date = ''
    if D:
        vol_date = (f'<span style="color:#fff;font-family:&quot;{cfg["fonts"]["data"]}&quot;,'
                    f'monospace;font-size:{_s(lay["vol_px"])}px;'
                    f'letter-spacing:{lay["vol_letter"]}">{lay["vol_text"]}</span>'
                    f'<span style="color:{lay["date_color"]};'
                    f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                    f'font-weight:700;font-size:{_s(lay["date_px"])}px;'
                    f'padding:{_y(4)}px {_x(12)}px;'
                    f'transform:rotate({lay["date_rot"]}deg);display:inline-block;'
                    f'background:{lay["date_bg"]}">{D}</span>')
    bottom = (f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"])}px;'
              f'right:{_x(lay["hero_right"])}px;text-align:right;z-index:10">'
              f'{hero_html}<div style="margin-top:{_y(lay["vol_gap"])}px;display:flex;'
              f'gap:{_x(14)}px;align-items:center;justify-content:flex-end">{vol_date}</div></div>')
    # 黄箭头 ➜ rotate(-45°) 指右上 + 红标"看這裡!"（指向人物/主体；固定装饰文案）
    arrow = (f'<div style="position:absolute;bottom:{_y(lay["arrow_bottom"])}px;'
             f'left:{_x(lay["arrow_left"])}px;color:{cfg["palette"]["point"]};'
             f'font-size:{_s(lay["arrow_px"])}px;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
             f'font-weight:700;transform:rotate({lay["arrow_rot"]}deg);z-index:11">➜</div>')
    mark = (f'<div style="position:absolute;bottom:{_y(lay["mark_bottom"])}px;'
            f'left:{_x(lay["mark_left"])}px;color:#fff;background:{cfg["palette"]["accent"]};'
            f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};font-weight:700;'
            f'font-size:{_s(lay["mark_px"])}px;padding:{_y(4)}px {_x(10)}px;'
            f'transform:rotate({lay["mark_rot"]}deg);z-index:11">{lay["mark_text"]}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {photo}
  {band}
  {sticker}
  {bottom}
  {arrow}
  {mark}
</div>'''


def _duo_pop_dots_svg(lay, block_px):
    """duo_pop 12 颗无规律波普圆点 SVG（§1.2：坐标写死 config.dots，确定性——同图同点）。
    viewBox 900×300 基准 + preserveAspectRatio slice 随画幅缩放（探针 P2_duo_pop__*_b 口径）。"""
    circles = ''
    for d in lay['dots']:
        stroke = (f' stroke="{d["stroke"]}" stroke-width="{d["stroke_w"]}"'
                  if d.get('stroke') else '')
        circles += (f'<circle cx="{d["cx"]}" cy="{d["cy"]}" r="{d["r"]}" '
                    f'fill="{d["fill"]}" opacity="{d["opacity"]}"{stroke}/>')
    return (f'<svg style="position:absolute;inset:0" width="100%" height="100%" '
            f'viewBox="0 0 900 {block_px}" preserveAspectRatio="xMidYMid slice">{circles}</svg>')


def _tpl_duo_pop(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """双色波普（§1.2 方案 b，探针 P2_duo_pop__*_b.png）：照片**原色满幅**（contrast/saturate
    轻调，**禁 duotone 滤镜链**——a 方案实证人像翻车）+ 顶部三色跑马条 15px + 底部红色文字块
    270px（白字大标 100px 黑影 + EN Impact 黄字 40px + 日期行 mono）+ 12 颗无规律波普圆点
    （SVG circle，坐标写死 config，确定性）+ 右下大圆点青底黄描边环。
    text_on_photo=True（红块 270px+圆点覆盖满幅照片下部，需人工核，不护脸）。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 照片原色满幅（方案 b 核心：无 duotone）
    photo = f'<div style="position:absolute;inset:0">{_img(uri, cfg["tone_filter"])}</div>'
    # 顶部三色跑马条（#54 后 15px；值在 config `bar_px`；repeating-linear-gradient 90deg，各 40px）
    c1, c2, c3 = lay['bar_colors']
    seg = lay['bar_seg']
    bar = (f'<div style="position:absolute;top:0;left:0;right:0;height:{_y(lay["bar_px"])}px;'
           f'background:repeating-linear-gradient(90deg,{c1} 0 {seg}px,{c2} {seg}px '
           f'{2 * seg}px,{c3} {2 * seg}px {3 * seg}px);z-index:5"></div>')
    # 底部红色文字块（#54 后 270px；值在 config `block_px`；overflow:hidden 内嵌圆点 SVG——探针 b 口径：圆点只在红块内）
    block_px = _y(lay['block_px'])
    dots_svg = _duo_pop_dots_svg(lay, lay['block_px'])
    block = (f'<div style="position:absolute;bottom:0;left:0;right:0;height:{block_px}px;'
             f'background:{cfg["palette"]["accent"]};overflow:hidden;z-index:6">{dots_svg}</div>')
    # 大标（--title）白字 100px 黑影 6px + EN（--sub）Impact 黄字 40px
    hero_html = ''
    if T:
        hero_px = _s(cfg['scale']['hero_px'])
        hero_fs = fit_title_fs(T, int(W * 0.82), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"])}px;'
                     f'left:{_x(lay["hero_left"])}px;color:#fff;'
                     f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};font-weight:900;'
                     f'font-size:{hero_fs}px;line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]};white-space:nowrap;z-index:8">{T}</div>')
    en_html = ''
    if S:
        en_html = (f'<div style="position:absolute;bottom:{_y(lay["en_bottom"])}px;'
                   f'left:{_x(lay["en_left"])}px;color:{cfg["palette"]["point"]};'
                   f'font-family:Impact,&quot;{cfg["fonts"]["emotion"]}&quot;,sans-serif;'
                   f'font-size:{_s(lay["en_px"])}px;letter-spacing:{lay["en_letter"]};'
                   f'text-transform:uppercase;white-space:nowrap;z-index:8">{S}</div>')
    # 日期行 mono（date 参数化 + 固定 EN 词头）
    _m = _meta(D, '', meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="position:absolute;bottom:{_y(lay["meta_bottom"])}px;'
                     f'left:{_x(lay["meta_left"])}px;color:#ffe9e6;'
                     f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(lay["meta_px"])}px;letter-spacing:{lay["meta_letter"]};'
                     f'z-index:8">{_m} · {lay["meta_suffix"]}</div>')
    # 右下大圆点：青底 120px + 黄描边环 14px（box-shadow 环；保留 v1）
    bd = lay['big_dot']
    big_dot = (f'<div style="position:absolute;bottom:{_y(bd["bottom"])}px;right:{_x(bd["right"])}px;'
               f'width:{_s(bd["d"])}px;height:{_s(bd["d"])}px;border-radius:50%;'
               f'background:{bd["color"]};box-shadow:0 0 0 {_s(bd["ring"])}px {bd["ring_color"]};'
               f'z-index:8"></div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {photo}
  {bar}
  {block}
  {hero_html}
  {en_html}
  {meta_html}
  {big_dot}
</div>'''


def _tpl_doodle_summer(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """涂鸦夏日（§1.3，探针 P3_doodle_summer__*.png）：照片洗白 + 白色上下渐隐 +
    中文大标题楷体 #2e5e3f 92px（left calc 基点 -5%，rotate -2°，白描影+绿投影；
    **标题完整在画面内**）+ EN 贴纸右下（白底 .92 橘字 26px 左黄边条 4px rotate -3°）+
    云朵三枚（top 250/180/296，left 均 calc(x-5%)）+ 橘红虚线飞镖箭头 SVG（top 60 right 40）+
    太阳 SVG（bottom 250 left 60）+ 左上黄胶带 + 底部固定文案两行。
    text_on_photo=True（标题/固定文案/EN 贴纸落洗白照片的渐隐带上，需人工核，不护脸）。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # 照片洗白 + 白色上下渐隐（180deg 四站点，config.fade_stops）
    photo = f'<div style="position:absolute;inset:0">{_img(uri, cfg["tone_filter"])}</div>'
    stops = ','.join(f'{col} {pct}%' for pct, col in lay['fade_stops'])
    fade = (f'<div style="position:absolute;inset:0;'
            f'background:linear-gradient(180deg,{stops})"></div>')
    # 中文大标题（--title）楷体 #2e5e3f 92px：left calc(60px - 5%)〔v2 左移 15% → v3 回调
    # +6%+4% 最终=-5% 基点〕rotate(-2°) 白描影+绿投影；fit 收敛（标题完整在画面内）
    hero_html = ''
    if T:
        hero_px = _s(cfg['scale']['hero_px'])
        hero_fs = fit_title_fs(T, int(W * 0.82), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;top:{_y(lay["hero_top"])}px;'
                     f'left:calc({_x(lay["hero_left_base"])}px + {lay["hero_left_pct"]});'
                     f'color:{cfg["palette"]["accent"]};'
                     f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};font-weight:700;'
                     f'font-size:{hero_fs}px;line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'transform:rotate({lay["hero_rot"]}deg);'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]};white-space:nowrap;z-index:5">{T}</div>')
    # EN 贴纸右下（--sub）：白底 .92 + 橘字 26px + 左黄边条 4px，rotate(-3°)，bottom 120 right 36
    en_html = ''
    if S:
        en_html = (f'<div style="position:absolute;bottom:{_y(lay["en_bottom"])}px;'
                   f'right:{_x(lay["en_right"])}px;background:{lay["en_bg"]};'
                   f'color:{cfg["palette"]["point"]};font-family:&quot;{cfg["fonts"]["hero"]}&quot;,'
                   f'{_serif_cn};font-size:{_s(lay["en_px"])}px;'
                   f'padding:{_y(lay["en_pad_y"])}px {_x(lay["en_pad_x"])}px;'
                   f'transform:rotate({lay["en_rot"]}deg);'
                   f'box-shadow:2px 3px 8px rgba(0,0,0,.18);'
                   f'border-left:{_s(lay["en_border_left"])}px solid {lay["en_border_color"]};'
                   f'z-index:5">{S}</div>')
    # 云朵三枚（探针 SVG 椭圆口径：每枚双 ellipse；left 均 calc(x - 5%)）
    clouds = ''
    for cl in lay['clouds']:
        vw, vh = cl['w'], cl['h']
        _op = cl['op']
        clouds += (f'<svg style="position:absolute;top:{_y(cl["top"])}px;'
                   f'left:calc({_x(cl["left"])}px - 5%)" width="{_x(vw)}" height="{_y(vh)}" '
                   f'viewBox="0 0 {vw} {vh}" preserveAspectRatio="none">'
                   f'<ellipse cx="{int(vw * 0.47)}" cy="{int(vh * 0.55)}" rx="{int(vw * 0.35)}" '
                   f'ry="{int(vh * 0.29)}" fill="#fff" opacity="{_op}"/>'
                   f'<ellipse cx="{int(vw * 0.73)}" cy="{int(vh * 0.44)}" rx="{int(vw * 0.23)}" '
                   f'ry="{int(vh * 0.2)}" fill="#fff" opacity="{_op}"/></svg>')
    # 橘红虚线飞镖箭头 SVG（top 60 right 40；探针终图口径：曲线虚线+实心箭头）
    aw, ah = lay['arrow_w'], lay['arrow_h']
    arrow = (f'<svg style="position:absolute;top:{_y(lay["arrow_top"])}px;'
             f'right:{_x(lay["arrow_right"])}px" width="{_x(aw)}" height="{_y(ah)}" '
             f'viewBox="0 0 {aw} {ah}" preserveAspectRatio="none">'
             f'<path d="M{int(aw * 0.09)} {int(ah * 0.73)} Q{int(aw * 0.27)} {int(ah * 0.2)} '
             f'{int(aw * 0.5)} {int(ah * 0.47)} T{int(aw * 0.91)} {int(ah * 0.27)}" '
             f'stroke="{cfg["palette"]["point"]}" stroke-width="4" fill="none" '
             f'stroke-dasharray="10 8"/>'
             f'<path d="M{int(aw * 0.85)} {int(ah * 0.2)} l{int(aw * 0.07)} {int(ah * 0.07)} '
             f'-{int(aw * 0.08)} {int(ah * 0.05)} z" fill="{cfg["palette"]["point"]}"/></svg>')
    # 太阳 SVG（bottom 250 left 60；圆心 + 8 根光芒线，rotate -8°）
    sw = lay['sun_px']
    sun = (f'<svg style="position:absolute;bottom:{_y(lay["sun_bottom"])}px;'
           f'left:{_x(lay["sun_left"])}px" width="{_s(sw)}" height="{_s(sw)}" '
           f'viewBox="0 0 120 120"><g transform="rotate(-8 60 60)">'
           f'<circle cx="60" cy="48" r="14" fill="{lay["en_border_color"]}"/>'
           f'<g stroke="{lay["en_border_color"]}" stroke-width="6" stroke-linecap="round">'
           f'<line x1="60" y1="12" x2="60" y2="26"/><line x1="60" y1="70" x2="60" y2="84"/>'
           f'<line x1="24" y1="48" x2="38" y2="48"/><line x1="82" y1="48" x2="96" y2="48"/>'
           f'<line x1="34" y1="22" x2="44" y2="32"/><line x1="76" y1="64" x2="86" y2="74"/>'
           f'<line x1="86" y1="22" x2="76" y2="32"/><line x1="44" y1="64" x2="34" y2="74"/>'
           f'</g></g></svg>')
    # 左上黄胶带
    tape = (f'<div style="position:absolute;top:{_y(lay["tape_top"])}px;left:{_x(lay["tape_left"])}px;'
            f'width:{_x(lay["tape_w"])}px;height:{_y(lay["tape_h"])}px;'
            f'background:rgba(240,214,120,.85);transform:rotate({lay["tape_rot"]}deg);'
            f'box-shadow:0 2px 6px rgba(0,0,0,.15);z-index:5"></div>')
    # 底部固定文案两行（foot=楷体 title_font 24px 字距 .3em〔繁体装饰文案随 title_font
    # 渲染+预检，设计稿 §2〕+ date · SKETCH DIARY mono 17px）
    foot = (f'<div style="position:absolute;bottom:{_y(lay["foot_bottom"])}px;left:0;right:0;'
            f'text-align:center;color:{cfg["palette"]["accent"]};'
            f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
            f'font-size:{_s(lay["foot_px"])}px;letter-spacing:{lay["foot_letter"]};'
            f'z-index:5">{lay["foot_text"]}</div>')
    _m = _meta(D, '', meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="position:absolute;bottom:{_y(lay["meta_bottom"])}px;left:0;right:0;'
                     f'text-align:center;color:#7a8a6f;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(lay["meta_px"])}px;letter-spacing:{lay["meta_letter"]};'
                     f'z-index:5">{_m} · {lay["meta_suffix"]}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {photo}
  {fade}
  {hero_html}
  {en_html}
  {clouds}
  {arrow}
  {sun}
  {tape}
  {foot}
  {meta_html}
</div>'''


def _photo_seed(uri):
    """照片内容哈希 → 词墙 seed（设计稿 §6：**内容哈希**，非 mtime 防重渲漂移、
    非路径——同一张照片换路径/复制渲染词墙布局不变）。读盘字节 md5；
    读失败（文件移动/权限）回退路径哈希（仍确定性，绝不掷随机）。"""
    from urllib.parse import unquote
    p = uri[len('file:///'):] if uri.startswith('file:///') else uri
    try:
        with open(unquote(p), 'rb') as f:
            return int(hashlib.md5(f.read()).hexdigest(), 16)
    except OSError:
        return int(hashlib.md5(uri.encode('utf-8')).hexdigest(), 16)


def _word_wall_params(words, rng, lay):
    """词墙逐词形态参数抽取（§1.4：五档字号/三色/四类形态）。
    **rng 单实例顺序消费**（§6 风险）：每词恰 3 次取随机（形态/字号/颜色），斜置词
    第 4 次（角度）——消费序列由分支结构固定，与后续缩档重建无关（参数抽取一次，
    渲染可带 scale 重建），保证同图同池结果可复现。"""
    sizes = lay['wall_sizes']
    colors = lay['wall_colors']
    ratio = lay['wall_ratio']
    tilt_max = lay['wall_tilt_max']
    v = ratio['vertical']
    t = v + ratio['tilt']
    o = t + ratio['outline']
    iv = o + ratio['inverse']
    params = []
    for w in words:
        r = rng.random()
        fs = rng.choice(sizes)
        color = rng.choice(colors)
        deg = 0
        if r < v:
            kind = 'v'
        elif r < t:
            kind = 't'
            deg = rng.randint(-tilt_max, tilt_max)
        elif r < o:
            kind = 'o'
        elif r < iv:
            kind = 'i'
        else:
            kind = 'n'
        params.append((kind, fs, color, deg, _html.escape(str(w))))
    return params


def _wall_est_height(params, words, W, lay):
    """词墙排版总高估算（服务端可测的"溢出即缩档"口径，§3 clip-safe 越界检查）。
    行填充贪心模拟：词宽≈Σ(汉字 1.0em / 其它 0.65em)×fs + 左右 margin + word-spacing
    （估宽系数与 type_guard.fit_title_fs 同源）；斜置词 ×1.25（旋转外接保守从宽）；
    竖排词宽=一列 fs（writing-mode），行高贡献=min(字数×fs, max_h)（保守取大）。
    估高≥实际（保守方向：只多缩不漏缩）。"""
    lh = lay['wall_lh']
    margin2 = lay['wall_margins'] * 2
    ws = lay['wall_word_gap']
    max_h = lay['wall_max_h']
    line_w = 0.0
    line_h = 0.0
    total = 0.0
    for (kind, fs, color, deg, _esc), w in zip(params, words):
        word = str(w)
        if kind == 'v':
            w_px = fs + margin2 + ws
            h_contrib = min(len(word) * fs, max_h)
        else:
            w_px = sum((fs if _is_cjk(c) else 0.65 * fs) for c in word) + margin2 + ws
            if kind == 't':
                w_px *= 1.25
            h_contrib = fs
        if line_w > 0 and line_w + w_px > W:
            total += line_h * lh
            line_w, line_h = 0.0, 0.0
        line_w += w_px
        line_h = max(line_h, h_contrib)
    return total + line_h * lh


def _wall_span(kind, fs, color, deg, esc_w, lay, wall_font, scale):
    """按形态参数渲染一个词 span（scale=溢出缩档因子，1.0=设计稿档位原值；
    字号下限 12px 同 fit_title_fs 口径）。"""
    fs = max(int(round(fs * scale)), 12)
    margin = lay['wall_margins']
    max_h = max(int(round(lay['wall_max_h'] * scale)), 12)
    base = (f'font-size:{fs}px;color:{color};font-family:&quot;{wall_font}&quot;,'
            f'{_sans_cn};font-weight:900;margin:0 {margin}px;letter-spacing:.02em')
    if kind == 'v':
        return (f'<span style="{base};writing-mode:vertical-rl;display:inline-block;'
                f'vertical-align:middle;max-height:{max_h}px">{esc_w}</span>')
    if kind == 't':
        return (f'<span style="{base};display:inline-block;'
                f'transform:rotate({deg}deg)">{esc_w}</span>')
    if kind == 'o':
        return (f'<span style="{base};color:transparent;'
                f'-webkit-text-stroke:2px {color}">{esc_w}</span>')
    if kind == 'i':
        return (f'<span style="font-size:{fs}px;background:{color};color:#f3efe6;'
                f'font-family:&quot;{wall_font}&quot;,{_sans_cn};font-weight:900;'
                f'margin:0 {margin}px;letter-spacing:.02em;padding:0 6px">{esc_w}</span>')
    return f'<span style="{base}">{esc_w}</span>'


def _word_wall(words, rng, lay, wall_font, W, H):
    """collage_man 词墙生成器（§0.5/§1.4）：三层词池（款格词+元数据词+用户词）已在调用侧
    组装传入；本函数做 seed 洗牌 + 逐词形态参数抽取 + 溢出缩档 + span 渲染。
    形态四类占比（设计语义）：竖排 14% / 斜置 10% / 空心 6% / 反白 6% / 常规 64%。
    洗牌用调用侧传入的 random.Random 单实例**顺序消费**（§6 风险：禁止多处独立取随机——
    seed 确定性由"同图同 seed + 单实例顺序消费"共同保证）。
    缩档（§3 clip-safe 越界检查）：五档字号豁免 fit（设计语义），但按 _wall_est_height
    估算总高超出可用高（H-wall_top）时整墙等比缩档（"溢出即缩档"），词墙容器
    overflow:hidden 为最终兜底。rng 消费只在参数抽取一次，缩档重建不改随机序列。
    返回 span 序列（已 esc——词表来自 config 固定文案 + CLI 参数，注入前逐词 escape）。"""
    import random as _random  # noqa: F401  （rng 由调用侧注入；保留 import 以示口径）
    params = _word_wall_params(words, rng, lay)
    avail = max(H - lay['wall_top'], 1)
    est = _wall_est_height(params, words, W, lay)
    scale = min(1.0, avail / est) if est > avail else 1.0
    return [_wall_span(k, fs, c, d, e, lay, wall_font, scale)
            for (k, fs, c, d, e) in params]


def _tpl_collage_man(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None,
                     words=None):
    """杂拼人物（§1.4 v3 融合版，探针 P4_collage_man__face.png）：底 #f3efe6 + 全高文字墙
    （_word_wall：三层词池+seed 洗牌+四类形态）+ 蛋形窗 605×691 居中 top 190 + 顶部红标 EN +
    全元素融合（v3 定稿 11 件：胶带×2/半调网点×3/贴纸×2/章×2/GO!!/WALK THIS WAY）+
    虚线箭头+看這裡!! 在蛋框左下（v3 终版：仅一条，指向蛋框；右侧旧箭头已删）+
    底部中文大标黑体 Heavy 76px 黑字红影。text_on_photo=False（蛋窗+bottom 文字=护脸）。
    words：CLI --words 注入的用户词（③层，缺省 None）。
    词墙五档字号为装饰性混排（设计语义），豁免 fit；受 clip-safe 越界检查——
    _wall_est_height 估总高超出可用高即整墙缩档（§3"溢出即缩档"），容器 overflow:hidden
    为最终兜底（词墙不越画布）。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    # ---- 词墙：三层词池组装 + seed=照片**内容**哈希（§6 风险：非 mtime 防重渲漂移、
    # 非路径——换路径/复制渲染词墙布局不变）。random.Random 单实例顺序消费
    #（词序洗牌 → 逐词形态/字号/颜色/角度，消费序列由分支结构固定）。同图两次渲染
    # 字节一致；异图（内容哈希不同）不重样。
    import random as _random
    pool = list(lay['words_a']) + list(lay['words_b'])
    # ②层 真实元数据词（每图天然不同；空缺省 '—' 不注入占位噪音）。
    # D/L 已在 render esc 过一次、meta_extra 此处 esc 一次——先 _unesc_once 还原，
    # 让 _word_wall_params 内统一 esc 恰好一次（防双转义；unesc→esc 往返对原文含
    # '&'/'&lt;' 字面量的极端输入同样安全，净效果=恰好一次转义）。
    def _unesc_once(s):
        return (s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>'))
    meta_words = [_unesc_once(w) for w in (D, L) if w]
    if meta_extra:
        meta_words.append(_unesc_once(_html.escape(meta_extra)))
    # ③层 用户词（--words 注入；其余款忽略此参数）
    user_words = [w.strip() for w in (words or []) if w and w.strip()]
    rng = _random.Random(_photo_seed(uri))
    rng.shuffle(pool)
    wall_words = pool + meta_words + user_words
    spans = _word_wall(wall_words, rng, lay, cfg['fonts']['hero'], W, H)
    wall = (f'<div style="position:absolute;top:{_y(lay["wall_top"])}px;left:0;right:0;bottom:0;'
            f'overflow:hidden;line-height:{lay["wall_lh"]};word-spacing:{_x(lay["wall_word_gap"])}px;'
            f'opacity:{lay["wall_opacity"]}">{"".join(spans)}</div>')
    # 蛋形窗（605×691 居中 top 200〔#56 下移 5%〕；10px 底色边+大投影；护脸核心：脸落窗内，文字不压窗）
    egg_w, egg_h = _x(lay['egg_w']), _y(lay['egg_h'])
    egg = (f'<div style="position:absolute;top:{_y(lay["egg_top"])}px;left:50%;'
           f'transform:translateX(-50%);width:{egg_w}px;height:{egg_h}px;'
           f'border-radius:{lay["egg_radius"]};overflow:hidden;'
           f'border:{_s(lay["egg_border"])}px solid {cfg["palette"]["primary"]};'
           f'box-shadow:{lay["egg_shadow"]};z-index:6">{_img(uri, cfg["tone_filter"])}</div>')
    # 顶部红标 EN（--sub；rotate -3°，居中）
    tag_html = ''
    if S:
        tag_html = (f'<div style="position:absolute;top:{_y(lay["tag_top"])}px;left:50%;'
                    f'transform:translateX(-50%) rotate({lay["tag_rot"]}deg);'
                    f'background:{cfg["palette"]["point"]};color:#fff;'
                    f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;font-weight:700;'
                    f'font-size:{_s(lay["tag_px"])}px;letter-spacing:{lay["tag_letter"]};'
                    f'padding:{_y(6)}px {_x(16)}px;z-index:8">{S}</div>')
    # 全元素融合（v3 定稿 11 件，config.elems 声明式逐件渲染；固定装饰文案）
    elems = ''
    for e in lay['elems']:
        pos = ''
        if 'top' in e:
            pos += f'top:{_y(e["top"])}px;'
        if 'bottom' in e:
            pos += f'bottom:{_y(e["bottom"])}px;'
        if 'left' in e:
            pos += f'left:{_x(e["left"])}px;'
        if 'right' in e:
            pos += f'right:{_x(e["right"])}px;'
        kind = e['kind']
        if kind == 'tape':
            elems += (f'<div style="position:absolute;{pos}width:{_x(e["w"])}px;'
                      f'height:{_y(e["h"])}px;background:rgba(240,214,120,.85);'
                      f'transform:rotate({e["rot"]}deg);'
                      f'box-shadow:0 2px 6px rgba(0,0,0,.15);z-index:3"></div>')
        elif kind in ('halftone_red', 'halftone_blue'):
            _hc = '#d33' if kind == 'halftone_red' else '#1b6fae'
            elems += (f'<div style="position:absolute;{pos}width:{_x(e["w"])}px;'
                      f'height:{_y(e["h"])}px;background:radial-gradient(circle,{_hc} 1.6px,'
                      f'transparent 1.8px);background-size:{e["cell"]}px {e["cell"]}px;'
                      f'transform:rotate({e["rot"]}deg);opacity:{e["op"]};z-index:3"></div>')
        elif kind == 'sticker':
            _sh = f'box-shadow:{e["shadow"]};' if e.get('shadow') else ''
            elems += (f'<div style="position:absolute;{pos}background:{e["bg"]};'
                      f'color:{e["color"]};font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                      f'font-weight:700;font-size:{_s(e["px"])}px;'
                      f'padding:{_y(e["pad_y"])}px {_x(e["pad_x"])}px;'
                      f'transform:rotate({e["rot"]}deg);{_sh}z-index:4">{e["text"]}</div>')
        elif kind in ('stamp_red', 'stamp_blue'):
            _sc = e['color']
            _bg = f'background:{e["bg"]};' if e.get('bg') else ''
            elems += (f'<div style="position:absolute;{pos}border:3px dashed {_sc};'
                      f'color:{_sc};font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                      f'font-weight:700;font-size:{_s(e["px"])}px;padding:{_y(6)}px {_x(10)}px;'
                      f'transform:rotate({e["rot"]}deg);letter-spacing:.2em;{_bg}z-index:4">'
                      f'{e["text"]}</div>')
        elif kind == 'go':
            # GO!! 红字黄影（探针 P4 终图口径：红 #d33 字 + 黄 #ffd23f 硬影）
            elems += (f'<div style="position:absolute;{pos}color:{cfg["palette"]["point"]};'
                      f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};font-weight:900;'
                      f'font-size:{_s(e["px"])}px;transform:rotate({e["rot"]}deg);'
                      f'text-shadow:2px 2px 0 #ffd23f;z-index:4">{e["text"]}</div>')
        elif kind == 'walk':
            elems += (f'<div style="position:absolute;{pos}color:#1b6fae;'
                      f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;font-weight:700;'
                      f'font-size:{_s(e["px"])}px;letter-spacing:.3em;'
                      f'transform:rotate({e["rot"]}deg);opacity:.75;z-index:4">{e["text"]}</div>')
    # 虚线箭头+看這裡!! 在蛋框左下（v3 终版：仅一条箭头，指向蛋框；黑虚线 rotate(-30°)）
    aw, ah = lay['arrow_w'], lay['arrow_h']
    arrow = (f'<svg style="position:absolute;bottom:{_y(lay["arrow_bottom"])}px;'
             f'left:{_x(lay["arrow_left"])}px;transform:rotate({lay["arrow_rot"]}deg);z-index:4" '
             f'width="{_x(aw)}" height="{_y(ah)}" viewBox="0 0 {aw} {ah}" preserveAspectRatio="none">'
             f'<path d="M{int(aw * 0.12)} {int(ah * 0.84)} Q{int(aw * 0.4)} {int(ah * 0.22)} '
             f'{int(aw * 0.79)} {int(ah * 0.48)}" stroke="#1a1a1a" stroke-width="4" fill="none" '
             f'stroke-dasharray="9 7"/>'
             f'<path d="M{int(aw * 0.72)} {int(ah * 0.38)} l{int(aw * 0.11)} {int(ah * 0.1)} '
             f'-{int(aw * 0.12)} {int(ah * 0.09)} z" fill="#1a1a1a"/></svg>')
    mark = (f'<div style="position:absolute;bottom:{_y(lay["mark_bottom"])}px;'
            f'left:{_x(lay["mark_left"])}px;color:#fff;background:{lay["mark_bg"]};'
            f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};font-weight:700;'
            f'font-size:{_s(lay["mark_px"])}px;padding:{_y(5)}px {_x(12)}px;'
            f'transform:rotate({lay["mark_rot"]}deg);box-shadow:2px 2px 0 rgba(0,0,0,.35);'
            f'z-index:4">{lay["mark_text"]}</div>')
    # 底部：中文大标黑体 Heavy 76px 黑字红影（居中）+ date · 型不设防城市展（mono 18px）
    hero_html = ''
    if T:
        hero_px = _s(cfg['scale']['hero_px'])
        hero_fs = fit_title_fs(T, int(W * 0.8), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;bottom:{_y(lay["hero_bottom"])}px;left:0;right:0;'
                     f'text-align:center;font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
                     f'font-weight:900;font-size:{hero_fs}px;color:{cfg["palette"]["accent"]};'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]};white-space:nowrap;'
                     f'z-index:8">{T}</div>')
    _m = _meta(D, '', meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="position:absolute;bottom:{_y(lay["meta_bottom"])}px;left:0;right:0;'
                     f'text-align:center;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(lay["meta_px"])}px;letter-spacing:{lay["meta_letter"]};'
                     f'color:#444;z-index:8">{_m} · {lay["meta_suffix"]}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {wall}
  {elems}
  {egg}
  {tag_html}
  {arrow}
  {mark}
  {hero_html}
  {meta_html}
</div>'''


# ===============================================================
# 构图三款（2026-09-08，docs/批量设计-构图三款-设计.md §1 终值 = 实现契约）共用 helper
# ===============================================================
# font_guard.check_and_wrap 兜底 span 的 style 前缀（缺字包裹产物识别用）——
# fg_texts dict 兜底后 layout 值已是「逐字 esc + 思源宋 span」的安全 HTML，直接嵌入
# 不再 esc（否则双转义，彩活批 _unesc_once 同教训）；未兜底值为原文，esc 恰好一次
_FG_SPAN_PREFIX = '<span style="font-family:\'思源宋体\',\'Songti SC\',serif;'


def _fg_html(val):
    """fg_texts 装饰文案 → (安全 HTML, fallback_used)。
    兜底产物（_FG_SPAN_PREFIX 开头）= 已 esc 的思源宋 span 串，原样嵌入；
    其余 = 原文，_html.escape 恰好一次。"""
    if val and val.startswith(_FG_SPAN_PREFIX):
        return val, True
    return _html.escape(val), False


def _star_svg(right, top, size, color, rot, stroke='#111', stroke_w=3):
    """爆炸星小星 SVG（pop_lichtenstein 黑条星群共用；探针 star_field 口径：十角星
    polygon viewBox 0 0 100 100 + #111 描边 + rotate）。大星走 div clip-path 不经此。"""
    pts = '50,0 61,35 98,35 68,57 79,91 50,70 21,91 32,57 2,35 39,35'
    return (f'<svg style="position:absolute;top:{top}px;right:{right}px;width:{size}px;'
            f'height:{size}px;transform:rotate({rot}deg)" viewBox="0 0 100 100">'
            f'<polygon points="{pts}" fill="{color}" stroke="{stroke}" '
            f'stroke-width="{stroke_w}"/></svg>')


def _halftone_css(dot_px, color, inner_px, gap):
    """半调网点 CSS（pop_press 刊头/底部满铺共用；探针口径：
    radial-gradient(circle {dot}px,{color} {inner}px,transparent {dot}px) + size gap）。"""
    return (f'background:radial-gradient(circle {dot_px}px,{color} {inner_px}px,'
            f'transparent {dot_px}px);background-size:{gap}px {gap}px')
# （_BEBAS_CSS 防御性冗余注：BebasNeue 已在基础 FONTS_CSS 内、无 config 把该名挂 fonts
#  三位，下方注入分支当前恒假——渲染由基础常量兜住；保留为将来款把 BebasNeue 挂
#  fonts 位时的按需注入占位，语义与 _LXGW_CSS 同口径。）


# ---------------------------------------------------------------
# branch_magazine · 折枝杂志（§1.1，探针终版 branch_折枝杂志__*.html / _gen_v5.py
# A4 同源分叉）：米白纸底 #f6f2ea + 双 radial 纸纹 + 左上文字块（黑体 Heavy 88px
# title 经 fit / EN Courier / 红杠 72×3 / 两行宋体固定文案）+ 右上竖排小字 +
# 花枝 SVG（branch_paths 坐标表写死）+ 双层照片窗（外裁左下；内窗 rotate -8°，
# right:30——A4 源码勘误值，见 config §1.1 勘误注）。
# 无日期行、无红章（v5 终版用户拍板删除）。hero=bottom_right 槽；
# text_on_photo=False 护脸（照片在独立斜切窗内，文字/花枝全落留白区）。
# ---------------------------------------------------------------
def _tpl_branch_magazine(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """折枝杂志（§1.1）：护脸款——双层斜切照片窗 + 左上文字块 + 右上竖排小字 + 花枝。"""
    lay = dict(cfg['layout'])
    # 横版覆盖（变更记录 2026-09-09 横版人工核补账）：H<W 时套用 landscape_overrides，
    # 竖排小字/花枝避开抬升的窗顶；竖版零改动
    if H < W and 'landscape_overrides' in lay:
        lay.update(lay['landscape_overrides'])

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    grain = (f'<div style="position:absolute;inset:0;'
             f'background:{lay["grain"]}"></div>')
    # 左上文字块：title（黑体 Heavy 88px，fit 容器宽=探针版面可用宽，长 title 一行缩档）
    title_html = ''
    if T:
        title_fs = fit_title_fs(T, _x(lay['title_fit_w']), _s(cfg['scale']['hero_px']),
                                cfg['scale']['hero_letter'])
        title_html = (f'<div style="position:absolute;top:{_y(lay["title_top"])}px;'
                      f'left:{_x(lay["title_left"])}px;color:{cfg["palette"]["accent"]};'
                      f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
                      f'font-weight:900;font-size:{title_fs}px;'
                      f'line-height:{cfg["scale"]["hero_lh"]};'
                      f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                      f'white-space:nowrap;z-index:3">{T}</div>')
    en_html = ''
    if S:
        # EN：Courier 24px 字距 .34em（A4 源码勘误值；长 EN fit 缩档——§4-7 边界口径）
        en_fs = fit_title_fs(S, _x(lay['en_fit_w']), _s(lay['en_px']), lay['en_letter'])
        en_html = (f'<div style="position:absolute;top:{_y(lay["en_top"])}px;'
                   f'left:{_x(lay["en_left"])}px;color:{lay["en_color"]};'
                   f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,monospace;'
                   f'font-size:{en_fs}px;letter-spacing:{lay["en_letter"]};'
                   f'white-space:nowrap;z-index:3">{S}</div>')
    rule = (f'<div style="position:absolute;top:{_y(lay["rule_top"])}px;'
            f'left:{_x(lay["rule_left"])}px;width:{_x(lay["rule_w"])}px;'
            f'height:{_s(lay["rule_h"])}px;background:{cfg["palette"]["point"]};'
            f'z-index:3"></div>')
    # 两行宋体固定文案（fg_texts dict 兜底产物直接嵌入，否则 esc 恰好一次；<br> 分行；
    # 字体族=SourceSerifHeavy 真字重（与 fg_texts 预检键一致——评审 #3）+ 系统衬线回退）
    k1, k1_fb = _fg_html(lay['kengei_l1'])
    k2, k2_fb = _fg_html(lay['kengei_l2'])
    kengei = (f'<div style="position:absolute;top:{_y(lay["kengei_top"])}px;'
              f'left:{_x(lay["kengei_left"])}px;color:{lay["kengei_color"]};'
              f'font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};'
              f'font-size:{_s(lay["kengei_px"])}px;'
              f'letter-spacing:{lay["kengei_letter"]};line-height:{lay["kengei_lh"]};'
              f'z-index:3">{k1}<br>{k2}</div>')
    # 右上竖排小字（固定装饰文案；字体族同上=与预检键一致）
    vt, vt_fb = _fg_html(lay['vtext'])
    vtext = (f'<div style="position:absolute;top:{_y(lay["vtext_top"])}px;'
             f'right:{_x(lay["vtext_right"])}px;writing-mode:vertical-rl;'
             f'color:{lay["vtext_color"]};font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};'
             f'font-size:{_s(lay["vtext_px"])}px;letter-spacing:{lay["vtext_letter"]};'
             f'z-index:3">{vt}</div>')
    # 花枝 SVG（branch_paths 坐标表写死；path/circle 两类，坐标不缩放——探针
    # 固定 297×285 viewBox 0 0 330 300，width/height 随 fs）
    parts = ''
    for p in lay['branch_paths']:
        if 'd' in p:
            stroke = (f'stroke="{p["stroke"]}" stroke-width="{p["sw"]}"'
                      if 'stroke' in p else '')
            op = f'opacity="{p["op"]}"' if 'op' in p else ''
            parts += f'<path d="{p["d"]}" {stroke} fill="{p["fill"]}" {op}/>'
        else:
            op = f'opacity="{p["op"]}"' if 'op' in p else ''
            parts += (f'<circle cx="{p["cx"]}" cy="{p["cy"]}" r="{p["r"]}" '
                      f'fill="{p["fill"]}" {op}/>')
    branch = (f'<svg style="position:absolute;top:{_y(lay["branch_top"])}px;'
              f'right:{_x(lay["branch_right"])}px;z-index:3" '
              f'width="{_x(lay["branch_w"])}" height="{_y(lay["branch_h"])}" '
              f'viewBox="0 0 330 300">{parts}</svg>')
    # 双层照片窗：外裁剪容器（bottom -10/right 0〔A4 源码勘误值〕，overflow hidden 只裁左下）→
    # 内窗（bottom 55/right 30 rotate -8°，14px 底色边 + outline + 大投影）→
    # img 反转 8° scale 1.18（right=30 保竖排小字与窗右上角完整，勘误注见 config）
    # 2026-09-14 微调批2 #57：内窗 676→744（+10%）/ 上移 5%（bottom 30→55）；外容器仅尺寸
    # 随动 760→828→864（864 = 2026-09-15 微调批3 A#1a：装下 -8° 包围盒 840.3px；win_outer_bottom
    # 保持 −10，外容器不位移——位移会使内窗绝对位移翻倍）。
    win = (f'<div style="position:absolute;bottom:{_y(lay["win_outer_bottom"])}px;'
           f'right:{_x(lay["win_outer_right"])}px;width:{_x(lay["win_outer_w"])}px;'
           f'height:{_y(lay["win_outer_h"])}px;overflow:hidden;z-index:4">'
           f'<div style="position:absolute;bottom:{_y(lay["win_bottom"])}px;'
           f'right:{_x(lay["win_right"])}px;width:{_x(lay["win_w"])}px;'
           f'height:{_y(lay["win_h"])}px;transform:rotate({lay["win_rot"]}deg);'
           f'overflow:hidden;box-shadow:{lay["win_shadow"]};'
           f'border:{_s(lay["win_border"])}px solid {lay["win_border_color"]};'
           f'outline:{lay["win_outline"]}">'
           f'<img class="ph" src="{uri}" style="transform:rotate({lay["img_rot"]}deg) '
           f'scale({lay["img_scale"]});filter:{cfg["tone_filter"]};'
           f'object-position:{lay["img_pos"]}"></div></div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {grain}
  {title_html}
  {en_html}
  {rule}
  {kengei}
  {vtext}
  {branch}
  {win}
</div>'''


# ---------------------------------------------------------------
# pop_lichtenstein · 波普宣言（§1.2，探针 tpl_02c 移植）：黄底 Ben-Day 圆点 + 内框
# 4px #111 + 原色照片窗（top 78/侧 24/高 76%）+ 大红爆炸星 148px 破界压照片底缘
# （clip-path 十角星 rotate -8°，内嵌 BebasNeue WOW!/POP!；**有意构图**）+
# 漫画对话框（LXGWWenKai bold 17px {title}/太可愛了！）+ 底部黑条（黄字 title 28px +
# Courier 11px meta 行）+ 黑条星群 12 颗（坐标表写死，转角 seed=7 预计算）。
# hero=bottom_center；text_on_photo=True（星/星群破界压照片底缘，需人工核）。
# ---------------------------------------------------------------
def _tpl_pop_lichtenstein(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """波普宣言（§1.2）：利希滕斯坦漫画式自由拼贴，星群破界为原稿有意构图。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    dots_bg = (f'background:radial-gradient(circle {_s(lay["dot_px"])}px,'
               f'{lay["dot_color"]} {_s(lay["dot_inner"])}px,transparent {_s(lay["dot_px"])}px);'
               f'background-size:{_x(lay["dot_gap"])}px {_x(lay["dot_gap"])}px;'
               f'opacity:{lay["dot_opacity"]}')
    photo = (f'<div style="position:absolute;top:{_y(lay["photo_top"])}px;'
             f'left:{_x(lay["photo_side"])}px;right:{_x(lay["photo_side"])}px;'
             f'height:{lay["photo_h_pct"]}%;overflow:hidden;'
             f'border:{_s(lay["photo_border"])}px solid {lay["frame_color"]};z-index:5">'
             f'<img class="ph" src="{uri}" style="{cfg["tone_filter"]};'
             f'object-position:{lay["photo_pos"]}"></div>')
    # 大红爆炸星（div clip-path + drop-shadow；内嵌 BebasNeue 两行白字）
    star = (f'<div style="position:absolute;top:{_y(lay["star_top"])}px;'
            f'left:{_x(lay["star_left"])}px;width:{_s(lay["star_px"])}px;'
            f'height:{_s(lay["star_px"])}px;background:{lay["star_color"]};'
            f'clip-path:{lay["star_clip"]};display:flex;align-items:center;'
            f'justify-content:center;transform:rotate({lay["star_rot"]}deg);z-index:20;'
            f'filter:drop-shadow({lay["star_shadow"]})">'
            f'<div style="font-family:&quot;BebasNeue&quot;,sans-serif;'
            f'font-size:{_s(lay["star_text_px"])}px;color:#fff;text-align:center;'
            f'line-height:1">{lay["star_text"]}<br>'
            f'<span style="font-size:{_s(lay["star_text2_px"])}px">{lay["star_text2"]}</span>'
            f'</div></div>')
    # 漫画对话框：{title}（esc 参数）+ 固定装饰文案（fg 兜底产物直接嵌入）
    bt, bt_fb = _fg_html(lay['bubble_text'])
    bub = (f'<div style="position:absolute;top:{_y(lay["bub_top"])}px;'
           f'right:{_x(lay["bub_right"])}px;background:#fff;'
           f'border:{_s(lay["bub_border"])}px solid {lay["frame_color"]};'
           f'border-radius:50%;padding:{_y(lay["bub_pad_y"])}px {_x(lay["bub_pad_x"])}px;'
           f'z-index:20;transform:rotate({lay["bub_rot"]}deg);'
           f'box-shadow:{lay["bub_shadow"]};max-width:{_x(lay["bub_max_w"])}px;'
           f'text-align:center">'
           f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
           f'font-size:{_s(lay["bub_px"])}px;color:{lay["frame_color"]};font-weight:bold;'
           f'line-height:{lay["bub_lh"]}">{T}<br>{bt}</div></div>')
    # 底部黑条（黄字 title + Courier 11px meta 行；suffix 固定装饰文案）
    _m = _meta(D, L, meta_extra)
    bar_meta = ''
    if _m:
        bar_meta = (f'<div style="position:relative;z-index:16;'
                    f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                    f'font-size:{_s(lay["bar_meta_px"])}px;color:#fff;'
                    f'letter-spacing:{lay["bar_meta_letter"]};'
                    f'margin-top:3px">{_m} · {lay["bar_suffix"]}</div>')
    bar_title = ''
    if T:
        # §2 契约「pop 二款 title fit」：黑条 title 28px fit 收敛（黑条宽-左右 padding，
        # 超长一行缩档不折行不压照片区；容器宽扣内框 frame_pad/border——终审 🔵 修正）
        _bt_w = (W - 2 * (_x(lay['frame_pad']) + _s(lay['frame_border'])
                          + _x(lay['bar_side']) + _x(lay['bar_pad_x'])))
        bar_title = (f'<div style="position:relative;z-index:16;'
                     f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                     f'font-size:{fit_title_fs(T, _bt_w, _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                     f'color:{cfg["palette"]["primary"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'white-space:nowrap">{T}</div>')
    # 黑条星群 12 颗（坐标+转角全在 config 写死；描边 max(3, size/8) 探针口径）
    star_field = ''.join(
        _star_svg(_x(st['right']), _y(st['top']), _s(st['size']), st['color'], st['rot'],
                  lay['star_field_color'], max(3, int(st['size'] / 8)))
        for st in lay['stars'])
    bar = (f'<div style="position:absolute;bottom:{_y(lay["bar_bottom"])}px;'
           f'left:{_x(lay["bar_side"])}px;right:{_x(lay["bar_side"])}px;'
           f'background:{lay["frame_color"]};'
           f'padding:{_y(lay["bar_pad_y"])}px {_x(lay["bar_pad_x"])}px;z-index:15">'
           f'{star_field}{bar_title}{bar_meta}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]};padding:{_y(lay["frame_pad"])}px">
  <div style="position:relative;width:100%;height:100%;overflow:hidden;
              border:{_s(lay["frame_border"])}px solid {lay["frame_color"]};
              background:{cfg["palette"]["primary"]}">
    <div style="position:absolute;inset:0;{dots_bg}"></div>
    {photo}
    {star}
    {bub}
    {bar}
  </div>
</div>'''


# ---------------------------------------------------------------
# pop_press · 报纸印刷波普（§1.3，探针 tpl_04c + pop04d 渐隐参数移植）：外框
# #e8e2d2 padding 17 + 内版 #f2ecdc 3.5px 黑边 + 三段律（13/74/13）+ 刊头半调网点
# 满铺 + 渐隐 mask 加速版（45% 衰减中点=v4d 用户拍板）+ 原色照片 + 白网点 overlay +
# 底部镜像渐隐 + 底部文字（padding-bottom 26=v5 拍板）。
# hero=bottom_center；text_on_photo=True（网点满铺，需人工核）。
# ---------------------------------------------------------------
def _tpl_pop_press(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """报纸印刷波普（§1.3）：三段律 + 半调网点渐隐 + 白网点制版感。"""
    lay = cfg['layout']

    def _x(v): return int(round(v * fx))

    def _y(v): return int(round(v * fy))

    def _s(v): return int(round(v * fs))
    halo = _halftone_css(_s(lay['halo_px']), cfg['palette']['accent'], _s(lay['halo_inner']),
                         _s(lay['halo_gap']))
    # 渐隐 mask（加速版 v4d：config.fade_stops 四站点；head=180deg / foot=0deg 镜像）
    stops = ','.join(f'rgba(0,0,0,{a}) {p}%' for p, a in lay['fade_stops'])
    fade_head = f'linear-gradient(180deg,{stops})'
    fade_foot = f'linear-gradient(0deg,{stops})'
    halo_head = (f'<div style="position:absolute;inset:0;{halo};'
                 f'-webkit-mask-image:{fade_head};mask-image:{fade_head}"></div>')
    halo_foot = (f'<div style="position:absolute;inset:0;{halo};'
                 f'-webkit-mask-image:{fade_foot};mask-image:{fade_foot}"></div>')
    # 刊头（title 纸色光晕 + EN 黑底白字条；长 EN fit 缩档防溢出横版）
    en_bar = ''
    if S:
        en_fs = fit_title_fs(S, _x(lay['en_bar_max_w']), _s(lay['en_bar_px']),
                             lay['en_bar_letter'])
        en_bar = (f'<div style="display:inline-block;margin-top:8px;background:#111;'
                  f'color:{cfg["palette"]["point"]};'
                  f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                  f'font-size:{en_fs}px;letter-spacing:{lay["en_bar_letter"]};'
                  f'padding:{_y(lay["en_bar_pad_y"])}px {_x(lay["en_bar_pad_x"])}px;'
                  f'position:relative;z-index:4">{S}</div>')
    head_text = (f'<div style="position:relative;text-align:center;'
                 f'padding-top:{_y(lay["head_pad_top"])}px;z-index:3">'
                 f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                 f'font-size:{fit_title_fs(T, int(W * 0.86), _s(cfg["scale"]["hero_px"]), cfg["scale"]["hero_letter"])}px;'
                 f'color:{cfg["palette"]["accent"]};'
                 f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                 f'line-height:{cfg["scale"]["hero_lh"]};'
                 f'white-space:nowrap;'
                 f'text-shadow:{lay["head_glow"]}">{T}</div>'
                 f'{en_bar}</div>')
    head = (f'<div style="position:absolute;top:0;left:0;right:0;'
            f'height:{lay["head_h_pct"]}%;background:{cfg["palette"]["point"]};'
            f'z-index:5">{halo_head}{head_text}</div>')
    # 照片区（原色 + 白网点 overlay 制版感）
    overlay = (f'background:radial-gradient(circle {_s(lay["ov_px"])}px,'
               f'rgba(255,255,255,.95) {_s(lay["ov_inner"])}px,'
               f'transparent {_s(lay["ov_px"])}px);'
               f'background-size:{_s(lay["ov_gap"])}px {_s(lay["ov_gap"])}px;'
               f'mix-blend-mode:overlay;opacity:{lay["ov_opacity"]}')
    photo = (f'<div style="position:absolute;top:{lay["head_h_pct"]}%;'
             f'left:{_x(lay["photo_side"])}px;right:{_x(lay["photo_side"])}px;'
             f'height:{lay["photo_h_pct"]}%;overflow:hidden;'
             f'border:{_s(lay["photo_border"])}px solid {cfg["palette"]["accent"]};z-index:10">'
             f'<img class="ph" src="{uri}" style="{cfg["tone_filter"]};'
             f'object-position:{lay["photo_pos"]}">'
             f'<div style="position:absolute;inset:0;{overlay}"></div></div>')
    # 底部（镜像渐隐；{title} · 網點城市 + 固定楷体句；padding-bottom 26=v5 拍板）
    fc, fc_fb = _fg_html(lay['foot_city'])
    ft, ft_fb = _fg_html(lay['foot_text'])
    foot_text = (f'<div style="position:relative;z-index:3;display:flex;'
                 f'flex-direction:column;justify-content:center;height:100%;'
                 f'text-align:center;padding-bottom:{_y(lay["foot_pad_bottom"])}px">'
                 f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                 f'font-size:{fit_title_fs(T, int(W * 0.86), _s(lay["foot_title_px"]), lay["foot_title_letter"])}px;'
                 f'color:{cfg["palette"]["accent"]};'
                 f'letter-spacing:{lay["foot_title_letter"]};'
                 f'line-height:1;white-space:nowrap;text-shadow:{lay["head_glow"]}">{T} '
                 f'<span style="color:{lay["foot_sep_color"]}">·</span> {fc}</div>'
                 f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                 f'font-size:{_s(lay["foot_text_px"])}px;color:{cfg["palette"]["accent"]};'
                 f'margin-top:8px;letter-spacing:{lay["foot_text_letter"]};'
                 f'font-weight:bold;text-shadow:{lay["head_glow"]}">{ft}</div></div>')
    foot = (f'<div style="position:absolute;bottom:0;left:0;right:0;'
            f'height:{lay["foot_h_pct"]}%;background:{cfg["palette"]["point"]};'
            f'z-index:5">{halo_foot}{foot_text}</div>')
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]};padding:{_y(lay["frame_pad"])}px">
  <div style="position:relative;width:100%;height:100%;overflow:hidden;
              border:{_s(lay["inner_border"])}px solid {cfg["palette"]["accent"]};
              background:{cfg["palette"]["point"]}">
    {head}
    {photo}
    {foot}
  </div>
</div>'''


# ===============================================================
# 撕纸手帐（2026-09-09，docs/批量设计-torn_journal-设计.md §1.4 · 第 14 款）
# ===============================================================
def _tpl_torn_journal(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """撕纸手帐（§1.4，探针 v6 定稿 _gen_torn_journal.py）：米白手作纸底（四层底纹：
    云斑/颗粒 multiply + 高光 screen + 46 纤维飞点）+ 顶部楷体逐字微旋转主标（中间字
    朱红 1.1em）+ 居中照片直撕（2026-09-25 用户裁定：照片撑满撕边、取消白边装裱环带，
    外层深咬口撕边 70-100px + 毛絮化 fiber 滤镜 + 整体 rotate -1.4°）+ 左右竖排小字轨道（右轨 date=全款唯一日期）+ 14 件手绘蓝系
    涂鸦（气泡/喇叭/T恤/go!徽章/猫/纸飞机等，部分轻搭照片边缘=拼贴语义）+ 底部日文
    小字/英文手写行/满宽波浪。
    本款特殊：撕纸块=刚性块禁非等比缩放 → 忽略家族 fx/fy/fs，统一缩放因子
    s=min(W/900,H/1200)、原点偏移 ox/oy（§1.1）；底纹层 inset:0 不满缩（feTurbulence
    程序化铺满 W×H），纤维飞点/点表在基准坐标系内随 s 缩放。
    font_guard 兜底协同（§1.4）：render 传 T_eff（缺字兜底串含 <span 标记）→ 整串
    直排不逐字旋转（兜底路径可读性优先）；fit 按兜底串提纯后的纯文本估宽（先 fit 后包）。
    text_on_photo=True（气泡/喇叭/T恤/go!徽章/白竖排短语轻搭照片边缘，需人工核，
    不护脸；主标/副标/竖排轨道全落纸面）。"""
    lay = cfg['layout']
    esc = _html.escape

    # ---- §1.1 本款统一缩放（忽略家族 fx/fy/fs）----
    s = min(W / 900, H / 1200)
    ox = (W - 900 * s) / 2
    oy = max(0, (H - 1200 * s) / 2)

    def _x(v):
        r = int(round(v * s)) + ox
        return int(r) if r == int(r) else round(r, 2)

    def _y(v):
        r = int(round(v * s)) + oy
        return int(r) if r == int(r) else round(r, 2)

    def _r(v):
        r = int(round(v * s)) + ox          # right 基准偏移（距右缘，同 _x 口径）
        return int(r) if r == int(r) else round(r, 2)

    def _sv(v):
        return int(round(v * s))            # 尺寸/字号：只随 s，不加偏移

    def _f(v):
        return round(v * s, 1)              # 点表坐标（polygon px 保留 1 位，探针口径）

    # ---- 底纹第 4 层：纤维飞点（config 字面量 (x,y,deg,len) 随 s 缩放；端点 :.0f=探针）----
    lay_f = lay['filter_fiber']
    _fle = []
    for x, y, a, l in lay['flecks']:
        c = math.cos(math.radians(a)) * l / 2
        sn = math.sin(math.radians(a)) * l / 2
        _fle.append(f'<path d="M{x * s - c + ox:.0f} {y * s - sn + oy:.0f} '
                    f'L{x * s + c + ox:.0f} {y * s + sn + oy:.0f}"/>')
    flecks = ''.join(_fle)

    # ---- 主标逐字 span（font_guard 兜底协同 §1.4）：T 含兜底 span 标记 → 整串直排；
    # 否则 unescape 还原后逐字 esc+微旋转，中间字朱红 1.1em。fit 均按提纯文本估宽。
    if '<span' in T:
        title_html = T                      # font_guard 缺字兜底串整串直排（可读性优先）
        _chunks = T.split('>')
        T_fit = _html.unescape(''.join(c.split('<', 1)[0] for c in _chunks[1:]))
    else:
        _T = _html.unescape(T)
        T_fit = _T
        n = len(_T)
        mid = n // 2
        rots = lay['hero_rot_cycle']
        _parts = []
        for i, ch in enumerate(_T):
            rot = rots[i % 4]
            if i == mid and n >= 3:
                _parts.append(f'<span style="display:inline-block;color:{cfg["palette"]["point"]};'
                              f'font-size:{lay["hero_accent_px"]}em;'
                              f'transform:rotate({rot}deg)">{esc(ch)}</span>')
            else:
                _parts.append(f'<span style="display:inline-block;'
                              f'transform:rotate({rot}deg)">{esc(ch)}</span>')
        title_html = ''.join(_parts)

    # 主标 fit（792 = 0.88×900 基准宽，§1.1）
    hero_html = ''
    if T:
        hero_px = _sv(cfg['scale']['hero_px'])
        hero_fs = fit_title_fs(T_fit, _sv(792), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;top:{_y(lay["hero_top"])}px;left:0;width:100%;'
                     f'text-align:center;color:{lay["ink"]};'
                     f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                     f'font-size:{hero_fs}px;line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]};z-index:5">{title_html}</div>')

    # 副标（--sub）顶部 Caveat 手写行
    sub_html = ''
    if S:
        sub_html = (f'<div style="position:absolute;top:{_y(lay["sub_top"])}px;left:0;width:100%;'
                    f'text-align:center;color:{lay["sub_color"]};'
                    f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,cursive;'
                    f'font-size:{_sv(cfg["scale"]["lead_px"])}px;letter-spacing:2px;'
                    f'z-index:5">{S}</div>')

    # ---- 撕纸直撕四段（2026-09-25 裁定；审查修复 F1：删 torn_inner 死变量+旧层序注释）
    # [白衬 poly2c → 撕层 tjsplit → 照片 clip poly2 外环 → img]；torn_inner 直撕后模板
    # 不再引用（config 参数保留+自检断言，见设计档 §1.3）；照片零像素改动 P0-1）----
    poly2 = ' '.join(f'{_f(px):g}px {_f(py):g}px' for px, py in lay['torn_outer'])
    # 撕裂白衬（2026-09-25 四段定稿）：0-4px 抖动断续微缝 —— 只垫"照片被撕碎"的毛刺
    # 拉开处（撕裂断面露白），非均匀描边；照片本体由撕层 filter tjsplit 高频位移打毛。
    _kx = (lay["wrap_w"] + 4) / lay["wrap_w"]; _ky = (lay["wrap_h"] + 4) / lay["wrap_h"]
    poly2c = ' '.join(f'{_f(px * _kx + (i % 5) - 2):g}px {_f(py * _ky + (i * 3 % 5) - 2):g}px'
                      for i, (px, py) in enumerate(lay['torn_outer']))
    torn = (f'<div style="position:absolute;top:{_y(lay["frame_top"])}px;'
            f'left:{_x((900 - lay["wrap_w"]) // 2)}px;width:{_sv(lay["wrap_w"])}px;height:{_sv(lay["wrap_h"])}px;'
            f'transform:rotate({lay["frame_rot"]}deg);">'
            f'<div style="position:absolute;inset:0;'
            f'filter:url(#tjfiber) drop-shadow(4px 7px 12px rgba(90,80,60,.35));">'
            f'<div style="position:absolute;inset:0;clip-path:polygon({poly2});'
            f'background:{lay["paper_color"]};">'
            f'<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="100%" height="100%" filter="url(#tjpapernoise)" '
            f'style="mix-blend-mode:multiply"/></svg></div></div>'
            # 照片直撕四段结构：白衬(0-4px 断续) → 撕层(tjsplit 毛刺) → 照片 clip poly2 → img
            f'<div style="position:absolute;top:-2px;left:-2px;'
            f'width:{_sv(lay["wrap_w"] + 4)}px;height:{_sv(lay["wrap_h"] + 4)}px;'
            f'clip-path:polygon({poly2c});background:{lay["paper_color"]};">'
            f'<div style="position:absolute;top:2px;left:2px;'
            f'width:{_sv(lay["wrap_w"])}px;height:{_sv(lay["wrap_h"])}px;'
            f'filter:url(#tjsplit);">'
            f'<div style="position:absolute;top:0;left:0;'
            f'width:{_sv(lay["wrap_w"])}px;height:{_sv(lay["wrap_h"])}px;'
            f'clip-path:polygon({poly2});overflow:hidden;">'
            f'<img src="{uri}" style="width:100%;height:100%;object-fit:cover;'
            f'transform:scale(1.03)"></div></div></div></div>')

    # ---- 涂鸦 14 件（config 字面量；item 编码 S=描边线稿 F=实心填充 R=矩形 A=弧线
    # W=细轨迹 C=circle D=实心点；第 14 件=竖排短语右 cat_phrase；探针 DOM 层序分组）----
    dds = lay['doodles']

    def _svg(k, inner):
        p = dds[k]
        lft = p['left'] if 'left' in p else 900 - p['right'] - p['w']   # right 基准 → left px
        return (f'<svg style="position:absolute;top:{_y(p["top"])}px;left:{_x(lft)}px" '
                f'width="{_sv(p["w"])}" height="{_sv(p["h"])}" '
                f'xmlns="http://www.w3.org/2000/svg">{inner}</svg>')

    def _line(d, color, w):
        return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{_sv(w)}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')

    # 顶部组：波浪行 + 雨滴线（探针 :208-215）
    dd_top = (_svg('wave_top', _line(*dds['wave_top']['paths'][0]))
              + _svg('rain_line', ''.join(_line(*pp) for pp in dds['rain_line']['paths'])))
    # 弧线/猫/竖排短语右/虚点行组（探针 :220-240；猫与短语在撕纸 wrap 下层）
    cat_items = []
    for it in dds['cat']['items']:
        if it.startswith('C:'):
            cx, cy, r = it[2:].split(',')
            cat_items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none"/>')
        elif it.startswith('D:'):
            cx, cy, r = it[2:].split(',')
            cat_items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{dds["cat"]["stroke"]}"/>')
        else:
            cat_items.append(_line(it, dds['cat']['stroke'], 3))
    dd_arc_cat_dots = (_svg('title_arc', _line(*dds['title_arc']['paths'][0]))
                       + _svg('cat', ''.join(cat_items))
                       + f'<div style="position:absolute;top:{_y(dds["cat_phrase"]["top"])}px;'
                         f'right:{_r(dds["cat_phrase"]["right"])}px;left:auto;writing-mode:vertical-rl;'
                         f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
                         f'font-size:{_sv(dds["cat_phrase"]["px"])}px;color:{lay["tr_vtext_color"]};'
                         f'letter-spacing:6px;line-height:1.9;z-index:5">{lay["tr_vtext"]}</div>'
                       + _svg('dots_row', '<g fill="' + lay['accent_2'] + '">' + ''.join(
                           f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
                           for cx, cy, r in dds['dots_row']['circles']) + '</g>'))
    # 气泡（纸色填充 .82）+ 气泡文本（探针 :254-260）
    bub = dds['bubble']
    dd_bubble = (_svg('bubble',
                      f'<path d="{bub["paths"][0][0]}" fill="{lay["paper_color"]}" fill-opacity="0.82" '
                      f'stroke="{lay["accent_3"]}" stroke-width="{_sv(4)}" stroke-linejoin="round"/>'
                      + ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{lay["paper_color"]}" '
                                f'fill-opacity="0.82" stroke="{lay["accent_3"]}" stroke-width="{_sv(w)}"/>'
                                for cx, cy, r, w in bub['extra_circles']))
                + f'<div style="position:absolute;top:{_y(bub["txt_top"])}px;left:{_x(bub["txt_left"])}px;'
                  f'width:{_sv(bub["txt_w"])}px;font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
                  f'font-size:{_sv(lay["phrase_px"])}px;color:{lay["bubble_color"]};'
                  f'text-align:center;line-height:1.55;z-index:5">'
                  f'{lay["bubble_l1"]}<br>{lay["bubble_l2"]}</div>')
    # 喇叭（F 实心 + R 矩形 + A 弧线；探针 :263-269）
    _mega = []
    for d, m in dds['megaphone']['items']:
        if m == 'A':
            _mega.append(_line(d, lay['accent_3'], 4))
        elif m == 'R':
            rx, ry, rw, rh = d.split(',')
            _mega.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{lay["accent_3"]}"/>')
        else:
            _mega.append(f'<path d="{d}" fill="{lay["accent_3"]}"/>')
    dd_mega = _svg('megaphone', ''.join(_mega))
    # ×××/螺旋箭头/T恤/go!徽章（探针 :280-305；T恤/徽章压照片右下=拼贴语义）
    bd = dds['badge']
    dd_low = (_svg('xxx', ''.join(_line(*pp) for pp in dds['xxx']['paths']))
              + _svg('spiral', ''.join(_line(*pp) for pp in dds['spiral']['paths']))
              + _svg('tshirt',
                     f'<path d="{dds["tshirt"]["items"][0][0]}" fill="none" stroke="{lay["accent_3"]}" '
                     f'stroke-width="{_sv(4)}" stroke-linejoin="round"/>')
              + _svg('badge', f'<ellipse cx="{bd["ellipse"][0]}" cy="{bd["ellipse"][1]}" '
                              f'rx="{bd["ellipse"][2]}" ry="{bd["ellipse"][3]}" '
                              f'fill="{lay["accent_2"]}" opacity="0.92"/>')
              + f'<div style="position:absolute;top:{_y(bd["txt_top"])}px;right:{_r(bd["txt_right"])}px;'
                f'width:{_sv(bd["w"])}px;font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,cursive;'
                f'font-size:{_sv(bd["txt_px"])}px;color:#fff;text-align:center;'
                f'z-index:5">{bd["text"]}</div>')
    # 纸飞机（S 主形 + W 细轨迹；探针 :311-316，随底部组）
    _pln = []
    for d, m in dds['plane']['items']:
        if m == 'S':
            _pln.append(f'<path d="{d}" fill="none" stroke="{lay["accent_2"]}" stroke-width="{_sv(3.5)}" '
                        f'stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            _pln.append(f'<path d="{d}" fill="none" stroke="{lay["accent_2"]}" stroke-width="{_sv(2.5)}" '
                        f'stroke-linecap="round"/>')
    dd_plane = _svg('plane', ''.join(_pln))
    dd_foot_wave = _svg('wave_foot', _line(*dds['wave_foot']['paths'][0]))

    # ---- 文字小元素（竖排轨道；右轨 date=全款唯一日期；探针 :272-277）----
    def _vtxt(txt, style, color, px, ls):
        return (f'<div style="position:absolute;{style};writing-mode:vertical-rl;'
                f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
                f'font-size:{_sv(px)}px;color:{color};letter-spacing:{ls}px;'
                f'line-height:1.9;z-index:5">{txt}</div>')

    tracks = (_vtxt(L, f'top:{_y(lay["rail_loc_y"])}px;left:{_x(lay["rail_loc_x"])}px',
                    cfg['palette']['accent'], lay['vtext_px'], 8)
              + _vtxt(lay['left_phrase'], f'top:{_y(lay["rail_phrase_y"])}px;left:{_x(lay["rail_phrase_x"])}px',
                      lay['accent_2'], lay['phrase_px'], 8)
              + _vtxt(D, f'top:{_y(lay["rail_date_y"])}px;right:{_r(lay["rail_date_right"])}px;left:auto',
                      lay['tr_vtext_color'], lay['vtext_px'], 6)
              + f'<div style="position:absolute;top:{_y(lay["photo_phrase_y"])}px;'
                f'right:{_r(lay["photo_phrase_right"])}px;writing-mode:vertical-rl;'
                f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
                f'font-size:{_sv(lay["photo_phrase_px"])}px;color:{lay["sub_color"]};letter-spacing:7px;'
                f'opacity:.92;text-shadow:0 0 6px rgba(255,255,255,.7);z-index:5">'
                f'{lay["photo_phrase"]}</div>')

    # ---- 底部四行：日文小字/英文手写行/纸飞机/灰色注脚/满宽波浪（探针 :308-320）----
    foot = (f'<div style="position:absolute;top:{_y(lay["foot_jp_y"])}px;left:0;width:100%;text-align:center;'
            f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
            f'font-size:{_sv(lay["foot_jp_px"])}px;color:{cfg["palette"]["accent"]};'
            f'z-index:5">{lay["foot_jp"]}</div>'
            f'<div style="position:absolute;top:{_y(lay["foot_en_y"])}px;left:0;width:100%;text-align:center;'
            f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,cursive;'
            f'font-size:{_sv(lay["foot_en_px"])}px;letter-spacing:3px;color:{lay["foot_en_color"]};'
            f'z-index:5">{lay["foot_en"]}</div>'
            + dd_plane
            + f'<div style="position:absolute;top:{_y(lay["note_y"])}px;left:0;width:100%;text-align:center;'
              f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
              f'font-size:{_sv(lay["note_px"])}px;letter-spacing:2px;color:{lay["small_note_color"]};'
              f'z-index:5">{lay["small_note"]}</div>'
            + dd_foot_wave)

    # ---- 滤镜库（5 只 feTurbulence，参数=探针逐字；id 前缀 tj=款内隔离）----
    m, g, sh, pn = lay['filter_mottle'], lay['filter_grainf'], lay['filter_sheen'], lay['filter_papernoise']
    defs = (f'<svg width="0" height="0" style="position:absolute" xmlns="http://www.w3.org/2000/svg"><defs>'
            f'<filter id="tjfiber" x="-5%" y="-5%" width="110%" height="110%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{lay_f["bf"]}" numOctaves="{lay_f["oct"]}" seed="{lay_f["seed"]}" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{lay_f["disp_scale"]}" xChannelSelector="R" yChannelSelector="G"/>'
            f'</filter>'
            f'<filter id="tjmottle"><feTurbulence type="fractalNoise" baseFrequency="{m["bf"]}" numOctaves="{m["oct"]}" seed="{m["seed"]}" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="{m["matrix"]}"/></filter>'
            f'<filter id="tjgrainf"><feTurbulence type="fractalNoise" baseFrequency="{g["bf"]}" numOctaves="{g["oct"]}" seed="{g["seed"]}" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="{g["matrix"]}"/></filter>'
            f'<filter id="tjsheen"><feTurbulence type="fractalNoise" baseFrequency="{sh["bf"]}" numOctaves="{sh["oct"]}" seed="{sh["seed"]}" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="{sh["matrix"]}"/></filter>'
            f'<filter id="tjpapernoise"><feTurbulence type="fractalNoise" baseFrequency="{pn["bf"]}" numOctaves="{pn["oct"]}" seed="{pn["seed"]}" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="{pn["matrix"]}"/></filter>'
            # 撕裂毛刺（2026-09-25 五段定稿·修"整图模糊"）：位移滤镜会挪动**内容**像素 →
            # 弃 displacement；改为【内容零位移内核(erode 7 保清晰) + 边缘环带噪声毛刺】：
            # dilate(erode)-erode = 14px 环带，带内按 turbulence 二值噪声保留斑块 = 撕裂毛边，
            # 最后 composite in 用该 alpha 裁源图 —— 内部像素原样（不糊）、边缘参差（撕感）。
            f'<filter id="tjsplit" x="-4%" y="-4%" width="108%" height="108%">'
            f'<feMorphology in="SourceAlpha" operator="erode" radius="7" result="core"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.4" numOctaves="3" seed="31" result="t"/>'
            f'<feColorMatrix in="t" type="luminanceToAlpha" result="ta"/>'
            f'<feComponentTransfer in="ta" result="tb"><feFuncA type="discrete" tableValues="0 0 1 1 1"/>'
            f'</feComponentTransfer>'
            f'<feMorphology in="core" operator="dilate" radius="14" result="halo"/>'
            f'<feComposite in="halo" in2="core" operator="out" result="band"/>'
            f'<feComposite in="band" in2="tb" operator="in" result="spikes"/>'
            f'<feMerge result="mask2"><feMergeNode in="core"/><feMergeNode in="spikes"/></feMerge>'
            f'<feComposite in="SourceGraphic" in2="mask2" operator="in"/>'
            f'</filter>'
            f'</defs></svg>')

    # ---- 组装（DOM 层序=探针：底纹四层 → 顶部涂鸦 → 主标/副标 → 弧线/猫/短语右/虚点
    # → 撕纸 wrap → 气泡/喇叭 → 竖排轨道 → ×××/螺旋/T恤/徽章 → 底部四行）----
    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {defs}
  <svg style="position:absolute;inset:0;pointer-events:none" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{W}" height="{H}" filter="url(#tjmottle)" style="mix-blend-mode:multiply"/>
    <rect width="{W}" height="{H}" filter="url(#tjgrainf)" style="mix-blend-mode:multiply"/>
    <rect width="{W}" height="{H}" filter="url(#tjsheen)" style="mix-blend-mode:screen"/>
    <g stroke="{lay["grain_stroke"]}" stroke-width="{_sv(lay["grain_w"])}" opacity="{lay["grain_op"]}">{flecks}</g>
  </svg>
  {dd_top}
  {hero_html}
  {sub_html}
  {dd_arc_cat_dots}
  {torn}
  {dd_bubble}
  {dd_mega}
  {tracks}
  {dd_low}
  {foot}
</div>'''


def _tpl_exhibition_poster(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """展览海报（§1.4，探针真机 _shot_exhibition_poster.py 定稿）：纯白画布 + 左上角
    红方块迷你徽标 + 顶部居中主标（SourceSerifHeavy 思源宋 Heavy）+ 主标下英文副标 +
    居中装裱照片（object-fit:cover + img_focus 取景）+ 左右留白竖排大字（LXGWWenKai
    霞鹜文楷，作者/主创名）+ 竖排伴随小字英文身份 + 右侧朱砂红竖排展签 + 底部三栏
    信息条（标题摘要 / 日期时段 / 展馆地址，上细黑线）。现代美术馆气质，文字全落纸面。
    本款特殊：固定几何禁非等比缩放 → 忽略家族 fx/fy/fs，统一缩放因子
    s=min(W/900,H/1200)、原点偏移 ox/oy（§1.1，照 torn_journal 先例）。
    字段映射（§1.4 智能降级）：T→主标、S→英文副标、D→竖排日期+底栏中栏、L→底栏右栏
    展馆；左右竖排大字/展签/底栏装饰位 = layout['fixed'] 固定文案（纯装饰小字不走
    fg_texts 缺字预检，字体靠模板内 _serif_cn/_sans_cn 回退链兜底）。
    text_on_photo=False（护脸安全，文字全落纸面）。"""
    lay = cfg['layout']
    fx0 = lay['fixed']

    # ---- §1.1 本款统一缩放（忽略家族 fx/fy/fs）----
    s = min(W / 900, H / 1200)
    ox = (W - 900 * s) / 2
    oy = max(0, (H - 1200 * s) / 2)

    def _x(v):
        r = int(round(v * s)) + ox
        return int(r) if r == int(r) else round(r, 2)

    def _y(v):
        r = int(round(v * s)) + oy
        return int(r) if r == int(r) else round(r, 2)

    def _sv(v):
        return int(round(v * s))

    def _cx(v):          # 照片窗/底栏 from-x 相对基准，随 s + ox（左基准口径）
        r = int(round(v * s)) + ox
        return int(r) if r == int(r) else round(r, 2)

    # ---- 主标（T → hero；fit_title_fs 收敛宽 792=0.88×900 基准宽）----
    hero_html = ''
    if T:
        hero_px = _sv(cfg['scale']['hero_px'])
        hero_fs = fit_title_fs(T, _sv(792), hero_px, cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;top:{_y(lay["hero_top"])}px;left:0;width:100%;'
                     f'text-align:center;color:#111111;'
                     f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                     f'font-weight:900;font-size:{hero_fs}px;line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};z-index:5">{T}</div>')

    # ---- 主标下英文副标（S 参数化；若缺省用 fixed 兜底）----
    hero_sub = S if S else fx0.get('hero_sub', '')
    hero_sub_html = ''
    if hero_sub:
        hero_sub_html = (f'<div style="position:absolute;top:{_y(lay["hero_sub_top"])}px;left:0;'
                         f'width:100%;text-align:center;color:#666666;'
                         f'font-family:{_sans_cn};'
                         f'font-size:{_sv(lay["hero_sub_px"])}px;letter-spacing:{lay["hero_sub_letter"]};'
                         f'text-transform:uppercase;z-index:5">{hero_sub}</div>')

    # ---- 左上角徽标（fixed：badge_logo + badge_sub）----
    badge = (f'<div style="position:absolute;top:{_y(lay["badge_top"])}px;'
             f'left:{_x(lay["badge_left"])}px;z-index:6">'
             f'<div style="font-family:&quot;SourceSerifHeavy&quot;,{_sans_cn};font-weight:700;'
             f'font-size:{_sv(lay["badge_logo_px"])}px;letter-spacing:1px;color:#111111;'
             f'display:flex;align-items:center;gap:{_sv(8)}px">'
             f'<span style="display:inline-block;width:{_sv(lay["badge_dot"])}px;'
             f'height:{_sv(lay["badge_dot"])}px;background:{cfg["palette"]["accent"]}"></span>'
             f'{fx0["badge_logo"]}</div>'
             f'<div style="margin-top:{_sv(4)}px;font-family:{_sans_cn};'
             f'font-size:{_sv(10)}px;letter-spacing:1px;color:#666666">{fx0["badge_sub"]}</div>'
             f'</div>')

    # ---- 照片窗（fixed 几何；object-fit:cover + img_focus；零像素改动 P0-1）----
    img = (f'<div style="position:absolute;top:{_y(lay["img_y"])}px;left:{_cx(lay["img_x"])}px;'
           f'width:{_sv(lay["img_w"])}px;height:{_sv(lay["img_h"])}px;overflow:hidden;'
           f'background:#eeeeee;z-index:1">'
           f'<img src="{uri}" style="width:100%;height:100%;object-fit:cover;'
           f'object-position:{lay["img_focus"]}"></div>')

    # ---- 竖排翼（左右对称内容片段；由外层 absolute 容器定位）----
    def _vert_content(main_name, role, top_meta='', bot_meta=''):
        """竖排翼内容：顶部小字 / 竖排大字+伴随英文 / 底部小字。main_name/role 为纯文本。"""
        names = (f'<div style="display:flex;gap:{_sv(lay["v_gap"])}px;align-items:flex-start">'
                 f'<div style="writing-mode:vertical-rl;text-orientation:upright;'
                 f'font-family:&quot;LXGWWenKai&quot;,{_serif_cn};'
                 f'font-size:{_sv(lay["v_name_px"])}px;letter-spacing:{lay["v_name_letter"]};'
                 f'line-height:1;color:#111111">{main_name}</div>'
                 f'<div style="writing-mode:vertical-rl;font-family:{_sans_cn};'
                 f'font-size:{_sv(lay["v_role_px"])}px;letter-spacing:{lay["v_role_letter"]};'
                 f'color:#777777;transform:rotate(180deg);margin-top:{_sv(4)}px">{role}</div>'
                 f'</div>')
        top = (f'<div style="writing-mode:vertical-rl;font-family:{_sans_cn};'
               f'font-size:{_sv(lay["meta_px"])}px;letter-spacing:1px;color:#888888;'
               f'transform:rotate(180deg)">{top_meta}</div>') if top_meta else ''
        bot = (f'<div style="font-family:{_sans_cn};'
               f'font-size:{_sv(lay["meta_px"])}px;color:#999999;line-height:1.3;'
               f'text-align:center;width:{_sv(lay["wing_w"] - 10)}px">{bot_meta}</div>') if bot_meta else ''
        return f'{top}{names}{bot}'

    left_wing = (f'<div style="position:absolute;top:{_y(lay["wing_top"])}px;left:0;'
                 f'width:{_sv(lay["wing_w"])}px;height:{_sv(lay["wing_h"])}px;'
                 f'display:flex;flex-direction:column;justify-content:space-between;'
                 f'align-items:center;padding:{_sv(12)}px 0;z-index:3">'
                 f'{_vert_content(fx0["left_name"], fx0["left_role"], fx0["left_meta_top"], fx0["left_meta_bot"])}'
                 f'</div>')
    # 右侧翼：竖排大字 + 朱砂红展签 + 竖排日期（D 参数化，缺省 fixed）
    right_date = D if D else fx0.get('right_date', '')
    right_tag = (f'<div style="writing-mode:vertical-rl;text-orientation:upright;'
                 f'font-family:{_sans_cn};font-weight:700;'
                 f'font-size:{_sv(lay["tag_px"])}px;letter-spacing:1px;color:{cfg["palette"]["accent"]};'
                 f'border-left:{_sv(2)}px solid #dddddd;padding-left:{_sv(6)}px">'
                 f'{fx0["right_tag"]}</div>')
    right_date_html = (f'<div style="writing-mode:vertical-rl;font-family:&quot;SpaceMono&quot;,monospace;'
                       f'font-weight:700;font-size:{_sv(lay["date_rail_px"])}px;letter-spacing:1px;'
                       f'color:#222222;transform:rotate(180deg)">{right_date}</div>')
    right_wing = (f'<div style="position:absolute;top:{_y(lay["wing_top"])}px;right:0;'
                  f'width:{_sv(lay["wing_w"])}px;height:{_sv(lay["wing_h"])}px;'
                  f'display:flex;flex-direction:column;justify-content:space-between;'
                  f'align-items:center;padding:{_sv(12)}px 0;z-index:3">'
                  f'<div style="display:flex;gap:{_sv(lay["v_gap"])}px;align-items:flex-start">'
                  f'<div style="writing-mode:vertical-rl;text-orientation:upright;'
                  f'font-family:&quot;LXGWWenKai&quot;,{_serif_cn};'
                  f'font-size:{_sv(lay["v_name_px"])}px;letter-spacing:{lay["v_name_letter"]};'
                  f'line-height:1;color:#111111">{fx0["right_name"]}</div>'
                  f'<div style="writing-mode:vertical-rl;font-family:{_sans_cn};'
                  f'font-size:{_sv(lay["v_role_px"])}px;letter-spacing:{lay["v_role_letter"]};'
                  f'color:#777777;transform:rotate(180deg);margin-top:{_sv(4)}px">{fx0["right_role"]}</div>'
                  f'</div>{right_tag}{right_date_html}</div>')

    # ---- 底部三栏（上细黑线；左标题/描述、中日期/时段、右展馆/入场）----
    f_time = D if D else ''           # 底栏中栏日期与 D 同步
    f_venue = L if L else fx0.get('f_venue', '')
    foot = (f'<div style="position:absolute;bottom:{_y(lay["foot_bottom"])}px;'
            f'left:{_cx(lay["foot_x"])}px;width:{_sv(lay["foot_w"])}px;'
            f'border-top:{_sv(lay["foot_rule"])}px solid #111111;padding-top:{_sv(10)}px;'
            f'display:flex;justify-content:space-between;align-items:flex-end;color:#111111;z-index:4">'
            f'<div style="text-align:left">'
            f'<div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-weight:700;'
            f'font-size:{_sv(lay["f_title_px"])}px">{fx0["f_title"]}</div>'
            f'<div style="font-family:{_sans_cn};font-size:{_sv(lay["f_desc_px"])}px;'
            f'color:#666666">{fx0["f_desc"]}</div></div>'
            f'<div style="text-align:center">'
            f'<div style="font-family:&quot;SpaceMono&quot;,monospace;font-weight:700;'
            f'font-size:{_sv(lay["f_time_px"])}px">{f_time}</div>'
            f'<div style="font-family:{_sans_cn};font-size:{_sv(lay["f_hours_px"])}px;'
            f'color:#888888">{fx0["f_hours"]}</div></div>'
            f'<div style="text-align:right">'
            f'<div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-weight:700;'
            f'font-size:{_sv(lay["f_venue_px"])}px">{f_venue}</div>'
            f'<div style="font-family:{_sans_cn};font-size:{_sv(lay["f_adm_px"])}px;'
            f'color:#666666">{fx0["f_adm"]}</div></div>'
            f'</div>')

    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  {badge}
  {hero_html}
  {hero_sub_html}
  {img}
  {left_wing}
  {right_wing}
  {foot}
</div>'''


# ===============================================================
# 撕纸族几何（torn_peephole / torn_deckle 共用；2026-09-10）
# 移植自探针 G:/dsh/render_torn_paper_9.py（torn_poly / hole_path_out2 / tape / FIBER）
# ===============================================================
def _torn_ring(seed, x0, y0, x1, y1, n=30, fine=(6.0, 15.0), deep=(15.0, 28.0), deep_ratio=0.2):
    """矩形四周随机锯齿点列（像素坐标）。振幅恒为正 => 恒朝外张（咬外圈、不咬内圈）：
    约 (1-deep_ratio) 细毛边（fine 区间）+ deep_ratio 深咬口（deep 区间）。"""
    rnd = random.Random(seed)

    def _amp():
        return rnd.uniform(*fine) if rnd.random() > deep_ratio else rnd.uniform(*deep)

    pts = []
    for i in range(n + 1):                                   # top: L->R
        pts.append((x0 + (x1 - x0) * i / n, y0 - _amp()))
    for i in range(1, n + 1):                                # right: T->B
        pts.append((x1 + _amp(), y0 + (y1 - y0) * i / n))
    for i in range(1, n + 1):                                # bottom: R->L
        pts.append((x1 - (x1 - x0) * i / n, y1 + _amp()))
    for i in range(1, n):                                    # left: B->T
        pts.append((x0 - _amp(), y1 - (y1 - y0) * i / n))
    return pts


def _spike(pts, idx, x_tip, x_pin, dy):
    """把 idx 点拉成冲出尖锋（尖端 x_tip/dy，左右邻点回收到 x_pin）——V 形撕裂锋。"""
    x, y = pts[idx]
    pts[idx] = (x_tip, y + dy)
    for j in (idx - 1, idx + 1):
        pts[j] = (x_pin, pts[j][1])
    return pts


def _torn_poly(seed, n=30, jag=1.2, inset=0.0):
    """矩形四周随机锯齿多边形（% 坐标，CSS clip-path）。同种子不同振幅 => 同号锯齿严格内缩
    （白边底层大振幅 + 照片层小振幅 = 撕口白色纤维毛边）。"""
    rnd = random.Random(seed)
    pts = []
    span = 100 - 2 * inset
    for i in range(n + 1):                                   # top: L->R
        x = inset + span * i / n
        pts.append((x, max(0.0, inset + rnd.uniform(-jag, jag))))
    for i in range(1, n + 1):                                # right: T->B
        y = inset + span * i / n
        pts.append((min(100.0, 100 - inset + rnd.uniform(-jag, jag)), y))
    for i in range(1, n + 1):                                # bottom: R->L
        x = 100 - inset - span * i / n
        pts.append((x, min(100.0, 100 - inset + rnd.uniform(-jag, jag))))
    for i in range(1, n):                                    # left: B->T
        y = 100 - inset - span * i / n
        pts.append((max(0.0, inset + rnd.uniform(-jag, jag)), y))
    return 'polygon(' + ', '.join(f'{x:.2f}% {y:.2f}%' for x, y in pts) + ')'


def _strip_poly(seed, n=30, jag=1.8, inset=0.0):
    """横条撕纸多边形（% 坐标，CSS clip-path）：仅上下缘锯齿、左右直切（探针 strip_poly
    同口径——NO.08 左下牛皮纸条的撕口）。"""
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):                                   # top: L->R
        x = inset + (100 - 2 * inset) * i / n
        pts.append((x, inset + rnd.uniform(-jag, jag)))
    bot = []
    for i in range(n + 1):                                   # bottom: L->R（倒序拼回）
        x = inset + (100 - 2 * inset) * i / n
        bot.append((x, 100 - inset + rnd.uniform(-jag, jag)))
    pts += bot[::-1]
    return 'polygon(' + ', '.join(f'{x:.2f}% {y:.2f}%' for x, y in pts) + ')'


def _tape_div(w, h, x, y, rot=0, op=0.55):
    """半透明渐变胶带。"""
    return (f'<div style="position:absolute;width:{w}px;height:{h}px;left:{x}px;top:{y}px;'
            f'transform:rotate({rot}deg);'
            f'background:linear-gradient(180deg,rgba(255,252,232,{op}),'
            f'rgba(244,236,206,{max(0.1, op - 0.12)}));'
            f'box-shadow:0 2px 5px rgba(0,0,0,0.28);z-index:40"></div>')


def _fiber_css(h, v):
    """纸纤维底纹（横/竖两组极淡细线）。"""
    return (f'repeating-linear-gradient(0deg,transparent 0 3px,rgba(120,90,50,{h}) 3px 4px),'
            f'repeating-linear-gradient(90deg,transparent 0 4px,rgba(120,90,50,{v}) 4px 5px)')


def _photo_ratio_from_uri(uri):
    """照片原图宽高比（洞形自适应用）；读取失败回退 0.75（3:4）。"""
    try:
        from urllib.parse import urlparse, unquote
        from PIL import Image as _PILImage
        p = unquote(urlparse(uri).path)
        if len(p) > 2 and p[0] == '/' and p[2] == ':':
            p = p[1:]
        with _PILImage.open(p) as im:
            w, h = im.size
        return w / float(h)
    except Exception:
        return 0.75


def _tpl_torn_peephole(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """撕纸 · 破洞窥视（§1 终值，探针 render_torn_paper_9.py #04 移植到 900×1200 基准）：
    牛皮纸封面（纸纤维底纹 0.20/0.16）+ 零裁剪 contain 洞 + 撕边恒朝外（细毛边 6~15 /
    深咬口 15~28，咬封面不咬照片）+ 洞缘宽白纤维毛边（微模糊）+ 洞内暗影纵深 + 4 根不对称
    锋刺（横图冲出画布缘锐 V / 竖图·长条画布内钝 V）+ 对角双胶带 + 顶部主标/英文副标 +
    底部手写行/编号行。
    本款特殊：几何缩放 s = min(W/900, H/1200) + ox/oy（照 torn_journal 先例，固定几何禁
    非等比）；洞形按**原图比例**自适应。text_on_photo=False（文字全落牛皮纸封面，护脸安全）。
    **零裁剪口径（2026-09-10 用户拍板 A · 定案）**：承诺对象 = **洞内容器矩形**（rw×rh，
    即照片盒内矩形）——该矩形内照片 100% 可见、零裁剪零像素改动。**4 根锋刺是装饰性撕口
    几何，允许越出容器矩形**：横图（ratio>1，见下 spike_out_* 分支）尖端钉画布缘
    x = W+edge_out / -edge_out，裂缝越出照片盒的那一段渲染为**封面撕口延续的白纤维毛边**
    （同 stroke rgba(255,252,242,0.95) + 暗影内阴影 rgba(35,22,6,0.5)），是设计语言而非
    “露底”。实测 1200×900 横画布：洞内∧盒外 14754px = 洞面积 4.447%（左右各 2 根裂缝的
    盒外段，峰值亮度 RGB(255,251,241) 高于封面 RGB(153,122,78) = 亮纤维非暗底）；
    900×1200 竖画布同口径仅 114px = 0.027%。**复测勿用“洞多边形内照片 100% 可见”口径**
    ——那是另一口径，会误判为违约（本轮已发生一次并纠正）。"""
    lay = cfg['layout']
    s = min(W / 900, H / 1200)
    ox = (W - 900 * s) / 2
    oy = max(0, (H - 1200 * s) / 2)

    def _x(v):
        return int(round(v * s + ox))

    def _y(v):
        return int(round(v * s + oy))

    def _sv(v):
        return int(round(v * s))

    ratio = _photo_ratio_from_uri(uri)

    # ---- 洞几何（contain 自适应 → 零裁剪）----
    aw, ah = lay['hole_aw'], lay['hole_ah']
    rw = min(aw, int(ah * ratio))
    rh = min(ah, int(aw / ratio))
    cx, cy = lay['hole_cx'], lay['hole_cy']
    rx0, ry0 = cx - rw / 2.0, cy - rh / 2.0
    rx1, ry1 = rx0 + rw, ry0 + rh
    pad, ipad = lay['hole_pad'], lay['img_pad']
    hx0, hy0, hx1, hy1 = rx0 - pad, ry0 - pad, rx1 + pad, ry1 + pad
    ring = _torn_ring(44, hx0, hy0, hx1, hy1, n=lay['n'],
                      fine=(lay['fine_lo'], lay['fine_hi']),
                      deep=(lay['deep_lo'], lay['deep_hi']),
                      deep_ratio=lay['deep_ratio'])
    pts = [(round(px * s + ox, 1), round(py * s + oy, 1)) for px, py in ring]
    _n = lay['n']
    _R, _L = _n + 1, 3 * _n + 1
    if ratio > 1.0:                       # 横图：尖端冲到画布缘外（锐 V）
        eo = lay['edge_out']
        for k, inset, dy in lay['spike_out_r']:
            _spike(pts, _R + k, W + eo, round(hx1 * s + ox - inset * s, 1), dy * s)
        for k, inset, dy in lay['spike_out_l']:
            _spike(pts, _L + k, -eo, round(hx0 * s + ox + inset * s, 1), dy * s)
    else:                                 # 竖图/长条：尖端留在画布内（钝 V）
        for k, out, inset, dy in lay['spike_in_r']:
            _spike(pts, _R + k, round(hx1 * s + ox + out * s, 1),
                   round(hx1 * s + ox - inset * s, 1), dy * s)
        for k, out, inset, dy in lay['spike_in_l']:
            _spike(pts, _L + k, round(hx0 * s + ox - out * s, 1),
                   round(hx0 * s + ox + inset * s, 1), dy * s)
    hole_d = 'M ' + ' L '.join(f'{px:g},{py:g}' for px, py in pts) + ' Z'

    fiber = _fiber_css(lay['fiber_h'], lay['fiber_v'])
    img_html = (f'<img src="{uri}" style="position:absolute;'
                f'left:{_x(rx0 - ipad)}px;top:{_y(ry0 - ipad)}px;'
                f'width:{_sv(rw + 2 * ipad)}px;height:{_sv(rh + 2 * ipad)}px;'
                f'object-fit:cover;object-position:center">')

    # ---- 文字（T 主标 / S 英文副标 / L·D 编号行；缺省用 fixed 兜底）----
    hero_html = ''
    if T:
        hfs = fit_title_fs(T, _sv(792), _sv(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])
        hero_html = (f'<div style="position:absolute;top:{_y(lay["hero_top"])}px;left:0;width:100%;'
                     f'text-align:center;font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                     f'font-size:{hfs}px;line-height:{cfg["scale"]["hero_lh"]};'
                     f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                     f'color:{cfg["palette"]["point"]};'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]};z-index:20">{T}</div>')
    sub = S if S else lay['fixed']['sub']
    sub_html = (f'<div style="position:absolute;top:{_y(lay["sub_top"])}px;left:0;width:100%;'
                f'text-align:center;font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                f'font-size:{_sv(lay["sub_px"])}px;letter-spacing:{lay["sub_letter"]};'
                f'color:rgba(253,248,236,0.85);z-index:20">{sub}</div>')
    _parts = [p for p in (L, D) if p]
    micro = ' · '.join(_parts) if _parts else lay['fixed']['micro']
    foot_html = (f'<div style="position:absolute;bottom:{_y(lay["lead_bottom"])}px;left:0;'
                 f'width:100%;text-align:center;z-index:20">'
                 f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                 f'font-size:{_sv(cfg["scale"]["lead_px"])}px;letter-spacing:0.18em;'
                 f'color:{cfg["palette"]["point"]};'
                 f'text-shadow:{lay["lead_shadow"]}">{lay["fixed"]["lead"]}</div>'
                 f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                 f'font-size:{_sv(cfg["scale"]["micro_px"])}px;letter-spacing:0.32em;'
                 f'color:rgba(253,248,236,0.65);margin-top:{_sv(10)}px">{micro}</div></div>')

    t1x, t1y, t1r = lay['tape1']
    t2x, t2y, t2r = lay['tape2']
    tapes = (_tape_div(_sv(lay['tape_w']), _sv(lay['tape_h']), _x(t1x), _y(t1y), t1r)
             + _tape_div(_sv(lay['tape_w']), _sv(lay['tape_h']), _x(t2x), _y(t2y), t2r))

    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{fiber}"></div>
  <div style="position:absolute;inset:0;overflow:hidden">{img_html}</div>
  <svg viewBox="0 0 {W} {H}" style="position:absolute;inset:0;width:100%;height:100%;z-index:10">
    <defs>
      <linearGradient id="tpg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#bc9f72"/><stop offset="0.55" stop-color="#ab8c5e"/><stop offset="1" stop-color="#97794d"/>
      </linearGradient>
      <filter id="tpblur5" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{round(4.5 * s, 2)}"/></filter>
      <filter id="tpblur8" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{round(8 * s, 2)}"/></filter>
      <clipPath id="tphole"><path d="{hole_d}"/></clipPath>
    </defs>
    <path d="M 0,0 H {W} V {H} H 0 Z {hole_d}" fill-rule="evenodd" fill="url(#tpg)"/>
    <path d="M 0,0 H {W} V {H} H 0 Z {hole_d}" fill-rule="evenodd" fill="rgba(90,60,25,0.12)"/>
    <path d="{hole_d}" fill="none" stroke="rgba(255,250,235,0.9)" stroke-width="{round(18 * s, 1)}" filter="url(#tpblur5)"/>
    <path d="{hole_d}" fill="none" stroke="rgba(255,252,242,0.95)" stroke-width="{round(6 * s, 1)}" transform="translate({round(-2 * s, 1)},{round(-2 * s, 1)})"/>
    <g clip-path="url(#tphole)">
      <path d="{hole_d}" fill="none" stroke="rgba(35,22,6,0.5)" stroke-width="{round(26 * s, 1)}" filter="url(#tpblur8)"/>
    </g>
  </svg>
  {hero_html}
  {sub_html}
  {foot_html}
  {tapes}
</div>'''


def _tpl_torn_deckle(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """撕纸 · 双层撕纸（§1 终值，探针 render_torn_paper_9.py #08 移植到 900×1200 基准）：
    灰底（纸纤维底纹 0.20/0.16）+ 大毛边照片（白边底层 jag 2.5 + 照片层 jag 1.3，同种子
    同号锯齿严格内缩 = 撕口白色纤维毛边）+ 骑线标题纸片（约 1/4 压照片、3/4 落灰底；长标题
    word-break 自动换行 + overflow 兜底）+ 左下手记小纸片（+ 骑线 NO.08 圆戳）+ 左下牛皮纸
    条（上下缘撕口 _strip_poly 79/jag 8%；探针原值 1.2% 在盒高 51px 上仅 0.6px 亚像素、
    肉眼近直边，2026-09-10 用户拍板放大到 8% = 名义 ±4.1px；% 坐标以盒边为基准 → 外凸半幅
    画在盒外不呈现，实际可见为单向内凹锯齿 0~4.1px，最深仍远小于 strip_pad 14px 不压字）
    + 单胶带。照片原色（P0-1 零像素改动）。
    本款特殊：几何缩放 s = min(W/900, H/1200) + ox/oy（照 torn_journal 先例）。
    text_on_photo=False（纸片位置固定右下角、不涉人脸区；纸片骑线仅轻压照片底部 6.5%
    = 56/864px、占纸片高 1/4，拼贴语义同 torn_journal——用户 2026-09-10 拍板不作人工核脸款）。"""
    lay = cfg['layout']
    s = min(W / 900, H / 1200)
    ox = (W - 900 * s) / 2
    oy = max(0, (H - 1200 * s) / 2)

    def _x(v):
        return int(round(v * s + ox))

    def _y(v):
        return int(round(v * s + oy))

    def _sv(v):
        return int(round(v * s))

    fiber = _fiber_css(lay['fiber_h'], lay['fiber_v'])
    win_w = 900 - lay['win_left'] - lay['win_right']

    # ---- 大毛边照片（双层同号锯齿）----
    pb = _torn_poly(77, jag=lay['jag_back'])
    pp = _torn_poly(77, jag=lay['jag_photo'])
    photo = (f'<div style="position:absolute;top:{_y(lay["win_top"])}px;'
             f'left:{_x(lay["win_left"])}px;width:{_sv(win_w)}px;height:{_sv(lay["win_h"])}px;'
             f'filter:drop-shadow(0 {_sv(18)}px {_sv(42)}px rgba(30,28,24,0.5));z-index:10">'
             f'<div style="position:absolute;inset:0;background:#f6f3ea;clip-path:{pb}"></div>'
             f'<div style="position:absolute;inset:0;clip-path:{pp};overflow:hidden">'
             f'<img src="{uri}" style="position:absolute;inset:0;width:100%;height:100%;'
             f'object-fit:cover;object-position:{lay["photo_focus"]}"></div></div>')

    # ---- 骑线标题纸片（约 1/4 压照片；长标题 word-break 换行 + overflow 兜底）----
    qb = _torn_poly(78, jag=lay['plate_jag_back'])
    qp = _torn_poly(78, jag=lay['plate_jag_photo'])
    pad_y, pad_x = lay['plate_pad']
    en_txt = S if S else lay['fixed']['lead_en']
    meta_txt = D if D else lay['fixed']['micro']
    hero_block = ''
    if T:
        hfs = fit_title_fs(T, _sv(lay['plate_w'] - 2 * pad_x),
                           _sv(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])
        hero_block = (f'<div style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};'
                      f'font-size:{hfs}px;line-height:{cfg["scale"]["hero_lh"]};'
                      f'letter-spacing:{cfg["scale"]["hero_letter"]};'
                      f'color:{cfg["palette"]["point"]};word-break:break-word;'
                      f'max-width:100%">{T}</div>')
    plate = (f'<div style="position:absolute;right:{_x(lay["plate_right"])}px;'
             f'top:{_y(lay["plate_top"])}px;width:{_sv(lay["plate_w"])}px;'
             f'height:{_sv(lay["plate_h"])}px;'
             f'filter:drop-shadow(0 {_sv(14)}px {_sv(34)}px rgba(30,28,24,0.45));z-index:20">'
             f'<div style="position:absolute;inset:0;background:#f4efe0;clip-path:{qb}"></div>'
             f'<div style="position:absolute;inset:0;clip-path:{qp};background:#f4efe0;'
             f'display:flex;flex-direction:column;justify-content:center;align-items:center;'
             f'text-align:center;padding:{_sv(pad_y)}px {_sv(pad_x)}px;box-sizing:border-box;'
             f'overflow:hidden">'
             f'{hero_block}'
             f'<div style="font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-style:italic;'
             f'font-size:{_sv(cfg["scale"]["lead_px"])}px;color:#6a5a40;'
             f'margin-top:{_sv(lay["plate_gap"])}px">{en_txt}</div>'
             f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
             f'font-size:{_sv(cfg["scale"]["micro_px"])}px;color:#8a7a5a;letter-spacing:0.3em;'
             f'margin-top:{_sv(lay["plate_gap"])}px">{meta_txt}</div></div></div>')

    # ---- 左下手记小纸片 + 骑线圆戳 ----
    nb = _torn_poly(881, jag=lay['note_jag_back'])
    np_ = _torn_poly(881, jag=lay['note_jag_photo'])
    n_pad_y, n_pad_x = lay['note_pad']
    st = lay['stamp_size']
    note = (f'<div style="position:absolute;left:{_x(lay["note_left"])}px;'
            f'top:{_y(lay["note_top"])}px;width:{_sv(lay["note_w"])}px;'
            f'height:{_sv(lay["note_h"])}px;'
            f'filter:drop-shadow(0 {_sv(10)}px {_sv(26)}px rgba(30,28,24,0.35));'
            f'z-index:22;transform:rotate(-2.5deg)">'
            f'<div style="position:absolute;inset:0;background:#f7f4e8;clip-path:{nb}"></div>'
            f'<div style="position:absolute;inset:0;clip-path:{np_};background:#f7f4e8;'
            f'padding:{_sv(n_pad_y)}px {_sv(n_pad_x)}px;box-sizing:border-box">'
            f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
            f'font-size:{_sv(cfg["scale"]["lead_px"] + 4)}px;color:#3a3226;'
            f'letter-spacing:0.1em">{lay["fixed"]["note"]}</div>'
            f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
            f'font-size:{_sv(cfg["scale"]["micro_px"] + 1)}px;color:#8a7a5a;letter-spacing:0.28em;'
            f'margin-top:{_sv(lay["note_gap"])}px">{lay["fixed"]["note_meta"]}</div></div>'
            f'<div style="position:absolute;right:{_x(lay["stamp_right"])}px;'
            f'top:{_y(lay["stamp_top"])}px;width:{_sv(st)}px;height:{_sv(st)}px;'
            f'border:{_sv(2)}px solid #a5834f;border-radius:50%;display:flex;'
            f'align-items:center;justify-content:center;background:rgba(247,244,232,0.92);'
            f'transform:rotate({lay["stamp_rot"]}deg);'
            f'box-shadow:0 {_sv(6)}px {_sv(16)}px rgba(30,28,24,0.25)">'
            f'<span style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
            f'font-size:{_sv(cfg["scale"]["micro_px"] - 1)}px;color:#a5834f">'
            f'{lay["fixed"]["stamp"]}</span></div></div>')

    # ---- 左下牛皮纸条 + 胶带 ----
    s_pad_y, s_pad_x = lay['strip_pad']
    s_poly = _strip_poly(79, jag=lay['strip_jag'])       # 撕口 seed 照探针（strip_poly 79）；
                                                         # jag 8% 为拍板放大值；inset=0 → 外凸半幅在盒外不呈现
    strip = (f'<div style="position:absolute;left:{_x(lay["strip_left"])}px;'
             f'bottom:{_y(lay["strip_bottom"])}px;background:{cfg["palette"]["accent"]};'
             f'padding:{_sv(s_pad_y)}px {_sv(s_pad_x)}px;'
             f'transform:rotate({lay["strip_rot"]}deg);'
             f'clip-path:{s_poly};'
             f'box-shadow:0 {_sv(10)}px {_sv(24)}px rgba(30,28,24,0.4);z-index:25">'
             f'<span style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
             f'font-size:{_sv(cfg["scale"]["micro_px"] + 7)}px;color:#fdf8ec;'
             f'letter-spacing:0.14em">{lay["fixed"]["strip"]}</span></div>')
    t1x, t1y, t1r = lay['tape1']
    tape_html = _tape_div(_sv(lay['tape_w']), _sv(lay['tape_h']), _x(t1x), _y(t1y), t1r)

    return f'''<div class="stage" style="background:{cfg["palette"]["primary"]}">
  <div style="position:absolute;inset:0;background:{fiber}"></div>
  {photo}
  {plate}
  {note}
  {strip}
  {tape_html}
</div>'''


# ===============================================================
# template_id -> 构建函数映射
# ===============================================================

# 新款入库批 2026-09-16：模板拆分第一步（§1.4 表 D；design_templates_b = 本批落位的新款文件）。
# import 顺序约束（§2.7 唯一硬前提）：design_templates_b 从本模块导入 _serif_cn/_sans_cn，
# 须在其定义（:71-72）之后 import——此处已在模块底部，时序满足。
from design_templates_b import _tpl_modern_spread, _tpl_cultural_journal  # noqa: E402

_TPL = {
    '_tpl_pop_halftone': _tpl_pop_halftone,
    '_tpl_kinfolk_air': _tpl_kinfolk_air,
    '_tpl_museum_frame': _tpl_museum_frame,
    '_tpl_swiss_red_grid': _tpl_swiss_red_grid,
    '_tpl_super_index': _tpl_super_index,
    '_tpl_retro_tv': _tpl_retro_tv,
    '_tpl_street_zine': _tpl_street_zine,
    '_tpl_duo_pop': _tpl_duo_pop,
    '_tpl_doodle_summer': _tpl_doodle_summer,
    '_tpl_collage_man': _tpl_collage_man,
    '_tpl_branch_magazine': _tpl_branch_magazine,
    '_tpl_pop_lichtenstein': _tpl_pop_lichtenstein,
    '_tpl_pop_press': _tpl_pop_press,
    '_tpl_torn_journal': _tpl_torn_journal,
    '_tpl_exhibition_poster': _tpl_exhibition_poster,
    '_tpl_torn_peephole': _tpl_torn_peephole,
    '_tpl_torn_deckle': _tpl_torn_deckle,
    # 新款入库批 2026-09-16（+2；模板落 design_templates_b.py，§1.4 表 D/D-14）
    '_tpl_modern_spread': _tpl_modern_spread,
    '_tpl_cultural_journal': _tpl_cultural_journal,
}


# ---------------------------------------------------------------
# 主渲染
# ---------------------------------------------------------------
def _bright(bg_luma, key='top'):
    """取落点分区亮度（scalar 0~255）；无 bg_luma / 取不到返回 None。"""
    if isinstance(bg_luma, dict) and bg_luma.get(key) is not None:
        try:
            return float(bg_luma[key])
        except (TypeError, ValueError):
            return None
    if bg_luma is not None and not isinstance(bg_luma, dict):
        try:
            return float(bg_luma)
        except (TypeError, ValueError):
            return None
    return None


def render(photo_path, config, title, sub, date, location, meta_extra='', bg_luma=None,
           photo_focus_y=None, words=None, fg_fixed=None):
    """设计语言 19 款渲染入口。

    config 必须为 DESIGN_CONFIGS 的某一键对应的 dict（engine 传入 --genre）。
    内部按 config['template_id'] 分发到具体构建函数。
    画幅按源图比例自适应（_canvas_for），模板绝对像素按 fx/fy/fs 缩放（int(round(v*fs))）。
    meta_extra（可选）：镜头参数等补充注脚信息（super 目录 04 栏 / pop·tv 注脚位）。
    words（可选）：collage_man 词墙 ③层用户词（list，--words 注入；其余款忽略）。
    fg_fixed（可选）：固定装饰文案覆盖 dict（--fg-texts 注入；键 = layout.fixed 内键名，
    经下方 cfg 合并供模板自然读取，不进模板 kwargs；值经 HTML 转义恰好一次；None/空 →
    整段不走，输出字节零变化）。
    返回完整 HTML 字符串。
    """
    esc = _html.escape
    uri = _photo_uri(photo_path)
    T, S, D, L = esc(title), esc(sub), esc(date), esc(location)
    W, H, fs = _canvas_for(photo_path)
    fx = fy = fs   # 等比单因子（设计语言族几何统一乘 fs，设计稿 §1：int(round(v*fs))）
    # 非破坏性：不污染共享 DESIGN_CONFIGS，仅本渲染生效
    cfg = dict(config)
    # --fg-texts 固定装饰文案覆盖（b 方案）：cfg 是浅拷贝、fixed 是 layout 的嵌套 dict，
    # 直接改会污染共享 DESIGN_CONFIGS → 先拷 layout 再拷 fixed 后覆盖；不注入（None/空）
    # 整段不走，输出字节零变化。模板不加形参（tpl 位置调用零波及），自然读到覆盖值。
    # 注入值经 esc 转义恰好一次（与 T/S/D/L、--words 同口径——模板对 fixed 是裸插，
    # 含 < > & " 的注入词防结构破坏）；config 默认词是受信字面量、不转义，缺省路径零变化。
    if fg_fixed:
        cfg['layout'] = dict(cfg['layout'])
        _fixed = dict(cfg['layout'].get('fixed') or {})
        _fixed.update({k: esc(str(v)) for k, v in fg_fixed.items()})
        cfg['layout']['fixed'] = _fixed
    # 落点背景亮度：text_on_photo=False 款用 base_color 亮度（确定性，不依赖像素）；
    # True 款用 analyze_pixel 底部亮度（bg_luma），取不到回退 None（双影兜底）。
    if cfg.get('text_on_photo'):
        bg = _bright(bg_luma, 'bottom')
    else:
        bg = luma(cfg.get('base_color') or cfg['palette']['primary'])
    tpl = _TPL[cfg['template_id']]
    # WP-B · 照片取景焦点：y≠50 时 .ph 类规则追加 object-position（0=保顶裁脚）；
    # y=50/缺省 → focus_css 走 _BASE_CSS 默认值（含 ';object-position:center' 字面量）。
    _fy = 50 if photo_focus_y is None else int(photo_focus_y)
    focus_css = ';object-position:center' if _fy == 50 else (';object-position:center %d%%' % _fy)

    # ---- font_guard 缺字预检（§4-5；接入点 A，matting_engine 先例：先 fit 后包）----
    # 作用域：title_font ∈ 白名单（六款 = SourceHanSansHeavy；彩活楷体款 = ZhuoKaiKai）的款。
    # check_and_wrap 收**未转义原文**（其内部逐字 esc）；fit 按纯文本估宽，兜底 span 只在
    # 最终 HTML 上包裹。sub×emotion_font 不查不注（同 matting 现款口径）。
    # 彩活四款补充（设计稿 §2 font_guard 覆盖）：固定装饰文案的繁体字（subline_text/
    # mark_text/foot_text 等）**随所在款 title_font 一起被预检**——config.layout['fg_texts']
    # 逐款声明参与预检的装饰文案键；缺字时对应 layout 值替换为思源宋兜底 span（渲染保底）
    # 并记 font-fallback 注释（与主标同 token，质检器 [font-coverage] 解析）。
    _fg_comment = ''
    _fg_uncoverable = []
    _fg_fallback_used = False
    _fg_html = None
    if cfg['fonts']['hero'] in font_guard.FONT_GUARD_WHITELIST and title:
        _fg = font_guard.check_and_wrap(title, cfg['fonts']['hero'])
        _fg_fallback_used = _fg['fallback_used']
        _fg_comment = _fg['comment'] if _fg_fallback_used else ''
        _fg_uncoverable = _fg['uncoverable']
        _fg_html = _fg['html']
    # 装饰文案预检（同款同字体；layout 值替换须不污染共享 DESIGN_CONFIGS——render 开头
    # cfg=dict(config) 是浅拷贝，layout 仍共享，故此处对 layout 再做一层拷贝后改写）。
    # fg_texts 两种形态（§0.5 覆盖口径，2026-09-08 构图三款扩）：
    #   tuple/list（彩活四款旧形态）——随所在款 title_font 预检；
    #   dict {layout键: font_family}（构图三款新形态）——**按文案自身 font 逐字 cmap 预检**
    #   （装饰文案的字体≠title_font，如 branch 宋体文案/pop 对话框 LXGWWenKai）。
    # dict 值须在 font_guard.FONT_FILES（否则 font_covers_family 放行不查）。
    # dict 形态按文案自身 font 预检（§0.5：**不限 title_font 白名单**——pop 二款
    # hero=SourceSerifHeavy 不在白名单，但装饰文案仍须逐字查）；tuple 形态保持彩活
    # 先例门（hero ∈ 白名单才查——作用域=主标字体，非装饰文案自身）。
    _fgt = cfg['layout'].get('fg_texts')
    if _fgt and isinstance(_fgt, dict):
        cfg['layout'] = dict(cfg['layout'])
        for _k, _fam in _fgt.items():
            _txt = cfg['layout'].get(_k)
            if not _txt:
                continue
            _r = font_guard.check_and_wrap(_txt, _fam)
            if _r['fallback_used']:
                cfg['layout'][_k] = _r['html']
                _fg_comment = (_fg_comment + '|' + _r['comment']) if _fg_comment else _r['comment']
                _fg_fallback_used = True
            _fg_uncoverable = _fg_uncoverable + _r['uncoverable']
    elif cfg['fonts']['hero'] in font_guard.FONT_GUARD_WHITELIST and _fgt:
        cfg['layout'] = dict(cfg['layout'])
        for _k in _fgt:
            _txt = cfg['layout'].get(_k)
            if not _txt:
                continue
            _r = font_guard.check_and_wrap(_txt, cfg['fonts']['hero'])
            if _r['fallback_used']:
                cfg['layout'][_k] = _r['html']
                _fg_comment = (_fg_comment + '|' + _r['comment']) if _fg_comment else _r['comment']
                _fg_fallback_used = True
            _fg_uncoverable = _fg_uncoverable + _r['uncoverable']
    if _fg_uncoverable:
        # 兜底字体也缺字（升格 ✗）：独立注释块（font-fallback 块照常；质检器按 token 各自解析）
        _fg_note_unc = 'font-uncoverable: ' + ','.join(_fg_uncoverable)
    else:
        _fg_note_unc = ''

    # collage_man 词墙 ③层用户词经模板 kwarg 传入（其余款签名无 words 形参 → 走位置调用）
    # _t_eff：torn_journal 传兜底协同串（§1.4 ——主标逐字微旋转与兜底 span 不兼容，
    # 模板检测 '<span' in T_eff → 有则整串直排不逐字旋转；本款 body 无连续 `>{T}` 串，
    # 末尾 replace 对其自然 no-op。其余款 _t_eff=T 零行为变化）
    _t_eff = (_fg_html if _fg_html else T) if cfg['template_id'] == '_tpl_torn_journal' else T
    if cfg['template_id'] == '_tpl_collage_man':
        body = tpl(uri, cfg, _t_eff, S, D, L, W, H, fx, fy, fs, meta_extra, bg, words=words)
    else:
        body = tpl(uri, cfg, _t_eff, S, D, L, W, H, fx, fy, fs, meta_extra, bg)
    # 兜底包裹在 fit 之后（模板内 fit 用的 T 为纯文本）：直接替换最终 HTML 中首个 T 文本节点
    # ——模板把 T 原样放进度（无属性混排），此处安全替换（与 matting「先 fit 后包」语义一致）。
    # ⚠️ 隐性前提（勿破坏）：白名单款的模板中 T 必须是 body 里**第一个**出现的 T 文本节点
    # 且先于 D/L（若未来白名单扩到 D/L 前置的款〔如 museum info 条〕，title==date 时会错误
    # 包裹日期——届时须把包裹下沉到 tpl 签名内显式传递）。彩活四款核查：
    #   street_zine：T 在 body 中晚于 S/D（黑带内 S 先渲）→ 白名单楷体款 T 非首个文本节点——
    #   但 replace 目标 `>T<`（>T 后接 </div>）与日期块（>D< 同样结构）仅在 title==date 时
    #   撞名；P1 的 T 在 S/D 之后渲 → replace 首个 `>{T}` 命中 S 之后的首个 T 节点；
    #   D 为 mono 青块独立 span 结构 `>{D}</span>`，与 T 的 `>{T}</div>` 结构不同——
    #   仅当 title 与 date 字面相同且同结构才可能误包，验收 4 人工核兜底。
    #   duo_pop/doodle_summer/collage_man：T 均在 S/D 之后渲（同上结构核查，安全）。
    #   torn_journal（2026-09-09）：兜底串经 _t_eff 直接传模板（见上方 §1.4 注），
    #   本款不做 `>{T}` replace（body 无连续 `>{T}` 串）。
    if _fg_fallback_used and _fg_html is not None:
        # _fg_html 非 None 才替换（dict 形态装饰文案兜底时 title 未查、_fg_html=None，
        # 此时装饰文案的兜底 span 已在 cfg['layout'] 替换——不能把 '>T' 换成 '>None'）
        if cfg['template_id'] != '_tpl_torn_journal':
            body = body.replace(f'>{T}', f'>{_fg_html}', 1)
    # ---- @font-face 按需注入（§2：不匹配款字节零变化）----
    # hero/emotion/data 三位任一命中即注入（本批 10 款 data 均为 SpaceMono 基础常量；
    # 三位同查防后续款把新字体挂 data 位时漏注入——口径与文件头注释一致）。
    # street_zine 刊名红块 name_font（layout 键，=SourceHanSansHeavy）单独并入排查——
    # 设计稿 §1.1 契约"黑体 Heavy"要求该块真字重渲染。
    font_css = FONTS_CSS
    _used = (cfg['fonts']['hero'], cfg['fonts']['emotion'], cfg['fonts']['data'])
    # 新款入库批 2026-09-16（§2.7 ③ 唯一新增行）：config 声明式 extra_fonts（D-4）——
    # 现有 17 款无该键 ⇒ _used 逐元素不变 ⇒ 不匹配款字节零变化（§7 A8 机检）。
    _used = _used + tuple(cfg['layout'].get('extra_fonts', ()))
    if cfg['template_id'] == '_tpl_street_zine':
        _used = _used + (cfg['layout'].get('name_font', ''),)
    if 'SourceHanSansHeavy' in _used:
        font_css += '\n' + _SS_HEAVY_CSS
    if 'SourceHanSerifMedium' in _used:
        font_css += '\n' + _SS_SERIF_MED_CSS
    if 'CaveatBold' in _used:
        font_css += '\n' + _CAVEAT_CSS
    if 'ZhuoKaiKai' in _used:
        font_css += '\n' + _QSSS1_CSS
    if 'LXGWWenKai' in _used:
        font_css += '\n' + _LXGW_CSS
    if 'BebasNeue' in _used:
        font_css += '\n' + _BEBAS_CSS
    # ---- 新款入库批 2026-09-16：+5 条 family 注入分支（形制照上方先例，§2.7 ③）----
    if 'Prata' in _used:
        font_css += '\n' + _PRATA_CSS
    if 'SourceHanSansBold' in _used:
        font_css += '\n' + _SS_BOLD_CSS
    if 'SourceHanSansRegular' in _used:
        font_css += '\n' + _SS_REG_CSS
    if 'SourceHanSerifRegular' in _used:
        font_css += '\n' + _SS_SERIF_REG_CSS
    if 'LXGWWenKaiReg' in _used:
        font_css += '\n' + _LXGW_REG_CSS
    if _fg_fallback_used or _fg_uncoverable:
        font_css += '\n' + _FALLBACK_SONG_CSS
    _fg_note = f'<!-- {_fg_comment} -->' if _fg_comment else ''
    _fg_note += f'<!-- {_fg_note_unc} -->' if _fg_note_unc else ''
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css}\n'
            f'{_BASE_CSS(cfg["palette"]["primary"], W, H, focus_css)}</style></head><body>'
            f'{_fg_note}{body}</body></html>')
