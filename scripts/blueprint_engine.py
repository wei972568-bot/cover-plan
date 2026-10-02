#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝图 28 套补齐 · 文字压照片渲染器（blueprint canonical · 6 款异构模板）
=====================================================================
render(photo_path, config, title, sub, date, location, meta_extra='') -> html_str
（与 matting_engine 同签名：传 config 而非 template_id。）
meta_extra（可选）：镜头参数等补充注脚信息（如 '35MM F1.4'），经 _meta 拼在 date·location 之后。
按 config['template_id'] 分发到 6 个构建函数；mode='B' 仅为家族标记（非分发键）。
文字一律来自参数（不硬编码文案）；仅"物/结构"标签（日期戳/帧号等）由参数派生（确定性 seed）。

画幅：按源图比例自适应（复用 engine_v2 / metaphor 的比例检测，见 _canvas）：
  3:4→1080x1350 · 4:3→1350x1080 · 16:9→1350x759 · 9:16→759x1350 · 1:1→1080x1080
  比例检测失败（PIL 读不到）兜底 3:4。
  模板内绝对像素（横→fx、纵→fy、字/线/圆角→fs）按画布缩放；flex/% 保持相对。
色彩：照片加载**色彩原图**（默认不上黑白滤镜）；按 config['palette']['primary'] 上画布底色，
      config['tone_filter'] 指定时加在照片上。
字体：@font-face 加载 D:/dsh/fonts 下（路径同 matting_engine）：
  SourceSerifHeavy / LXGWWenKai / SpaceMono / CormorantItalic / PlayfairItalic /
  CinzelBold / BebasNeue（file:/// 绝对路径）。
照片：file:/// 绝对路径（chrome headless 可读）；object-fit:cover 源图自动裁切到画幅。

简化声明（设计 §5 拆两档）：
  - 完整气质 4 款：light_leak / draping / bedrock_stele / midnight（2026-09-05 -horizon）。
  - 简化气质 2 款：deep_interlock / silhouette（2026-09-05 -piercing）—— 首版大字版式 + 简化咬合/环绕
    （叠字/色带/阶梯块顺边缘），**不含真正的发丝 3D 咬合/顺轮廓抠像**（那是另案，需轮廓识别）。
"""
import hashlib
import os
import html as _html
from pathlib import Path

# ---- 共享排版守卫（收敛宽度自适应 / 落点亮度对比 / clip-safe）----
from type_guard import fit_title_fs, luma, readability

FONTS_DIR = 'D:/dsh/fonts'

# 画幅分桶（同 engine_v2 / metaphor_engine）：宽x高。
_SIZES = {'3:4': (1080, 1350), '4:3': (1350, 1080), '16:9': (1350, 759),
          '9:16': (759, 1350), '1:1': (1080, 1080)}

_serif_cn = "'Songti SC','Source Han Serif SC','SimSun','Noto Serif CJK SC',serif"
_sans_cn = "'PingFang SC','Source Han Sans SC','Noto Sans CJK SC','Microsoft YaHei',sans-serif"

# 7 款字体（@font-face，路径同 matting_engine；BebasNeue 为最佳推测路径，缺失则回退 sans）
FONTS_CSS = f'''
@font-face {{ font-family:"SourceSerifHeavy"; src:url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Heavy-4.otf"); }}
@font-face {{ font-family:"LXGWWenKai"; src:url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf"); }}
@font-face {{ font-family:"SpaceMono"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/SpaceMono-Bold.ttf"); }}
@font-face {{ font-family:"CormorantItalic"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/CormorantGaramond-Italic.ttf"); }}
@font-face {{ font-family:"PlayfairItalic"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/PlayfairDisplay-Italic.ttf"); }}
@font-face {{ font-family:"CinzelBold"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Cinzel-Bold.ttf"); }}
@font-face {{ font-family:"BebasNeue"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BebasNeue-Regular.ttf"); }}
'''


# ---------------------------------------------------------------
# 比例检测（复用 engine_v2 / metaphor_engine 的 _SIZES + 分桶 + fx/fy/fs）
# ---------------------------------------------------------------
def _canvas(photo_path):
    """按源图宽高比分桶画幅，返回 (W, H, fx, fy, fs)。"""
    try:
        from PIL import Image as _PI
        _pw, _ph = _PI.open(photo_path).size
        _r = _pw / _ph
        if _r >= 1.6:
            _RATIO = '16:9'
        elif _r >= 1.25:
            _RATIO = '4:3'
        elif _r > 0.9:
            _RATIO = '1:1'
        elif _r > 0.6:
            _RATIO = '3:4'
        else:
            _RATIO = '9:16'
    except Exception:
        _RATIO = '3:4'
    W, H = _SIZES[_RATIO]
    if W > H:
        fx, fy = W / 1350, H / 1080
    else:
        fx, fy = W / 1080, H / 1350
    fs = min(fx, fy)
    return W, H, fx, fy, fs


# ---------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------
def _photo_uri(photo_path):
    return Path(os.path.abspath(photo_path)).as_uri()


def _shadow(color, bg=None):
    """落点亮度感知对比守卫（readability 的 light 包装）：返回 text-shadow 值。"""
    return readability(color, bg)['shadow']


def _ct(color, bg=None):
    """文字对比保障（兼容旧签名）：浅字→暗影、深字→亮影；落点亮度感知。"""
    return _shadow(color, bg)


def _seed(*parts):
    _s = '|'.join(str(p) for p in parts if p)
    return int(hashlib.md5(_s.encode('utf-8')).hexdigest(), 16)


def _num(seed, lo, hi):
    """确定性整数区间（用于派生 LOT/版本/帧号/日期戳等）。"""
    return lo + (seed % (hi - lo + 1))


def _frame_roll(title, date, location):
    """派生胶片卷号/帧号（仅结构标签，非文案）。"""
    return f"36MM · FRAME {_num(_seed('roll', title, date, location), 1, 36):02d}"


def _img(uri, tf=''):
    return f'<img class="ph" src="{uri}" style="{tf}">'


def _meta(date, location, meta_extra=''):
    # date/location 已在 render 内 esc()；meta_extra 未转义，须在此补齐（与 matting_engine 一致）
    return ' · '.join(x for x in [date, location, _html.escape(meta_extra)] if x)


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


# ===============================================================
# 各模板构建函数（返回 body 片段 = 一个 .stage 容器）
# 签名统一：fn(uri, cfg, T, S, D, L, W, H, fx, fy, fs)
#   横量（宽/left/right/横向 padding/gap）→ fx；纵量（高/top/bottom/纵向 padding）→ fy；
#   字号/线宽/圆角/正圆形件 → fs；flex/% 保持相对。
#   局部 _x/_y/_s 为三轴缩放辅助，避免逐个手写 int(v*factor)。
#   所有文字（T/S/D/L）为已转义字符串，**不硬编码文案**。
# ===============================================================
def _tpl_light_leak(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """35mm 光斑漏光日杂：红橙漏光径向灌入 + 左侧竖排荧光主标 + 底部数码日期戳。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']
    acc = cfg['palette']['accent']            # 主标奶油色（可读）
    pt = cfg['palette']['point']              # 荧光橙（日期戳）
    leak_side = cfg['layout']['leak_side']
    strength = cfg['layout']['leak_strength']
    hero = cfg['fonts']['hero']
    if leak_side == 'top':
        pos = f'circle at 50% {_y(4)}%'
    elif leak_side == 'left':
        pos = f'circle at {_x(6)}% {_y(55)}%'
    else:
        pos = f'circle at {_x(94)}% {_y(48)}%'
    leak = (f'radial-gradient({pos}, rgba(255,60,20,{strength*0.9:.2f}) 0%, '
            f'rgba(255,110,30,{strength*0.55:.2f}) 30%, rgba(255,160,60,0) 66%)')
    shade = ('linear-gradient(180deg,rgba(10,4,2,.6) 0%,rgba(10,4,2,0) 38%,'
             'rgba(10,4,2,.28) 72%,rgba(10,4,2,.5) 100%)')
    ct = _ct(acc, bg)
    stamp = _frame_roll(T, D, L)              # 结构标签：胶片卷号（派生）
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;color:{acc};letter-spacing:.3em;'
                    f'opacity:.92;text-shadow:{cfg["scale"]["hero_shadow"]}">{S}</div>')
    meta_html = ''
    _m = _meta(D, L, meta_extra)
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{pt};letter-spacing:.28em;'
                     f'opacity:.9;text-shadow:{cfg["scale"]["hero_shadow"]};margin-top:{_y(14)}px">{_m}</div>')
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:{leak},{shade};z-index:5"></div>
  <div style="position:absolute;top:{_y(64)}px;left:{_x(70)}px;z-index:20;display:flex;flex-direction:column;gap:{_y(18)}px;align-items:flex-start">
    <div style="font-family:&quot;{hero}&quot;,{_sans_cn};font-weight:900;font-size:{fit_title_fs(T, int(W*0.78), _s(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])}px;line-height:{cfg['scale']['hero_lh']};letter-spacing:{cfg['scale']['hero_letter']};color:{acc};text-shadow:{cfg['scale']['hero_shadow']},{ct};text-transform:uppercase">{T}</div>
    {sub_html}
  </div>
  <div style="position:absolute;left:{_x(70)}px;bottom:{_y(52)}px;z-index:20;display:flex;flex-direction:column;gap:{_y(2)}px">
    <div style="font-family:&quot;{cfg['fonts']['data']}&quot;,monospace;font-size:{_s(cfg['scale']['micro_px']*1.6)}px;color:{pt};letter-spacing:.24em;text-shadow:0 0 8px rgba(255,92,26,.55),{cfg['scale']['hero_shadow']}">{stamp}</div>
    {meta_html}
  </div>
  <div style="position:absolute;right:{_x(44)}px;bottom:{_y(52)}px;z-index:20;display:flex;align-items:center;gap:{_x(10)}px">
    <div style="width:{_x(64)}px;height:1px;background:linear-gradient(90deg,transparent,{pt});opacity:.7"></div>
    <div style="font-family:&quot;{cfg['fonts']['data']}&quot;,monospace;font-size:{_s(cfg['scale']['micro_px'])}px;color:{pt};letter-spacing:.3em;opacity:.85">FRAME 12A</div>
    <div style="width:6px;height:6px;border:1px solid {pt};transform:rotate(45deg);opacity:.8"></div>
  </div>
</div>'''


def _tpl_deep_interlock(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """深度咬合（简化：CSS 叠字）——Cormorant 巨字压主体留白，前景大字母与背景字交错。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']
    acc = cfg['palette']['accent']            # 奶油
    pt = cfg['palette']['point']              # 金
    hero = cfg['fonts']['hero']
    giant_fs = _s(cfg['layout']['giant_fs'])
    giant_op = cfg['layout']['giant_opacity']
    # 背景叠字：横排大写巨字压入画面（简化咬合：前景字叠在背景巨字上）
    giant_chars = (T or 'INTERLOCK').upper()[:12]
    # 背景叠字为装饰性 watermark（低透明度，pointer-events:none，.stage overflow:hidden 裁掉越出部分），
    # 不作宽度自适应（保持"大字母压入画布边缘"的咬合意象）；前景 hero 大字才做 fit。
    giant = (f'<div style="position:absolute;top:{_y(120)}px;left:0;right:0;z-index:6;'
             f'text-align:center;font-family:&quot;{hero}&quot;,{_sans_cn};font-style:italic;'
             f'font-weight:700;font-size:{giant_fs}px;line-height:1;letter-spacing:.02em;'
             f'color:{acc};opacity:{giant_op};white-space:nowrap;pointer-events:none">{giant_chars}</div>')
    ct = _ct(acc, bg)
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;color:{acc};letter-spacing:.3em;'
                    f'opacity:.9;text-shadow:{cfg["scale"]["hero_shadow"]}">{S}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{pt};letter-spacing:.4em;'
                     f'text-shadow:{cfg["scale"]["hero_shadow"]}">{_m}</div>')
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.30) 55%,rgba(0,0,0,.78) 100%);z-index:4"></div>
  {giant}
  <div style="position:absolute;top:87.5%;right:{_x(78)}px;transform:translateY(-50%);z-index:20;display:flex;flex-direction:column;gap:{_y(18)}px;align-items:flex-end;text-align:right">
    <div style="font-family:&quot;{hero}&quot;,{_serif_cn};font-style:italic;font-weight:700;font-size:{fit_title_fs(T, int(W*0.55), _s(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])}px;line-height:{cfg['scale']['hero_lh']};letter-spacing:{cfg['scale']['hero_letter']};color:{acc};text-shadow:{cfg['scale']['hero_shadow']},{ct}">{T}</div>
    {sub_html}
  </div>
  <div style="position:absolute;left:0;right:0;bottom:{_y(40)}px;z-index:20;text-align:center">{meta_html}</div>
</div>'''


def _tpl_draping(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """悬垂流淌：书法大字从天顶垂落（竖排多列，底部渐隐）。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']
    acc = cfg['palette']['accent']            # 骨白
    pt = cfg['palette']['point']              # 朱砂
    hero = cfg['fonts']['hero']
    gap = cfg['layout']['col_gap']
    fade = cfg['layout']['fade_bottom']
    # 竖排从天顶垂落：title 一列 + sub 一列，顶部锚点，底部淡出
    ct = _ct(acc, bg)
    col = []
    # 主标列（单字逐列？——简化：整串竖排在天顶，从左至右多列）
    def _hang(text, font, size, color, ls, extra='', margin=0):
        return (f'<div style="writing-mode:vertical-rl;font-family:&quot;{font}&quot;,{_serif_cn};'
                f'font-weight:700;font-size:{fit_title_fs(text, int(H*0.78), _s(size), ls)}px;line-height:{cfg["scale"]["hero_lh"]};'
                f'letter-spacing:{ls};color:{color};text-shadow:{cfg["scale"]["hero_shadow"]},{ct};'
                f'margin-left:{_x(margin)}px;{extra}">{text}</div>')
    # 2026-09-14 用户微调：两列左右对调（副标列移到左侧、主标列移到右侧），整组靠右上。
    # 列序即 flex 顺序 → 先 append 副标(S)、后 append 主标(T)；列间距 margin 随主标列挂在 T 上。
    if S:
        col.append(_hang(S, cfg['fonts']['emotion'], cfg['scale']['lead_px'], acc, '0.22em',
                         extra='opacity:.9;'))
    col.append(_hang(T, hero, cfg['scale']['hero_px'], acc, cfg['scale']['hero_letter'],
                     margin=(gap if S else 0)))
    _m = _meta(D, L, meta_extra)
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,14,8,.72) 0%,rgba(20,14,8,.20) 40%,rgba(20,14,8,0) 62%,rgba(20,14,8,.34) 100%);z-index:4"></div>
  <div style="position:absolute;top:0;right:0;z-index:20;display:flex;justify-content:flex-end;align-items:flex-start;padding-top:{_y(52)}px;padding-right:{_x(56)}px;-webkit-mask-image:linear-gradient(180deg,#000 0%,#000 {int(fade*100)}%,rgba(0,0,0,0) 100%)">
    {''.join(col)}
  </div>
  <div style="position:absolute;left:0;right:0;bottom:{_y(44)}px;z-index:22;text-align:center">
    <div style="display:inline-block;font-family:&quot;{cfg['fonts']['data']}&quot;,monospace;font-size:{_s(cfg['scale']['micro_px'])}px;color:{pt};letter-spacing:.3em;background:rgba(20,14,8,.35);padding:{_y(6)}px {_x(14)}px;text-shadow:{cfg['scale']['hero_shadow']}">{_m}</div>
  </div>
</div>'''


def _tpl_silhouette(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """身形环绕（简化：阶梯标块顺边缘环抱）——右侧阶梯色块 + 竖排主标贴块。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']
    acc = cfg['palette']['accent']            # 金
    pt = cfg['palette']['point']              # 奶油
    hero = cfg['fonts']['hero']
    steps = cfg['layout']['step_count']
    step_h = _y(cfg['layout']['step_h'])
    step_gap = _y(cfg['layout']['step_gap'])
    # 阶梯块顺右缘排布：右缘贴齐、宽度逐级收窄 → 沿右缘向下形成"阶梯环抱"，不越出画布
    blocks = []
    for i in range(steps):
        blocks.append(
            f'<div style="position:absolute;right:0;top:{_y(112)+i*(step_h+step_gap)}px;'
            f'width:{_x(96)-i*_x(16)}px;height:{step_h}px;background:{acc};opacity:.85;'
            f'z-index:8;box-shadow:0 2px 10px rgba(0,0,0,.3)"></div>')
    ct = _ct(pt, bg)
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;color:{pt};letter-spacing:.3em;'
                    f'opacity:.92;text-shadow:{cfg["scale"]["hero_shadow"]}">{S}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{acc};letter-spacing:.34em;'
                     f'opacity:.85;margin-top:{_y(12)}px;text-shadow:{cfg["scale"]["hero_shadow"]}">{_m}</div>')
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.22) 60%,rgba(0,0,0,.62) 100%);z-index:4"></div>
  {''.join(blocks)}
  <div style="position:absolute;bottom:{_y(96)}px;right:{_x(96)}px;z-index:20;display:flex;flex-direction:column;gap:{_y(18)}px;align-items:flex-end;text-align:right">
    <div style="font-family:&quot;{hero}&quot;,{_serif_cn};font-weight:900;font-size:{fit_title_fs(T, int(W*0.5), _s(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])}px;line-height:{cfg['scale']['hero_lh']};letter-spacing:{cfg['scale']['hero_letter']};color:{pt};text-shadow:{cfg['scale']['hero_shadow']},{ct}">{T}</div>
    {sub_html}
  </div>
  <div style="position:absolute;right:{_x(96)}px;bottom:{_y(60)}px;z-index:20;text-align:right">{meta_html}</div>
</div>'''


def _tpl_bedrock_stele(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """泰山巨碑：底部 100-140px 特粗宋体如泰山托底（主标沉底居中）。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']
    acc = cfg['palette']['accent']            # 骨白
    pt = cfg['palette']['point']              # 朱砂
    hero = cfg['fonts']['hero']
    bottom_px = _y(cfg['layout']['stele_bottom_px'])
    ct = _ct(acc, bg)
    # 泰山托底：大字按宽度预算收缩（fit_title_fs），保证一行放下不溢出
    _fit = fit_title_fs(T, int(W * 0.92), _s(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;color:{acc};letter-spacing:.4em;'
                    f'opacity:.95;text-shadow:{cfg["scale"]["hero_shadow"]}">{S}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{pt};letter-spacing:.34em;'
                     f'opacity:.85;text-shadow:{cfg["scale"]["hero_shadow"]}">{_m}</div>')
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:linear-gradient(0deg,rgba(10,7,4,.88) 0%,rgba(10,7,4,.42) 26%,rgba(10,7,4,0) 46%);z-index:5"></div>
  <div style="position:absolute;left:0;right:0;bottom:{bottom_px}px;z-index:20;display:flex;flex-direction:column;align-items:center;text-align:center;gap:{_y(10)}px;padding:0 {_x(30)}px">
    <div style="font-family:&quot;{hero}&quot;,{_serif_cn};font-weight:900;font-size:{_fit}px;line-height:1;letter-spacing:{cfg['scale']['hero_letter']};color:{acc};text-shadow:{cfg['scale']['hero_shadow']},{ct};white-space:nowrap">{T}</div>
    {sub_html}
  </div>
  <div style="position:absolute;left:0;right:0;bottom:{_y(30)}px;z-index:20;text-align:center">{meta_html}</div>
</div>'''


def _tpl_midnight(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """暗夜黑胶：暗蓝压暗 + 暗金大字刊头（深邃唱片）。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    ink = cfg['palette']['primary']           # 暗蓝
    acc = cfg['palette']['accent']            # 暗金
    pt = cfg['palette']['point']              # 白
    hero = cfg['fonts']['hero']
    top_px = _y(cfg['layout']['headline_top_px'])
    dark = cfg['layout']['dark_overlay']
    ct = _ct(acc, bg)
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
                    f'font-size:{_s(cfg["scale"]["lead_px"])}px;color:{pt};letter-spacing:.3em;'
                    f'opacity:.9;text-shadow:{cfg["scale"]["hero_shadow"]}">{S}</div>')
    _m = _meta(D, L, meta_extra)
    meta_html = ''
    if _m:
        meta_html = (f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,monospace;'
                     f'font-size:{_s(cfg["scale"]["micro_px"])}px;color:{pt};letter-spacing:.4em;'
                     f'opacity:.7;margin-top:{_y(12)}px;text-shadow:{cfg["scale"]["hero_shadow"]}">{_m}</div>')
    return f'''<div class="stage" style="background:{ink};padding:0">
  <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,48,{dark}) 0%,rgba(10,20,48,{dark*0.6:.2f}) 42%,rgba(10,20,48,0) 68%,rgba(10,20,48,.5) 100%);z-index:4"></div>
  <div style="position:absolute;top:{top_px}px;left:0;right:0;z-index:20;text-align:center">
    <div style="display:inline-block;font-family:&quot;{hero}&quot;,{_serif_cn};font-weight:900;font-size:{fit_title_fs(T, int(W*0.9), _s(cfg['scale']['hero_px']), cfg['scale']['hero_letter'])}px;line-height:{cfg['scale']['hero_lh']};letter-spacing:{cfg['scale']['hero_letter']};color:{acc};text-shadow:{cfg['scale']['hero_shadow']},{ct}">{T}</div>
    <div style="margin-top:{_y(14)}px">{sub_html}</div>
  </div>
  <div style="position:absolute;left:0;right:0;bottom:{_y(42)}px;z-index:20;text-align:center">{meta_html}</div>
</div>'''


# ===============================================================
# template_id -> 构建函数映射
# ===============================================================
_TPL = {
    '_tpl_light_leak': _tpl_light_leak,
    '_tpl_deep_interlock': _tpl_deep_interlock,
    '_tpl_draping': _tpl_draping,
    '_tpl_silhouette': _tpl_silhouette,
    '_tpl_bedrock_stele': _tpl_bedrock_stele,
    '_tpl_midnight': _tpl_midnight,
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


def render(photo_path, config, title, sub, date, location, meta_extra='', bg_luma=None, photo_focus_y=None):
    """蓝图补齐 6 款渲染入口。

    config 必须为 BLUEPRINT_CONFIGS 的某一键对应的 dict（engine 传入 --genre）。
    内部按 config['template_id'] 分发到具体构建函数。
    画幅按源图比例自适应（_canvas），模板绝对像素按 fx/fy/fs 缩放。
    meta_extra（可选）：镜头参数等补充注脚信息，经 _meta 拼在 date·location 之后（如底部日期戳）。
    返回完整 HTML 字符串。
    """
    esc = _html.escape
    uri = _photo_uri(photo_path)
    T, S, D, L = esc(title), esc(sub), esc(date), esc(location)
    W, H, fx, fy, fs = _canvas(photo_path)
    # 非破坏性：不污染共享 BLUEPRINT_CONFIGS，仅本渲染生效
    cfg = dict(config)
    # 落点背景亮度：本 6 款文字均压照片 → 用 analyze_pixel 顶/底亮度；取不到回退 None（双影兜底）。
    # 中部/顶部取 top，底部（bedrock_stele）取 bottom。
    hero = cfg.get('hero_zone') or ''
    if hero == 'bottom_center':
        bg = _bright(bg_luma, 'bottom')
    elif isinstance(bg_luma, dict) and bg_luma.get('top') is not None and bg_luma.get('bottom') is not None:
        bg = (float(bg_luma['top']) + float(bg_luma['bottom'])) / 2
    else:
        bg = _bright(bg_luma, 'top')
    tpl = _TPL[cfg['template_id']]
    # WP-B · 照片取景焦点：y≠50 时 .ph 类规则追加 object-position（0=保顶裁脚）；
    # y=50/缺省 → focus_css 走 _BASE_CSS 默认值（含 ';object-position:center' 字面量），输出与历史字节一致。
    _fy = 50 if photo_focus_y is None else int(photo_focus_y)
    focus_css = ';object-position:center' if _fy == 50 else (';object-position:center %d%%' % _fy)
    body = tpl(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra, bg)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS_CSS}\n{_BASE_CSS(cfg["palette"]["primary"], W, H, focus_css)}</style></head><body>{body}</body></html>'
