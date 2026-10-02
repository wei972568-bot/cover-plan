#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
载体隐喻流派族 · 参数化渲染器（物格思维 · 7 款异构模板）
===========================================================
render(photo_path, genre_id, title, sub, date, location, photo_ratio=None, meta_extra='') -> html_str
按 genre_id 的 METAPHOR_CONFIGS['template_id'] 分发到 7 个构建函数。
meta_extra（可选）：镜头参数等补充注脚信息（如 '35MM F1.4'），经 _meta 拼在 date·location 之后。
  仅"有注脚位"的款（auction/dossier/score/arch）接收并渲染；playbill/lunar/viewfinder 的
  date/location 语义是折目/诗词内容（非注脚），故不收 meta_extra（版式语义，见设计 §2.2）。
mode='M' 仅为家族标记（非分发键）。文字一律来自参数（不硬编码文案）。
photo_ratio（可选，仅 music_manuscript 生效）：照片占比因子，默认 1.0 = v2 基准（谱线
78/56、标题 32、照片≈65%）；谱线按 1/photo_ratio 缩放——photo_ratio<1 谱线更高照片更小，
>1 谱线更矮照片更大。

画布：按源图比例自适应（复用 engine_v2 比例检测，见 _canvas）：
  3:4→1080x1350 · 4:3→1350x1080 · 16:9→1350x759 · 9:16→759x1350 · 1:1→1080x1080
  比例检测失败（PIL 读不到）兜底 3:4。
  模板内绝对像素（横→fx、纵→fy、字/线/圆角→fs）按画布缩放；flex/% 保持相对。
比例：模板用相对定位（%）/ flex，适配常规画幅；不再硬编码 1280×2056 / 900×1200。
色彩：照片加载色彩原图（默认不上黑白滤镜）；按 config['base_color'] 上"物"的基调色；
      config['tone_filter'] 指定时加在照片上（如 arch 暖调）。
字体：@font-face 加载 D:/dsh/fonts 下（同 matting_engine）：
  SourceSerifHeavy / LXGWWenKai / SpaceMono / CormorantItalic / PlayfairItalic /
  CinzelBold / BebasNeue（file:/// 绝对路径）。
照片：file:/// 绝对路径（chrome headless 可读）；object-fit:cover 源图自动裁切到画幅。
"""
import hashlib
import os
import re
import html as _html
from pathlib import Path

from metaphor_configs import METAPHOR_CONFIGS
# ---- 共享排版守卫（收敛宽度自适应 / 落点亮度对比 / clip-safe）----
from type_guard import fit_title_fs, luma, readability

FONTS_DIR = 'D:/dsh/fonts'

# 画幅分桶（同 engine_v2）：宽x高。
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
# 比例检测（复用 engine_v2 的 _SIZES + 分桶 + fx/fy/fs）
# ---------------------------------------------------------------
def _canvas(photo_path):
    """按源图宽高比分桶画幅，返回 (W, H, fx, fy, fs)。

    fx/fy 为横/纵向绝对像素的缩放参考（横向 px ×fx、纵向 px ×fy）；
    fs 为字号/线宽/圆角等"形状量"的缩放（= min(fx, fy)）。
    分桶失败（PIL 读不到）兜底 3:4。同 engine_v2.render_html 的比例检测。
    """
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
    """落点亮度感知对比守卫（readability 的 light 包装）：返回 text-shadow 值。

    各模板主标/注脚统一经此注入 readability（过去 `_ct` 定义了但从没被模板调用、
    全靠硬编码 text-shadow；现改为统一走落点亮度感知，见 docs/引擎排版健壮性-设计.md）。
    """
    return readability(color, bg)['shadow']


def _seed(*parts):
    _s = '|'.join(str(p) for p in parts if p)
    return int(hashlib.md5(_s.encode('utf-8')).hexdigest(), 16)


def _num(seed, lo, hi):
    """确定性整数区间（用于派生 LOT/版本/帧号等）。"""
    return lo + (seed % (hi - lo + 1))


def _lot_num(title, date, location):
    return _num(_seed('lot', title, date, location), 1, 99)


def _edition(title, date, location):
    return f"{_num(_seed('ed', title, date, location), 1, 50)}/50"


def _copy_no(title, date, location):
    return f"{_num(_seed('copy', title, date, location), 1, 20)}/20"


def _file_no(title, date, location):
    return f"NG-2026-{_num(_seed('file', title, date, location), 10000, 99999)}"


def _frame_no(title, date, location):
    return f"FRAME {_num(_seed('frame', title, date, location), 1, 99)}"


def _year_roman_or_arabic(date):
    """取 date 里 4 位年份；无则返回 None。"""
    m = re.search(r'\b(?:19|20)\d{2}\b', str(date or ''))
    return m.group(0) if m else None


def _month_en(date):
    """从 date 提取英文月份名（供月相历/图录用）；无则 ''。

    只按"可信模式"提取，避免把 '2026.09.01' 的日期 '01' 误判为一月：
      ① 显式英文月份名（JAN…DEC）；
      ② 年-月-日（YYYY[./-]M[./-]D，次要分隔符）取第 2 段为月；
      ③ 兜底：任一带分隔符的 1-12 段（best-effort，可能命中日，仅为装饰标）。
    """
    _m = ('JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
          'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER')
    d = str(date or '')
    up = d.upper()
    for name in _m:                                   # ① 英文名
        if name in up or name[:3] in up:
            return name
    m = re.search(r'(?:19|20)\d{2}[.\-/](\d{1,2})[.\-/]\d{1,2}', d)   # ② 年-月-日
    if m and 1 <= int(m.group(1)) <= 12:
        return _m[int(m.group(1)) - 1]
    m2 = re.search(r'[.\-/](\d{1,2})[.\-/]', d)        # ③ 兜底
    if m2 and 1 <= int(m2.group(1)) <= 12:
        return _m[int(m2.group(1)) - 1]
    return ''


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
# ===============================================================
def _tpl_auction(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """拍卖图录：顶部 EVENING SALE + LOT 号；照片窗；底部《title》+ sub；右侧传承/规格。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    bc = cfg['base_color']                  # 米白/暖白基调
    card = '#faf7ef'
    ink = '#1a1a1a'
    gold = '#8a6838'
    lot = _lot_num(T, D, L)
    ed = _edition(T, D, L)
    est = _num(_seed('est', T, D, L), 4, 60) * 1000
    est_hi = est + _num(_seed('esth', T, D, L), 4, 9) * 1000
    year = _year_roman_or_arabic(D) or 'MMXXVI'
    return f'''<div class="stage" style="background:{bc};padding:{_y(30)}px {_x(36)}px">
  <div style="position:relative;width:100%;height:100%;background:{card};overflow:hidden;padding:{_y(28)}px {_x(32)}px;display:flex;flex-direction:column;box-shadow:0 12px 40px rgba(0,0,0,.28)">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:{_s(2)}px solid {ink};padding-bottom:{_y(12)}px">
      <div>
        <div style="font-family:&quot;BebasNeue&quot;,{_sans_cn};font-size:{_s(30)}px;letter-spacing:.25em;color:{ink}">EVENING SALE</div>
        <div style="font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(14)}px;color:#666;margin-top:{_y(2)}px">{S or '影像專場'}</div>
      </div>
      <div style="text-align:right">
        <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(52)}px;color:{ink};letter-spacing:.06em;line-height:1">LOT {lot:03d}</div>
        <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:{gold};letter-spacing:.22em;margin-top:{_y(4)}px">EST. ¥{est:,} — {est_hi:,}</div>
      </div>
    </div>
    <div style="position:relative;width:100%;flex:1;overflow:hidden;margin:{_y(16)}px 0;border:{_s(1)}px solid {ink}">{_img(uri, cfg['tone_filter'])}</div>
    <div style="display:flex;gap:{_x(24)}px;align-items:center">
      <div style="flex:1.25">
        <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(T, int(W*0.45), _s(30), '0.12em')}px;color:#111;letter-spacing:.12em;text-shadow:{_shadow('#111', bg)}">《{T}》</div>
        <div style="font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-size:{_s(18)}px;color:#555;font-style:italic;margin-top:{_y(2)}px">{S}</div>
        <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(11)}px;color:#777;margin-top:{_y(8)}px;line-height:1.8">Gelatin silver print · 3:4<br>Signed and dated {year} · Edition {ed}<br>{_meta(D, L, meta_extra)}</div>
      </div>
      <div style="flex:1;border-left:{_s(1)}px solid rgba(0,0,0,.18);padding-left:{_x(20)}px">
        <div style="font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(13.5)}px;color:#333;line-height:2.0">來源：{L or '藝術家工作室'} · {year}<br>展览：{S or T} · 影像專場<br>此作為「{T}」系列核心影像，銀鹽工藝手工放大。</div>
      </div>
    </div>
  </div>
</div>'''


def _tpl_playbill(uri, cfg, T, S, D, L, W, H, fx, fy, fs, bg=None):
    """剧场节目单：左侧金竖排 title；照片窗；折子戏场目(第一折…/第二折…)+ACT/FINALE；底部年份。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    red = cfg['base_color']                 # 赭红
    outer = '#150a05'
    gold_mut = 'rgba(217,184,120,.6)'
    ink_f = '#f0d9a8'
    # 折目：第一折=title，第二折=sub（跳空则 location），大軸=date（跳空则默认）
    z1 = T or '第一折'
    z2 = S or (L or '第二折')
    z3 = (D or '大軸')
    act = ('ACT I', 'ACT II', 'FINALE')
    year = _year_roman_or_arabic(D) or 'MMXXVI'
    return f'''<div class="stage" style="background:{outer};padding:{_y(26)}px {_x(26)}px">
  <div style="position:relative;width:100%;height:100%;background:{red};box-shadow:0 24px 70px rgba(0,0,0,.8);overflow:hidden;border:{_s(3)}px solid rgba(217,184,120,.72);display:flex">
    <div style="width:{_x(126)}px;height:100%;border-right:{_s(1.5)}px solid {gold_mut};display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:{_y(26)}px 0;flex-shrink:0">
      <div style="writing-mode:vertical-rl;font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(T, int(H*0.72), _s(46), '0.3em')}px;color:{ink_f};letter-spacing:.3em;text-shadow:{_shadow(ink_f, bg)}">{T}</div>
      <div style="writing-mode:vertical-rl;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(13)}px;color:rgba(240,217,168,.72);letter-spacing:.3em">{S or '秋夜開鑼'}</div>
    </div>
    <div style="flex:1;display:flex;flex-direction:column;padding:{_y(26)}px {_x(30)}px">
      <div style="position:relative;width:100%;flex:1.3;overflow:hidden;border:{_s(1.5)}px solid {gold_mut}">{_img(uri, cfg['tone_filter'])}</div>
      <div style="margin-top:{_y(18)}px;display:flex;flex-direction:column;gap:{_y(11)}px">
        <div style="display:flex;align-items:center;gap:{_x(12)}px"><span style="font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(15)}px;color:{ink_f};letter-spacing:.1em">第一折 · <span style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(22)}px;letter-spacing:.12em">{z1}</span></span><span style="flex:1;height:1px;background:{gold_mut}"></span><span style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:rgba(240,217,168,.68)">{act[0]}</span></div>
        <div style="display:flex;align-items:center;gap:{_x(12)}px"><span style="font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(15)}px;color:{ink_f};letter-spacing:.1em">第二折 · <span style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(22)}px;letter-spacing:.12em">{z2}</span></span><span style="flex:1;height:1px;background:{gold_mut}"></span><span style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:rgba(240,217,168,.68)">{act[1]}</span></div>
        <div style="display:flex;align-items:center;gap:{_x(12)}px"><span style="font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(15)}px;color:{ink_f};letter-spacing:.1em">大軸 · <span style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(22)}px;letter-spacing:.12em">{z3}</span></span><span style="flex:1;height:1px;background:{gold_mut}"></span><span style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:rgba(240,217,168,.68)">{act[2]}</span></div>
      </div>
      <div style="margin-top:auto;font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:rgba(240,217,168,.55);letter-spacing:.26em">EVENING PROGRAMME · {year}</div>
    </div>
  </div>
</div>'''


def _tpl_dossier(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """解密档案卷宗：顶部档案头+红章「解密」+SUBJECT/CLEARANCE/COPY；照片窗；底部案卷注记+涂黑条。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    kraft = cfg['base_color']               # 牛皮纸
    outer = '#2a2620'
    ink = '#1a1a1a'
    sec = '#5a4a30'
    stamp = '#c43d2f'
    fno = _file_no(T, D, L)
    copy = _copy_no(T, D, L)
    year = _year_roman_or_arabic(D) or '2026'
    prov = _meta(D, L, meta_extra)
    return f'''<div class="stage" style="background:{outer};padding:{_y(26)}px {_x(26)}px">
  <div style="position:relative;width:100%;height:100%;background:{kraft};box-shadow:0 24px 60px rgba(0,0,0,.55);overflow:hidden;padding:{_y(32)}px {_x(36)}px;display:flex;flex-direction:column">
    <div style="position:absolute;top:{_y(-8)}px;right:{_x(118)}px;width:{_x(34)}px;height:{_y(106)}px;border:{_s(4)}px solid #7a7468;border-radius:{_s(18)}px;transform:rotate(6deg);z-index:40"></div>
    <div style="border-bottom:{_s(2)}px solid {ink};padding-bottom:{_y(12)}px;display:flex;justify-content:space-between;align-items:flex-end">
      <div>
        <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(f'VERMILION FILE · {T}', int(W*0.55), _s(34), '0.2em')}px;color:{ink};letter-spacing:.2em;text-shadow:{_shadow(ink, bg)}">VERMILION FILE · {T}</div>
        <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(11)}px;color:{sec};letter-spacing:.22em;margin-top:{_y(4)}px">FILE NO. {fno} · <span style="color:#c43d2f;font-weight:bold">DECLASSIFIED</span></div>
      </div>
      <div style="width:{_x(118)}px;height:{_y(62)}px;border:{_s(3)}px solid rgba(196,61,47,.85);border-radius:{_s(6)}px;display:flex;align-items:center;justify-content:center;transform:rotate(-8deg);color:{stamp};font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(23)}px;letter-spacing:.25em;opacity:.85">解密</div>
    </div>
    <div style="margin:{_y(16)}px 0 {_y(18)}px 0;font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(12)}px;color:#3a2f1e;letter-spacing:.15em">
      SUBJECT: <span style="background:#1a1a1a;color:#1a1a1a;padding:0 {_x(10)}px">██████████</span> · CLEARANCE: <span style="background:#1a1a1a;color:#1a1a1a;padding:0 {_x(10)}px">█████</span> · COPIES: {copy}
    </div>
    <div style="position:relative;width:100%;flex:1;overflow:hidden;border:{_s(1)}px solid rgba(60,45,20,.5);box-shadow:0 10px 26px rgba(0,0,0,.3);transform:rotate(-.5deg)">{_img(uri, cfg['tone_filter'])}</div>
    <div style="display:flex;gap:{_x(22)}px;margin-top:{_y(16)}px;align-items:center">
      <div style="flex:1;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(14.5)}px;color:#2c2314;line-height:2.0">記錄：例行巡查 {L or '至第三街區'}，狀況如常。{prov}<span style="background:#1a1a1a;color:#1a1a1a;padding:0 {_x(8)}px">████████</span> 並無異常。建議列為常規卷宗歸檔。</div>
      <div style="width:{_s(104)}px;height:{_s(104)}px;border:{_s(2)}px dashed rgba(90,74,48,.7);border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;color:{sec};font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(9)}px;transform:rotate(9deg);text-align:center;line-height:1.4;flex-shrink:0">
        <span style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(15)}px;letter-spacing:.1em">歸檔</span><span>{year}</span><span>ARCHIVE</span>
      </div>
    </div>
  </div>
</div>'''


def _tpl_lunar(uri, cfg, T, S, D, L, W, H, fx, fy, fs, bg=None):
    """月相历法盘：顶部月相八相序列+「月相歷」+副标；底部「月度诗词」+诗句。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    bc = cfg['base_color']                  # 深空
    cream = '#f4f0e4'
    dim = 'rgba(232,226,208,.7)'
    m = _month_en(D)
    month = f" · {m}" if m else ''
    # 月相序列（8 相）：满→亏→朔，用 CSS 渐变近似
    phases = (
        'background:#e8e2d0',
        'background:linear-gradient(90deg,#0b0e18 55%,#e8e2d0 55%)',
        'background:linear-gradient(90deg,#0b0e18 35%,#e8e2d0 35%)',
        'background:linear-gradient(90deg,#0b0e18 18%,#e8e2d0 18%)',
        'background:linear-gradient(270deg,#0b0e18 18%,#e8e2d0 18%)',
        'background:linear-gradient(270deg,#0b0e18 35%,#e8e2d0 35%)',
        'background:linear-gradient(270deg,#0b0e18 55%,#e8e2d0 55%)',
        'background:#0b0e18;border:1px solid rgba(232,226,208,.4)',
    )
    phase_labels = ('朔', '娥眉', '上弦', '盈凸', '虧凸', '下弦', '殘月', '晦')
    dots = ''.join(f'<div style="width:{_s(30)}px;height:{_s(30)}px;border-radius:50%;{p}"></div>' for p in phases)
    labels = ''.join(f'<span style="width:{_s(30)}px;text-align:center">{lb}</span>' for lb in phase_labels)
    return f'''<div class="stage" style="background:{bc};padding:0">
  <div style="position:relative;width:100%;height:100%;overflow:hidden">
    <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,6,12,.82) 0%,rgba(4,6,12,.28) 30%,rgba(4,6,12,.22) 60%,rgba(4,6,12,.86) 100%);z-index:5"></div>
    <div style="position:absolute;top:{_y(44)}px;left:0;right:0;z-index:20;text-align:center">
      <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(52)}px;color:{cream};letter-spacing:.24em;text-indent:.24em;text-shadow:0 3px 18px rgba(0,0,0,.95)">月相歷</div>
      <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(12)}px;color:{dim};letter-spacing:.4em;margin-top:{_y(6)}px">LUNAR PHASE ALMANAC{month}</div>
      <div style="display:flex;justify-content:center;gap:{_s(26)}px;margin-top:{_y(20)}px">{dots}</div>
      <div style="display:flex;justify-content:center;gap:{_s(26)}px;margin-top:{_y(6)}px;font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(8.5)}px;color:rgba(232,226,208,.55);letter-spacing:.1em">{labels}</div>
    </div>
    <div style="position:absolute;bottom:{_y(42)}px;left:0;right:0;z-index:20;text-align:center">
      <div style="display:flex;align-items:center;justify-content:center;gap:{_s(20)}px">
        <div style="width:{_x(84)}px;height:{_s(1.5)}px;background:linear-gradient(90deg,transparent,rgba(228,220,200,.8))"></div>
        <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(T, int(W*0.66), _s(36), '0.2em')}px;color:{cream};letter-spacing:.2em;text-indent:.2em;text-shadow:{_shadow('#f4f0e4', bg)}">{T}</div>
        <div style="width:{_x(84)}px;height:{_s(1.5)}px;background:linear-gradient(90deg,rgba(228,220,200,.8),transparent)"></div>
      </div>
      <div style="margin-top:{_y(8)}px;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(16)}px;color:rgba(228,220,200,.85);letter-spacing:.12em;text-shadow:0 2px 8px rgba(0,0,0,.9)">{S or '月有陰晴圓缺'} · {L or '千里共嬋娟'}</div>
    </div>
  </div>
</div>'''


def _tpl_score(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """乐谱手稿：上下五线谱+谱号；顶部「title」+速度/调号；底部落款。

    photo_ratio（可选，来自 cfg['photo_ratio']，经 render 归一为 float）：
      照片占比因子。默认 1.0 = v2 基准——顶部谱线 78px / 底部 56px / 标题 32px，
      此时照片约占 65%（见设计「默认 1.0 = 适度放大版」）。
      谱线高度与内部间隔按 1/photo_ratio 同步缩放（照片越大 → 谱线越矮、间隔越密）：
        photo_ratio<1 → 谱线更高、照片更小；photo_ratio>1 → 谱线更矮、照片更大。
      仅本款读取该字段；其它 6 款模板不读，行为不变。
    """
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    bc = cfg['base_color']                  # 米白乐谱纸
    paper = '#f4ecd8'
    ink = '#111'
    sec_ink = '#5a4a30'
    opus = f"Op. {_num(_seed('op', T, D, L), 1, 48)}"
    prov = _meta(D, L, meta_extra)
    pr = float(cfg.get('photo_ratio', 1.0))     # 照片占比因子（越大 → 照片越大）
    staff = 1.0 / pr                            # 谱线缩放因子（与照片占比互斥：pr 越大 → 谱线越矮）
    return f'''<div class="stage" style="background:{bc};padding:{_y(22)}px {_x(26)}px">
  <div style="position:relative;width:100%;height:100%;background:{paper};overflow:hidden;padding:{_y(28)}px {_x(32)}px;display:flex;flex-direction:column">
    <div style="display:flex;justify-content:space-between;align-items:flex-end;border-bottom:{_s(1.5)}px solid {ink};padding-bottom:{_y(10)}px">
      <div>
        <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(T, int(W*0.5), _s(32), '0.1em')}px;color:{ink};letter-spacing:.1em;text-shadow:{_shadow(ink, bg)}">{T}</div>
        <div style="font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-size:{_s(18)}px;color:#666;font-style:italic;margin-top:{_y(2)}px">{S}</div>
      </div>
      <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(11)}px;color:{sec_ink};letter-spacing:.2em;text-align:right">LENTO · ♩=52<br>KEY: {opus} · NIGHT</div>
    </div>
    <div style="position:relative;margin:{_y(18)}px 0;height:{_y(78*staff)}px;background:repeating-linear-gradient(180deg,transparent 0 {_y(24*staff)}px,rgba(20,20,20,.72) {_y(24*staff)}px {_y(26*staff)}px);border-radius:{_s(2)}px">
      <div style="position:absolute;left:{_x(14)}px;top:{_y(6)}px;font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-size:{_s(56)}px;color:{ink};line-height:1">𝄞</div>
      <div style="position:absolute;right:{_x(20)}px;top:{_y(12)}px;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(14)}px;color:#333;letter-spacing:.15em">{S or '夜燈初上 · 弱起漸強'}</div>
    </div>
    <div style="position:relative;width:100%;flex:1.2;overflow:hidden;border:{_s(1)}px solid {ink};transform:rotate(-.4deg);box-shadow:4px 6px 0 rgba(20,20,20,.15)">{_img(uri, cfg['tone_filter'])}</div>
    <div style="position:relative;margin-top:{_y(18)}px;height:{_y(56*staff)}px;background:repeating-linear-gradient(180deg,transparent 0 {_y(19*staff)}px,rgba(20,20,20,.62) {_y(19*staff)}px {_y(21*staff)}px)">
      <div style="position:absolute;left:{_x(14)}px;top:{_y(4)}px;font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-size:{_s(48)}px;color:{ink};line-height:1">𝄢</div>
      <div style="position:absolute;right:{_x(20)}px;bottom:{_y(6)}px;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(13)}px;color:#444;letter-spacing:.12em">{D or '歸途的腳步 · 漸弱漸遠'}</div>
    </div>
    <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end">
      <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(10)}px;color:#8a7a5a;letter-spacing:.22em">MANUSCRIPT · {prov or 'NIGHTFALL PRESS'}</div>
      <div style="font-family:&quot;CormorantItalic&quot;,{_serif_cn};font-size:{_s(24)}px;color:{ink};font-style:italic">{L or 'for the quiet hours'}</div>
    </div>
  </div>
</div>'''


def _tpl_arch(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """拱顶弧线：SVG textPath 曲线标题（BebasNeue 大字）拱顶 + 中轴副标；顶部渐变压暗。

    SVG 随画布宽度等比（viewBox 0 0 1024 360, width:100%、height:auto），弧线本身无需缩放。
    弧线文字基线在 viewBox y≈300/360 处（= path 端点基线），渲染到画布后的纵位 ≈ W*300/1024 − _arc_dy px
    （_arc_dy = 弧线标题上移量，见下行 #39 v4）；
    中部文字若只用 fy 缩放会在横/方画布上撞上弧线，故按 max(0.27*H, 0.30*W) 下移避让。
    """
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    bc = cfg['base_color']                  # 暖金
    curve = T or S                          # 弧线主字（BebasNeue；中文则回退衬线）
    mid = S or '燈火闌珊處'
    tail = _meta(D, L, meta_extra)
    _arc = int(max(H * 0.27, W * 0.30) * 0.65)  # 弧线收尾高度 → 中部文案避让量（2026-09-05 用户拍板：间距 -35%）
    # 2026-09-14 微调批2 #39：中段文案块整体上移 8%（先算后收——先取家族避让量再乘系数，
    # 同微调批1 pulip 的次序纪律）；2026-09-15 v4 补齐弧线标题同步上移 8%（见下行 _arc_dy）。
    # 位移只落承载 SVG 容器 top，不动 viewBox / path / 字号 / 字距（弧线形状的唯一源）→ 纯平移。
    _arc_dy = int(round(W * 300 / 1024 * 0.08))  # 弧线标题上移量 = path 端点基线(W*300/1024) 的 8%；与 _arc 互不相干
    _arc = int(round(_arc * 0.92))
    return f'''<div class="stage" style="background:#000;padding:0">
  <div style="position:relative;width:100%;height:100%;overflow:hidden">
    <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
    <div style="position:absolute;top:0;left:0;right:0;height:38%;background:linear-gradient(180deg,rgba(8,6,4,.86) 0%,rgba(8,6,4,.42) 60%,transparent 100%);z-index:5"></div>
    <svg viewBox="0 0 1024 360" style="position:absolute;top:-{_arc_dy}px;left:0;width:100%;height:auto;z-index:20">
      <defs><path id="arcPath" d="M 90 300 Q 512 80 934 300" fill="none"/></defs>
      <text style="font-family:&quot;BebasNeue&quot;,{_sans_cn};font-size:80px;fill:{bc};letter-spacing:12px;paint-order:stroke;stroke:rgba(0,0,0,.55);stroke-width:3px;text-transform:uppercase">
        <textPath href="#arcPath" startOffset="50%" text-anchor="middle">{curve}</textPath>
      </text>
    </svg>
    <div style="position:absolute;top:{_arc}px;left:0;right:0;z-index:20;text-align:center">
      <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{_s(38)}px;color:#ffffff;letter-spacing:.28em;text-indent:.28em;text-shadow:{_shadow('#ffffff', bg)}">{mid}</div>
      <div style="margin-top:{_y(8)}px;font-family:&quot;LXGWWenKai&quot;,{_serif_cn};font-size:{_s(17)}px;color:{bc};letter-spacing:.15em;text-shadow:{_shadow(bc, bg)}">{tail}</div>
    </div>
  </div>
</div>'''


def _tpl_viewfinder(uri, cfg, T, S, D, L, W, H, fx, fy, fs, bg=None):
    """相机取景器：四角对焦括号+中央十字+顶部机身参数+底部标题+副标。"""
    def _x(v): return int(v * fx)
    def _y(v): return int(v * fy)
    def _s(v): return int(v * fs)
    white = '#ffffff'
    a_k = _num(_seed('k', T, D, L), 26, 56) * 100
    f_no = _num(_seed('f', T, D, L), 14, 28) / 10
    iso = _num(_seed('iso', T, D, L), 200, 3200)
    shutter = _num(_seed('sh', T, D, L), 30, 240)
    if shutter >= 100:
        shutter_s = f"1/{shutter}"
    else:
        shutter_s = f"{shutter/100:.1f}s"
    _brk = _s(52)                           # 四角括号尺寸（正文形件，统一 fs 保持"方括号"）
    return f'''<div class="stage" style="background:#000;padding:0">
  <div style="position:relative;width:100%;height:100%;overflow:hidden">
    <div style="position:absolute;inset:0;z-index:1">{_img(uri, cfg['tone_filter'])}</div>
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 74%,rgba(0,0,0,.65) 100%);z-index:10"></div>
    <div style="position:absolute;top:{_y(78)}px;left:{_x(60)}px;width:{_brk}px;height:{_brk}px;border-top:{_s(3)}px solid rgba(255,255,255,.9);border-left:{_s(3)}px solid rgba(255,255,255,.9);z-index:20"></div>
    <div style="position:absolute;top:{_y(78)}px;right:{_x(60)}px;width:{_brk}px;height:{_brk}px;border-top:{_s(3)}px solid rgba(255,255,255,.9);border-right:{_s(3)}px solid rgba(255,255,255,.9);z-index:20"></div>
    <div style="position:absolute;bottom:{_y(96)}px;left:{_x(60)}px;width:{_brk}px;height:{_brk}px;border-bottom:{_s(3)}px solid rgba(255,255,255,.9);border-left:{_s(3)}px solid rgba(255,255,255,.9);z-index:20"></div>
    <div style="position:absolute;bottom:{_y(96)}px;right:{_x(60)}px;width:{_brk}px;height:{_brk}px;border-bottom:{_s(3)}px solid rgba(255,255,255,.9);border-right:{_s(3)}px solid rgba(255,255,255,.9);z-index:20"></div>
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:20;width:{_s(22)}px;height:{_s(22)}px">
      <div style="position:absolute;left:50%;top:0;bottom:0;width:{_s(2)}px;background:rgba(255,255,255,.9);transform:translateX(-50%)"></div>
      <div style="position:absolute;top:50%;left:0;right:0;height:{_s(2)}px;background:rgba(255,255,255,.9);transform:translateY(-50%)"></div>
    </div>
    <div style="position:absolute;top:{_y(26)}px;left:0;right:0;z-index:20;display:flex;justify-content:space-between;padding:0 {_x(30)}px;font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(12)}px;color:{white};text-shadow:0 1px 6px rgba(0,0,0,.9)">
      <span>AWB · {a_k}K</span><span>f/{f_no:.1f} · {shutter_s} · ISO {iso}</span>
    </div>
    <div style="position:absolute;bottom:{_y(80)}px;left:0;right:0;z-index:20;text-align:center">
      <div style="font-family:&quot;SourceSerifHeavy&quot;,{_serif_cn};font-size:{fit_title_fs(T, int(W*0.86), _s(96), '0.22em')}px;color:{white};letter-spacing:.22em;text-indent:.22em;text-shadow:{_shadow('#ffffff', bg)}">{T}</div>
      <div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{_s(24)}px;color:rgba(255,255,255,.8);letter-spacing:.34em;margin-top:{_y(10)}px">FOCUS LOCKED · {_frame_no(T, D, L)}</div>
    </div>
  </div>
</div>'''


# ===============================================================
# template_id -> 构建函数映射
# ===============================================================
_TPL = {
    '_tpl_auction': _tpl_auction,
    '_tpl_playbill': _tpl_playbill,
    '_tpl_dossier': _tpl_dossier,
    '_tpl_lunar': _tpl_lunar,
    '_tpl_score': _tpl_score,
    '_tpl_arch': _tpl_arch,
    '_tpl_viewfinder': _tpl_viewfinder,
}

# 不收 meta_extra 的模板：date/location 语义是折目/诗词内容（非注脚），见设计 §2.2（用户拍板 A）。
# 仅"有注脚位"的款（auction/dossier/score/arch）接收 meta_extra。
_NO_META_EXTRA_TPLS = {'_tpl_playbill', '_tpl_lunar', '_tpl_viewfinder'}


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


def render(photo_path, genre_id, title, sub, date, location, photo_ratio=None, meta_extra='', bg_luma=None, photo_focus_y=None):
    """载体隐喻 7 款渲染入口。

    genre_id 必须为 METAPHOR_CONFIGS 的键（engine 传入 --genre）。
    内部按 METAPHOR_CONFIGS[genre_id]['template_id'] 分发到具体构建函数。
    画幅按源图比例自适应（_canvas），模板绝对像素按 fx/fy/fs 缩放。
    返回完整 HTML 字符串。

    photo_ratio（可选）：照片占比因子，只对 config 带 photo_ratio 的款（music_manuscript）
    生效——谱线按 1/photo_ratio 缩放（见 _tpl_score）；缺省 None → 取 cfg['photo_ratio'] 或 1.0。
    其它款模板不读该字段，即使传入也不影响（行为不变）。
    meta_extra（可选）：镜头参数等补充注脚信息，经 _meta 拼在 date·location 之后（如拍卖图录的注脚）。
    仅透传给"有注脚位"的款（auction_catalog/declassified_file/music_manuscript/arch_curved）；
    playbill/lunar_dial/viewfinder_ui 的 date/location 语义是折目/诗词内容（非注脚），不收 meta_extra。
    """
    cfg = METAPHOR_CONFIGS[genre_id]
    esc = _html.escape
    uri = _photo_uri(photo_path)
    T, S, D, L = esc(title), esc(sub), esc(date), esc(location)
    W, H, fx, fy, fs = _canvas(photo_path)
    if photo_ratio is None:
        photo_ratio = cfg.get('photo_ratio', 1.0)
    # 非破坏性：不污染共享 METAPHOR_CONFIGS，仅本渲染生效
    cfg = dict(cfg)
    cfg['photo_ratio'] = photo_ratio
    # 落点背景亮度：文字落在"物"的卡纸/容器上（auction/playbill/dossier/score）→ 用基调色亮度；
    # 文字落在照片上（lunar/arch/viewfinder）→ 用 analyze_pixel 顶/底亮度（bg_luma）。
    # 按文字真实落区选分区（对齐 blueprint_engine 的分区策略，修"深字压暗底"）：
    #   文字落底（lunar_dial 底部诗词 / viewfinder_ui 底部标题）→ bottom；
    #   文字落顶（arch_curved 顶部弧线）→ top（保持既有行为，不改其它款）。
    if cfg['template_id'] in ('_tpl_auction', '_tpl_playbill', '_tpl_dossier', '_tpl_score'):
        bg = luma(cfg['base_color'])
    elif cfg['template_id'] in ('_tpl_lunar', '_tpl_viewfinder'):
        bg = _bright(bg_luma, 'bottom')
    else:
        bg = _bright(bg_luma, 'top')
    tpl = _TPL[cfg['template_id']]
    if cfg['template_id'] in _NO_META_EXTRA_TPLS:
        # 这 3 款 date/location 语义是折目/诗词内容（非注脚），不收 meta_extra（镜头注脚不渲染）
        body = tpl(uri, cfg, T, S, D, L, W, H, fx, fy, fs, bg)
    else:
        body = tpl(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra, bg)
    # WP-B · 照片取景焦点：y≠50 时 .ph 类规则追加 object-position（0=保顶裁脚）；
    # y=50/缺省 → focus_css 走 _BASE_CSS 默认值（含 ';object-position:center' 字面量），输出与历史字节一致。
    _fy = 50 if photo_focus_y is None else int(photo_focus_y)
    focus_css = ';object-position:center' if _fy == 50 else (';object-position:center %d%%' % _fy)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS_CSS}\n{_BASE_CSS(cfg["base_color"], W, H, focus_css)}</style></head><body>{body}</body></html>'


# 暴露给 engine_v2 的 --genre choices（虽然 engine 会 import METAPHOR_IDS from configs）
METAPHOR_IDS = list(METAPHOR_CONFIGS)
