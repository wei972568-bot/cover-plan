#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装裱/影格流派族 · 参数化渲染器（F 窗式 / T 顶栏式 / O 纹饰式）
===============================================================
render(photo_path, config, title, sub, date, location, meta_extra='') -> html_str
按 config['mode'] 分发三块模板。文字一律来自参数（不硬编码）。
唯一例外：french_elegance 规避头部版式（B23）的右上 ISSUE_04 红标为固定编辑标签（DOMICILIOGRAPHY / PORTRAITURE），按设计稿硬编码。
meta_extra（可选）：镜头参数等补充注脚信息（如 '35MM F1.4'），拼在 date·location 之后（if x 过滤空）。

画布：5 档自适应（_canvas_for 分桶，3:4=900×1200 基准；object-fit:cover 自适应裁剪）。
字体：@font-face 加载 D:/dsh/fonts 下的
  SourceSerifHeavy / LXGWWenKai / SpaceMono / CormorantItalic /
  PlayfairItalic / CinzelBold / BebasNeue（file:/// 绝对路径）。
照片：file:/// 绝对路径（chrome headless 可读）。
"""
import os
import html as _html
from pathlib import Path

# ---- 共享排版守卫（收敛宽度自适应 / 落点亮度对比 / clip-safe）----
from type_guard import fit_title_fs, luma, readability, clip_safe
# ---- 缺字预检共享模块（2026-09-05 §2.2）----
import font_guard
_FONT_GUARD_WHITELIST = font_guard.FONT_GUARD_WHITELIST

FONTS_DIR = 'D:/dsh/fonts'

# ---- 装裱族画幅自适应（2026-09-04，装裱自适应设计稿 WP-A）----
# 5 档分桶（移植 engine_v2 成熟模式）：比例精确 + 最长边 ≤1200，1:1 取 1080×1080 与 engine_v2 同口径；
# 3:4 基准 900×1200 与历史输出一致（fs=1.0 零回归）。阈值与 engine_v2 完全一致。
_SIZES = {'3:4': (900, 1200), '4:3': (1200, 900), '16:9': (1200, 675), '9:16': (675, 1200), '1:1': (1080, 1080)}


_BODONI_CSS = f'@font-face {{ font-family:"BodoniModa"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BodoniModa-Bold.ttf"); }}'

# 沐瑶软笔手写体（原 §5.2 script_bottom 主标）。按需注入（同 _BODONI_CSS 先例：仅 title_font 匹配时拼入，
# 不动其他款的 font_css 字节）。注意：文件真名为 "Muyao-Softbrush（沐瑶软笔手写体）.ttf"
# （探针样张 script_v4.html 里写的 "沐瑶软笔手写体.ttf" 已不存在，以盘上现状为准）。
# 2026-09-14 微调批2 #18：script_bottom 主标改 BodoniModa → 本常量与其注入分支
# （render 内 title_font=='MuyaoSoftbrush'）已无款引用 = 死代码，按口径④**保留**
# （清单见 docs/微调批2-设计.md §14.3；不得清理）。
_MUYAO_CSS = f'@font-face {{ font-family:"MuyaoSoftbrush"; src:url("file:///{FONTS_DIR}/免费商用书法字体/Muyao-Softbrush（沐瑶软笔手写体）.ttf"); }}'

# ---- 字体驱动段（2026-09-05 原 5 款，设计稿 §2.1/§2.3；2026-09-14 微调批2 −4 款 → 现役 1 款
# 〔par_avion_marcellus〕）：4 个 @font-face 按需注入常量**一律保留不清理**（口径④；拙楷两款
# 本批已删，`_ZHUOKAI_CSS`/`_YESEVA_CSS`/`_XINGKAI_CSS` 随之无款引用 = 死代码保留）。
# （照 _BODONI_CSS 先例：仅 title_font 匹配时拼入，不匹配款字节零变化）。
# 盘上实名 2026-09-05 ls 实证。缺字预检见 font_guard.py（title_font ∈ font_guard.FONT_GUARD_WHITELIST 的款启用）。
_MARCELLUS_CSS = f'@font-face {{ font-family:"Marcellus"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Marcellus-Regular.ttf"); }}'
_YESEVA_CSS = f'@font-face {{ font-family:"YesevaOne"; src:url("file:///{FONTS_DIR}/精选西文大刊与特色开源/YesevaOne-Regular.ttf"); }}'
_ZHUOKAI_CSS = f'@font-face {{ font-family:"ZhuoKai"; src:url("file:///{FONTS_DIR}/免费商用书法字体/江西拙楷2.0.ttf"); }}'
_XINGKAI_CSS = f'@font-face {{ font-family:"XingKai"; src:url("file:///{FONTS_DIR}/免费商用书法字体/三极行楷简体-粗.ttf"); }}'
# 兜底字体 @font-face（font_guard.FALLBACK_FONT_FAMILY）：思源宋体常规字重，仅在发生缺字兑底
# 时拼入（未兑底的款不引入，保字节一致门槛）。family 名与 font_guard.FALLBACK_FONT_FAMILY 一致。
_FALLBACK_SONG_CSS = f'@font-face {{ font-family:"思源宋体"; src:url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Regular-1.otf"); }}'


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

# 注意：这些名称用单引号（CSS 合法），因为嵌入 `style="..."`（双引号）属性，
# 双引号包住的名字会被宿主的 HTML 属性定界符截断（与 engine_v2 的 style='...' 单引号属性不同）。
_serif_cn = "'Songti SC','Source Han Serif SC','SimSun','Noto Serif CJK SC',serif"
_sans_cn = "'PingFang SC','Source Han Sans SC','Noto Sans CJK SC','Microsoft YaHei',sans-serif"

# 7 款字体（@font-face，路径同 engine_v2/flows.py；BebasNeue 为最佳推测路径，缺失则回退 sans）
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
# 小工具
# ---------------------------------------------------------------
def _photo_uri(photo_path):
    """绝对路径转 file:/// URI（chrome headless 可读）。"""
    return Path(os.path.abspath(photo_path)).as_uri()


def _ct(title_color, bg_luma=None):
    """文字对比保障（兼容旧签名）：浅字→暗影、深字→亮影；落点亮度感知（readability）。"""
    return readability(title_color, bg_luma)['shadow']


def _hex_to_rgba(hexcolor, alpha):
    """'#rrggbb' → 'rgba(r,g,b,a)'。

    band_bg 是 raw hex 直接插进 CSS `background:`（见 _render_window），`rgba(#hex,0.5)`
    是无效 CSS；要让它半透明以透出底下 .mat-bg 的纹饰，须先转成 rgba 形式。
    """
    h = str(hexcolor).lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'


def _frame_border(texture):
    """卡框边样式（按纹理/流派给不同款）。无纹理给极淡描边。"""
    t = texture or ''
    if t == 'gold_line':
        return '6px double #b8933f'
    if t == 'diagonal_silk':
        return '1px solid rgba(90,45,60,.25)'
    if t in ('letterbox_bars', 'letterbox_subtitles'):
        return '0px solid transparent'
    if t in ('geometric_line', 'ice_crack', 'xuan_paper'):
        return '1px solid rgba(0,0,0,.10)'
    return '1px solid rgba(0,0,0,.10)'


# meta_style -> 元信息行字体（默认 SpaceMono）
_META_FONT = {
    'mono_caps': 'SpaceMono', 'vogue_meta': 'SpaceMono', 'vinyl_meta': 'SpaceMono',
    'swiss_meta': 'SpaceMono', 'stamp_meta': 'SpaceMono', 'cinema_meta': 'SpaceMono',
    'italic': 'CormorantItalic',
}


def _meta_font_cls(style):
    return _META_FONT.get(style)


# ---------------------------------------------------------------
# 卡纸纹理（背景上图，叠在 mat_bg 之上，低透明度）
# 注：alpha 范围上限 .065（美术规范 §6 权威 0.04~0.065）。B22 已加深 10%（cap .065）。
#   —— xuan_paper 的次级层为 .033（低于规范下限 .04，为历史遗留 .03 的 ×1.1 结果，
#      设计 §2.2 要求的是 ×1.1 + cap .065，未要求抬升到 .04，故保留）；
#      ice_crack 次级层 2026-09-14 微调批2 #15 抬至 .049（主次同倍率 ×1.477，已入规范区间）。
# 带纹饰款的文案带透明度（band 半透明，透出底纹到文案区；B22）。
# ---------------------------------------------------------------
_BAND_TEX_ALPHA = 0.5
_TEX_CSS = {
    'geometric_line': 'repeating-linear-gradient(45deg, rgba(31,36,46,.055) 0 1px, transparent 1px 16px),'
                      'repeating-linear-gradient(-45deg, rgba(31,36,46,.044) 0 1px, transparent 1px 16px)',
    'diagonal_silk': 'repeating-linear-gradient(0deg, rgba(92,49,64,.055) 0 1px, transparent 1px 7px),'
                     'repeating-linear-gradient(90deg, rgba(92,49,64,.044) 0 1px, transparent 1px 7px)',
    'gold_line': 'repeating-linear-gradient(0deg, rgba(184,147,63,.065) 0 1px, transparent 1px 12px)',
    'ice_crack': 'repeating-linear-gradient(60deg, rgba(36,48,43,.065) 0 1px, transparent 1px 16px),'
                 'repeating-linear-gradient(-60deg, rgba(36,48,43,.049) 0 1px, transparent 1px 16px)',
    'xuan_paper': 'repeating-linear-gradient(30deg, rgba(60,50,40,.033) 0 1px, transparent 1px 9px),'
                  'radial-gradient(circle at 20% 30%, rgba(40,60,50,.044), transparent 60%)',
    # 万字锦地（45°交叉；DeepSeek 读图定制方法论）——米白宣纸感
    'wanzi': 'repeating-linear-gradient(45deg, rgba(31,36,46,.05) 0 1px, transparent 1px 14px),'
             'repeating-linear-gradient(-45deg, rgba(31,36,46,.05) 0 1px, transparent 1px 14px)',
    # 团花（radial 圆弧；DeepSeek 读图定制方法论）
    'tuanhua': 'radial-gradient(circle at 25% 30%, rgba(80,60,40,.06), transparent 40%),'
               'radial-gradient(circle at 75% 70%, rgba(80,60,40,.06), transparent 40%)',
}

# 纹饰（O 模式）：简化 CSS 纹饰，保证可辨认对应流派特征（诚实降级，非精细 SVG）
_ORN_CSS = {
    'par_avion': 'border:3px dashed #2b3a4a;'
                 'box-shadow:0 0 0 6px #fff inset,0 0 0 7px #c9d3dc inset;',
    'victorian_gilt': 'border:4px double #b8933f;'
                      'box-shadow:0 0 0 3px #5a4322 inset,0 0 0 9px #2e2418;',
    'gatsby_deco': 'border:3px solid #c9a25a;'
                   'background-image:repeating-linear-gradient(135deg, rgba(201,162,90,.28) 0 3px, transparent 3px 14px);',
    'perforated_stamp': 'border:3px dashed #1d2b33;'
                        'outline:2px solid #cbd2d6;outline-offset:-14px;',
    'meander': 'border:10px solid #2b3130;'
               'background-image:repeating-linear-gradient(90deg, #2b3130 0 3px, transparent 3px 14px),'
               'repeating-linear-gradient(0deg, #2b3130 0 3px, transparent 3px 14px);'
               'background-clip:padding-box;',
    'sprocket': 'border:22px solid #16130f;'
                'background-image:repeating-linear-gradient(180deg, transparent 0 16px, #e8dfc8 16px 26px),'
                'repeating-linear-gradient(90deg, transparent 0 16px, #e8dfc8 16px 26px),'
                'repeating-linear-gradient(90deg, transparent 0 16px, #e8dfc8 16px 26px);'
                'background-size:22px 100%, 100% 8px, 100% 8px;'
                'background-position:left, top, bottom;'
                'background-repeat:repeat-x, repeat-x, repeat-x;',
}


# ---------------------------------------------------------------
# 主渲染
# ---------------------------------------------------------------
def render(photo_path, config, title, sub, date, location, meta_extra='', bg_luma=None, photo_focus_y=50):
    esc = _html.escape
    W, H, fs = _canvas_for(photo_path)  # 画幅自适应（WP-A）：3:4 图 → 900×1200/fs=1.0 与历史一致
    fx = fs  # 等比单因子（装裱族几何统一乘 fs）

    # WP-B · 照片取景焦点：y≠50 时 .ph 挂 object-position（0=保顶裁脚；50=center 缺省不输出）
    ph_focus = ''
    if photo_focus_y is not None and int(photo_focus_y) != 50:
        ph_focus = 'object-position:center %d%%;' % int(photo_focus_y)

    mode = config['mode']
    mat_bg = config['mat_bg']
    frame_inset = int(round(int(config['frame_inset']) * fs))
    band_h = int(round(int(config['band_h']) * fs))
    texture = config.get('texture') or ''
    tone = config.get('tone_filter') or ''
    tf = f'filter:{tone};' if tone else ''
    uri = _photo_uri(photo_path)

    title_font = config['title_font']
    title_size = int(round(int(config['title_size']) * fs))
    title_color = config['title_color']
    en_font = config['en_font']
    meta_style = config.get('meta_style') or 'mono_caps'
    orn = config.get('svg_ornament')

    T = esc(title)
    S = esc(sub)
    meta = ' · '.join(x for x in [esc(date), esc(location), esc(meta_extra)] if x)

    # ---- font_guard 缺字预检（2026-09-05 §2.2 接入点 A；作用域=仅 title_font ∈ 白名单的款，保字节零回归门槛）----
    # 实现口径（与设计 §2.2 的对应关系如实标注）：
    # · title×title_font：全量逐字兜底（主标气质敏感）。check_and_wrap 收**未转义原文**（其内部
    #   逐字 esc——esc 后文本再 esc 会双转义）。**先 fit 后包**：fit_title_fs 按 esc 后纯文本
    #   （T=esc(title)）估宽，兜底 span 只在 fit 之后的最终 HTML 上包裹——否则 span 标记会被
    #   当成文本字符计入估宽，字号被错缩至下限（2026-09-05 advisor 评审修正）。
    # · sub×en_font：**不查不注**（如实标注）：en_font（SpaceMono/PlayfairItalic 等）不在
    #   font_guard.FONT_FILES 字库表内，font_covers_family 对未知 family 恒放行——sub 覆盖检查对
    #   现款不可触发（非静默：sub 落区字体栈尾含 _serif_cn 衬线回退，视觉成立）；如需真实 sub
    #   覆盖检查，先扩 FONT_FILES（另案）。
    # matting 三模板 title/sub 落区皆 HTML div（渲染介质确认逐落区实证，无 SVG <text> 落区）。
    _fg_comment = ''
    _fg_uncoverable = []
    _fg_fallback_used = False
    _fg_html = None
    if config['title_font'] in _FONT_GUARD_WHITELIST and title:
        _fg = font_guard.check_and_wrap(title, config['title_font'])
        _fg_fallback_used = _fg['fallback_used']
        _fg_comment = _fg['comment'] if _fg_fallback_used else ''
        _fg_uncoverable = _fg['uncoverable']
        _fg_html = _fg['html']
    if _fg_uncoverable:
        # 兜底字体也缺字（升格 ✗）：不能静默——**独立注释块**（font-fallback 块照常；本块另起，
        # 质检器按 token 各自解析。同块混排会让 font-uncoverable 正则永不命中——评审修正）。
        _fg_note_unc = 'font-uncoverable: ' + ','.join(_fg_uncoverable)
    else:
        _fg_note_unc = ''

    # 落点亮度感知：F/O 文字落在文字带（卡纸/黑带）上 → bg 用卡纸底色亮度（确定性，不依赖像素）；
    # T 顶栏文字落在照片上 → bg 用 analyze_pixel 顶/底亮度（bg_luma）或回退 mat_bg 亮度。
    # T_fit = esc 后纯文本（fit_title_fs 用，估宽不受兜底 span 标记污染）；T_html = 兜底包裹后 HTML。
    # 两者无兜底时相同。**先 fit 后包**（advisor 评审修正）：fit 按纯文本，包裹只在最终 HTML 上。
    T_html = T
    if _fg_fallback_used:
        T_html = _fg_html
    band_bg_luma = luma(config.get('band_bg') or mat_bg)
    if mode == 'T' and config.get('layout') == 'bottom':
        # WP-C · 底部落字家族布局（layout='bottom'）：文字全落底部 + 自下而上弱渐变（french_elegance/oriental 将来只加 config）
        bot = None
        if isinstance(bg_luma, dict):
            bot = bg_luma.get('bottom')
        elif bg_luma is not None:
            bot = bg_luma
        if bot is None:
            bot = luma(mat_bg)
        ct_b = readability(title_color, bot)['shadow']
        body = _render_bottom(T_html, S, meta, uri, tf, mat_bg, config,
                              title_font, title_size, title_color, en_font, meta_style, ct_b,
                              W, H, fs, ph_focus, T_fit=T)
    elif mode == 'T':
        top_bg_luma = None
        if isinstance(bg_luma, dict):
            top = bg_luma.get('top')
            top_bg_luma = top if top is not None else bg_luma.get('bottom')
        elif bg_luma is not None:
            top_bg_luma = bg_luma
        if top_bg_luma is None:
            top_bg_luma = luma(mat_bg)
        ct = readability(title_color, top_bg_luma)['shadow']
        body = _render_top(T_html, S, meta, uri, tf, mat_bg, config,
                           title_font, title_size, title_color, en_font, meta_style, ct, W, H, fs, ph_focus,
                           T_fit=T)
    else:
        ct = readability(title_color, band_bg_luma)['shadow']
        body = _render_window(mode, T_html, S, meta, uri, tf, mat_bg, config, texture, orn,
                              title_font, title_size, title_color, en_font, meta_style, ct,
                              frame_inset, band_h, W, H, fs, ph_focus, T_fit=T)
    font_css = FONTS_CSS
    if title_font == 'BodoniModa':
        font_css += _BODONI_CSS
    if title_font == 'MuyaoSoftbrush':
        font_css += _MUYAO_CSS
    # ---- 字体驱动 5 款按需注入（§2.3；不匹配款字节零变化）----
    if title_font == 'Marcellus':
        font_css += _MARCELLUS_CSS
    elif title_font == 'YesevaOne':
        font_css += _YESEVA_CSS
    elif title_font == 'ZhuoKai':
        font_css += _ZHUOKAI_CSS
    elif title_font == 'XingKai':
        font_css += _XINGKAI_CSS
    # 兜底字体 @font-face：仅实际发生缺字兜底包裹时拼入（不含纯注释场景）
    if _fg_fallback_used or _fg_uncoverable:
        font_css += _FALLBACK_SONG_CSS
    _fg_note = f'<!-- {_fg_comment} -->' if _fg_comment else ''
    _fg_note += f'<!-- {_fg_note_unc} -->' if _fg_note_unc else ''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css}\n{_BASE_CSS(mat_bg, W, H)}</style></head><body>{_fg_note}{body}</body></html>'


def _BASE_CSS(mat_bg, W=900, H=1200):
    return f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{mat_bg}}}
.stage{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{mat_bg}}}
.ph{{display:block;width:100%;height:100%;object-fit:cover}}
'''

# ---------- F / O 窗式 + 纹饰式 ----------
def _render_window(mode, T, S, meta, uri, tf, mat_bg, config, texture, orn,
                   title_font, title_size, title_color, en_font, meta_style, ct,
                   frame_inset, band_h, W, H, fs, ph_focus='', T_fit=None):
    # T_fit：估宽用纯文本（缺省=T；font_guard 兑底包裹时传 esc 后纯文本，防 span 标记计入估宽）
    if T_fit is None:
        T_fit = T
    texture_key = texture
    # 文字带底色（可选 band_bg，缺省=卡纸底色 mat_bg）→ 与大框底色形成含蓄色差
    band_bg = config.get('band_bg') or mat_bg
    # B22 · 纹饰覆盖文案区：有卡纸纹理（tex_bg 叠在 .mat-bg）时，把 band 底色改半透明，
    # 让底下的纹饰透到文案带里（不再被 band 底色盖住）。文字对比靠 _ct() 阴影保障；
    # 若某款纹饰太花致文字难读，该款可保留不透明（见设计 §2.1 视觉平衡）。
    if texture_key in _TEX_CSS:
        band_bg = _hex_to_rgba(band_bg, _BAND_TEX_ALPHA)
    # 独立外框（可选 outline_style，如 'inset:16px;border:2px solid #d3cbba' 完整内联样式）；
    # 旧 config 不设 → 不显示外框（保持既有款式不变）
    outline = config.get('outline_style') or ''
    frame_border = _frame_border(texture_key)
    # B24 · 双层框：photo_border（照片白内框）优先；缺省=该款各自 frame_border（见 _frame_border）
    border = config.get('photo_border') or frame_border
    if frame_inset == 0 and band_h == 0:
        band_h = int(round(200 * fs))  # 兜底：无卡边时也要有文字带
    band_h = max(band_h, int(round(120 * fs)))  # 下限：防 cinemascope/cinematic_subtitles 窄带文字溢出到照片区（护脸/P0-7）

    # 影格（letterbox）顶部黑条高度
    top_bar = int(round(90 * fs)) if texture_key == 'letterbox_bars' else 0

    # 照片窗：位于卡纸内，上为 frame_inset，下为 band，左右为 frame_inset
    ph_top = frame_inset + top_bar
    ph_bottom = band_h + frame_inset

    # 纹理背景叠加（叠在 mat 上）。注：letterbox_bars/letterbox_subtitles 无 _TEX_CSS 纹样，
    # 其"上下黑边"效果由下方 top_bar 分支（见上）直接给出几何黑条，不走纹理图。
    tex_bg = ''
    if texture_key in _TEX_CSS:
        tex_bg = f"background-image:{_TEX_CSS[texture_key]};"

    # O 纹饰：照片窗外一圈 `.orn` 框架
    orn_before = ''
    if mode == 'O' and orn:
        orn_css = _ORN_CSS.get(orn, '')
        # 纹饰框：占满画布 → 完整闭合的装裱框（左右贯穿、不因 band 遮盖而"断在底部"）
        orn_before = (
            f'<div class="orn orn-{orn}" '
            f'style="position:absolute;top:0;left:0;right:0;bottom:0;{orn_css}"></div>'
        )

    head = '<div class="stage"><div class="mat">'
    tail = '</div></div>'   # 关闭 .mat 与 .stage（与 _render_top 的 .stage 自闭合保持平衡）

    window = (
        f'<div class="photo-window" '
        f'style="position:absolute;top:{ph_top}px;left:{frame_inset}px;right:{frame_inset}px;'
        f'bottom:{ph_bottom}px;overflow:hidden;border:{border};background:#000;'
        f'box-shadow:0 10px 32px rgba(0,0,0,.22)">'
        f'<img class="ph" src="{uri}" style="{tf}{ph_focus}width:100%;height:100%;object-fit:cover"></div>'
    )

    top_bar_html = ''
    if top_bar:
        top_bar_html = f'<div style="position:absolute;top:0;left:0;right:0;height:{top_bar}px;background:#000;z-index:3"></div>'

    meta_font = _meta_font_cls(meta_style) or 'SpaceMono'
    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{en_font}&quot;,{_serif_cn};font-size:{int(round(15*fs))}px;'
                    f'letter-spacing:.3em;color:{title_color};opacity:.82">{S}</div>')
    meta_html = ''
    if meta:
        meta_html = (f'<div style="font-family:&quot;{meta_font}&quot;,monospace;font-size:{int(round(12*fs))}px;'
                     f'letter-spacing:.32em;color:{title_color};opacity:.65">{meta}</div>')

    # 宽度/高度自适应：band 固定高度 + overflow:hidden → 用 fit_title_fs 按"文字带可用宽"缩字号，
    # 再按 band_h 可用高收敛（防多行超高被上下裁）。为 sub/meta/gap 预留空间（按实际子项估算，
    # 上限 band_h×50% 防止小块影格（如 cinemascope band_h=95）被过度收缩）。
    _reserve = int(round(((22 if S else 0) + (18 if meta else 0) + 14 * ((1 if S else 0) + (1 if meta else 0))) * fs))
    _reserve = min(_reserve, int(band_h * 0.5))
    _avail_w = max(W - 2 * frame_inset - 60, 1)
    _avail_h = max(band_h - _reserve, 20)
    _title_fs = fit_title_fs(T_fit, _avail_w, title_size, '0.14em', max_h=_avail_h, line_h=1.14)
    # clip-safe：band 底部定位夹到画布内（band_bottom + band_h ≤ H，防越出画布被 overflow:hidden 裁）；
    # pad=0 保持 frame_inset=0 的影格黑带贴底（不作额外边距）。
    band_bottom = clip_safe(frame_inset, max(H - band_h, 0), 0)

    band = (
        f'<div class="band" style="position:absolute;left:{frame_inset}px;right:{frame_inset}px;'
        f'bottom:{band_bottom}px;height:{band_h}px;background:{band_bg};overflow:hidden;'
        f'display:flex;flex-direction:column;'
        f'justify-content:center;align-items:center;text-align:center;padding:0 {int(round(30*fs))}px;gap:{int(round(14*fs))}px">'
        f'<div class="t" style="font-family:&quot;{title_font}&quot;,{_serif_cn};font-size:{_title_fs}px;'
        f'line-height:1.14;letter-spacing:.14em;color:{title_color};text-shadow:{ct};font-weight:700">{T}</div>'
        f'{sub_html}{meta_html}'
        f'</div>'
    )

    # 独立外框：叠在 .stage 最外层（最上层），把「照片窗 + 文字带」整个框成一个装裱件。
    # 仅当 config 提供 outline_style 时渲染；pointer-events:none 不挡交互。
    frame_html = ''
    if outline:
        _outline = outline.rstrip()
        _sep = ';' if _outline.endswith(';') else ''
        frame_html = (
            f'<div class="frame" style="position:absolute;{_outline}{_sep}'
            f'pointer-events:none;z-index:6"></div>'
        )

    body = (
        f'{head}'
        f'<div class="mat-bg" style="position:absolute;inset:0;background-color:{mat_bg};{tex_bg}"></div>'
        f'{orn_before}'
        f'{window}'
        f'{top_bar_html}'
        f'{band}'
        f'{frame_html}'
        f'{tail}'
    )
    return body


# ---------- T 顶栏式（全幅照片 + 渐变 + 安全区文字） ----------
def _render_top(T, S, meta, uri, tf, mat_bg, config,
                title_font, title_size, title_color, en_font, meta_style, ct, W, H, fs, ph_focus='',
                T_fit=None):
    # T_fit：估宽用纯文本（同 _render_window 注）
    if T_fit is None:
        T_fit = T
    hero = config['hero_zone']

    # B24 · T 类白内框：有 photo_border → 叠一个白内框 overlay（不包住 img，保留渐变对照片的正常压暗）。
    # box-sizing:border-box 使 border 落在画布边缘；z-index:2 在渐变之上、文字(z-index:3)之下。
    ph_border = config.get('photo_border')
    frame_overlay = ''
    if ph_border:
        frame_overlay = (
            f'<div class="ph-frame" style="position:absolute;inset:0;border:{ph_border};'
            f'pointer-events:none;z-index:2"></div>'
        )

    # ---- B23 · 法式优雅·规避头部（french_elegance 专属：hero='top_and_bottom'）----
    if hero == 'top_and_bottom':
        return _french_avoid_top(T, S, meta, uri, tf, frame_overlay, config,
                                 title_font, title_size, title_color, en_font, meta_style, ct, fs, W,
                                 ph_focus, T_fit=T_fit)

    # 渐变方向按文字落区（避五官：文字只落顶部/侧边，底面加对比渐变）
    if hero == 'right_vertical':
        grad = ('linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.35) 45%, '
                'rgba(0,0,0,.82) 100%)')
        txt_pos = ('right:60px;top:50%;transform:translateY(-50%);writing-mode:vertical-rl;'
                   'text-align:left;')
        t_align = 'text-align:left;'
    elif hero == 'middle':
        grad = ('linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.6) 38%, '
                'rgba(0,0,0,.6) 62%, rgba(0,0,0,0) 100%)')
        txt_pos = 'top:44%;left:0;width:100%;transform:translateY(-50%);'
        t_align = 'text-align:center;'
    else:  # top_center
        grad = ('linear-gradient(180deg, rgba(0,0,0,.82) 0%, rgba(0,0,0,.45) 32%, '
                'rgba(0,0,0,0) 62%)')
        txt_pos = 'top:64px;left:50%;transform:translateX(-50%);'
        t_align = 'text-align:center;'

    # 顶栏标题宽度自适应：top_center/middle 为横向（按可用宽缩字号，防右缘溢出）；
    # right_vertical 为竖排（沿高度生长，不做水平 fit，垂直受画布高约束）。
    if hero == 'right_vertical':
        _t_fs = title_size
    else:
        _t_fs = fit_title_fs(T_fit, int(W * 0.88), title_size, '0.08em')

    sub_html = ''
    if S:
        sub_html = (f'<div style="font-family:&quot;{en_font}&quot;,{_serif_cn};font-size:{int(round(16*fs))}px;'
                    f'letter-spacing:.34em;color:{title_color};opacity:.85">{S}</div>')
    meta_html = ''
    if meta:
        mfont = _meta_font_cls(meta_style) or en_font
        meta_html = (f'<div style="font-family:&quot;{mfont}&quot;,monospace;font-size:{int(round(12*fs))}px;'
                     f'letter-spacing:.34em;color:{title_color};opacity:.7">{meta}</div>')

    body = (
        f'<div class="stage">'
        f'<img class="ph" src="{uri}" style="{tf}{ph_focus}width:100%;height:100%;object-fit:cover">'
        f'<div style="position:absolute;inset:0;background:{grad}"></div>'
        f'{frame_overlay}'
        f'<div style="position:absolute;{txt_pos}z-index:3;display:flex;flex-direction:column;'
        f'gap:{int(round(16*fs))}px;{t_align}">'
        f'<div style="font-family:&quot;{title_font}&quot;,{_serif_cn};font-size:{_t_fs}px;'
        f'line-height:1.08;letter-spacing:.08em;color:{title_color};text-shadow:{ct};font-weight:700">{T}</div>'
        f'{sub_html}{meta_html}'
        f'</div>'
        f'</div>'
    )
    return body


def _french_avoid_top(T, S, meta, uri, tf, frame_overlay, config,
                      title_font, title_size, title_color, en_font, meta_style, ct, fs=1.0, W=900,
                      ph_focus='', T_fit=None):
    # T_fit：估宽用纯文本（同 _render_window 注）
    if T_fit is None:
        T_fit = T
    """B23 · 法式优雅·规避头部（french_elegance hero='top_and_bottom'）。

    顶部英文大字偏上/左上（不压头顶）+ 右上 ISSUE_04 红标（固定文案）+ 底部中文条带
    （黑渐变；z-index:5 高于照片/白内框，不被裁）+ 头部区（中上）留空——规避人物特写头部。
    文案映射：T=顶部英文大字（主标），S=底部中文条带（「安靜的凝視」式），meta=顶部注脚。
    """
    # 顶部英文大字（偏上/左上，不压头顶）+ 顶部注脚；按 70% max-width 自适应防右缘溢出
    top_title = ''
    if T:
        _fs = fit_title_fs(T_fit, int(W * 0.66), title_size, '0.1em')
        top_title = (
            f'<div style="font-family:&quot;{title_font}&quot;,{_serif_cn};'
            f'font-size:{_fs}px;line-height:1.08;letter-spacing:.1em;'
            f'color:{title_color};text-shadow:{ct};font-weight:700">{T}</div>'
        )
    top_meta = ''
    if meta:
        mfont = _meta_font_cls(meta_style) or en_font
        top_meta = (
            f'<div style="font-family:&quot;{mfont}&quot;,monospace;font-size:{int(round(11*fs))}px;'
            f'letter-spacing:.28em;color:{title_color};opacity:.8;margin-top:{int(round(10*fs))}px">{meta}</div>'
        )
    # 右上红标（固定文案：ISSUE_04 / DOMICILIOGRAPHY / PORTRAITURE）
    issue = (
        f'<div style="position:absolute;top:4%;right:6%;z-index:3;background:#9b1c1c;'
        f'color:#f7f3ea;padding:{int(round(9*fs))}px {int(round(13*fs))}px;text-align:center;box-shadow:0 4px 14px rgba(0,0,0,.35)">'
        f'<div style="font-family:&quot;SpaceMono&quot;,monospace;font-size:{int(round(14*fs))}px;letter-spacing:.22em;'
        f'font-weight:700">ISSUE_04</div>'
        f'<div style="font-family:&quot;CormorantItalic&quot;,serif;font-size:{int(round(9*fs))}px;letter-spacing:.2em;'
        f'line-height:1.5;opacity:.9;margin-top:4px">DOMICILIOGRAPHY<br>PORTRAITURE</div>'
        '</div>'
    )
    # 底部中文条带（黑渐变；z-index:5 高于照片(z-auto)/白内框(z-index:2)，不被裁）
    band_inner = ''
    if S:
        band_inner = (
            f'<div style="font-family:&quot;{en_font}&quot;,{_serif_cn};font-size:{int(round(30*fs))}px;'
            f'letter-spacing:.3em;color:#f3ead9;font-weight:600;'
            f'text-shadow:0 1px 8px rgba(0,0,0,.8)">{S}</div>'
        )
    band = (
        '<div style="position:absolute;left:0;right:0;bottom:0;height:15%;z-index:5;'
        'background:linear-gradient(180deg,transparent,rgba(0,0,0,.85));'
        'display:flex;flex-direction:column;justify-content:flex-end;align-items:center;'
        f'text-align:center;padding:0 {int(round(30*fs))}px {int(round(22*fs))}px;gap:{int(round(8*fs))}px">'
        f'{band_inner}'
        '</div>'
    )

    body = (
        f'<div class="stage">'
        f'<img class="ph" src="{uri}" style="{tf}{ph_focus}width:100%;height:100%;object-fit:cover">'
        f'{frame_overlay}'
        f'<div style="position:absolute;top:12%;left:6%;z-index:3;display:flex;'
        f'flex-direction:column;gap:6px;max-width:70%">'
        f'{top_title}{top_meta}'
        f'</div>'
        f'{issue}'
        f'{band}'
        f'</div>'
    )
    return body


# ---------- T 底部式（底部落字家族：文字全落底部 + 自下而上弱渐变；WP-C 2026-09-04） ----------
def _render_bottom(T, S, meta, uri, tf, mat_bg, config,
                   title_font, title_size, title_color, en_font, meta_style, ct,
                   W, H, fs, ph_focus='', T_fit=None):
    # T_fit：估宽用纯文本（同 _render_window 注）
    if T_fit is None:
        T_fit = T
    """底部堆叠布局（顶栏系对人物照的解法）：主标→副标→meta 全落 bottom:6% 起，
    自下而上弱渐变（底部实、向上渐隐）压底保可读；readability 用 bg_luma['bottom'] 分区亮度。
    可复用：french_elegance/oriental 将来出底部变体只加 config（layout='bottom'）。
    §5.3（2026-09-05）config 可选键：title_spacing（缺省 .08em=家族缺省）/
    bottom_ornament（None|'stars'|'romann'，缺省 None）/
    sub_italic（bool，缺省 False）/ sub_color（缺省 title_color）。点缀插在主标与副标之间。
    渐变为家族统一规范（§5.1）：rgba(0,0,0,.82) 0% → .52 30% → transparent 45%。"""
    # 主标宽度自适应（88% 可用宽，同 top_center 口径）；字距 config 可调（§5.3，缺省 .08em=家族缺省）
    title_spacing = config.get('title_spacing') or '.08em'
    _t_fs = fit_title_fs(T_fit, int(W * 0.88), title_size, title_spacing)

    # §5.3 可选点缀（插在主标与副标之间）：stars=✦✦✦ 手账风 / romann=两侧渐隐金线+中心金菱形（罗马碑刻）
    ornament_html = ''
    bottom_ornament = config.get('bottom_ornament')
    if S and bottom_ornament == 'stars':
        # stars 字号 17px = 探针 v4（675 画布 13px）等比换算到 900 基准；字距 1.4em 照 §5.2
        ornament_html = (f'<div style="font-size:{int(round(17*fs))}px;letter-spacing:1.4em;'
                         f'margin-left:1.4em;color:#f5dfb8;opacity:.95;'
                         f'text-shadow:0 2px 10px rgba(0,0,0,.9)">✦ ✦ ✦</div>')
    elif S and bottom_ornament == 'romann':
        # 微调批3 A#2（2026-09-15）：线长 56→64（×1.15，内端贴菱形由 flex 结构自动保持）；
        # 站点 0%→85% 实金提前 = 平均不透明度 0.5→0.575（"降低透明度"落形，非改金色明度）。
        # 两线成镜像对（左 85% ↔ 右 15%）：实金段恒在内端、外端渐隐到 0。
        _line = (f'width:{int(round(64*fs))}px;height:1px;background:linear-gradient(90deg,transparent,#e8d9b0 85%)')
        _line_r = (f'width:{int(round(64*fs))}px;height:1px;background:linear-gradient(90deg,#e8d9b0 15%,transparent)')
        ornament_html = (f'<div style="display:flex;align-items:center;justify-content:center;gap:{int(round(12*fs))}px">'
                         f'<div style="{_line}"></div>'
                         f'<div style="width:{int(round(7*fs))}px;height:{int(round(7*fs))}px;background:#e8d9b0;'
                         f'transform:rotate(45deg);box-shadow:0 1px 6px rgba(0,0,0,.7)"></div>'
                         f'<div style="{_line_r}"></div>'
                         f'</div>')

    sub_html = ''
    if S:
        # §5.3 副标可调：sub_italic（斜体）+ sub_color（缺省=主标色，家族缺省行为）
        sub_color = config.get('sub_color') or title_color
        sub_italic = 'italic ' if config.get('sub_italic') else ''
        sub_html = (f'<div style="font-family:&quot;{en_font}&quot;,{_serif_cn};font-style:{sub_italic or "normal"};'
                    f'font-size:{int(round(16*fs))}px;'
                    f'letter-spacing:.34em;color:{sub_color};opacity:.85">{S}</div>')
    meta_html = ''
    if meta:
        mfont = _meta_font_cls(meta_style) or en_font
        meta_html = (f'<div style="font-family:&quot;{mfont}&quot;,monospace;font-size:{int(round(12*fs))}px;'
                     f'letter-spacing:.34em;color:{title_color};opacity:.7">{meta}</div>')

    body = (
        f'<div class="stage">'
        f'<img class="ph" src="{uri}" style="{tf}{ph_focus}width:100%;height:100%;object-fit:cover">'
        # 家族统一渐变（§5.1，2026-09-05 用户拍板 v4 探针参数"窄而深"）：底部 .82 实、30% 处 .52、45% 以上透明
        f'<div style="position:absolute;inset:0;background:linear-gradient(0deg, rgba(0,0,0,.82) 0%, rgba(0,0,0,.52) 30%, transparent 45%)"></div>'
        f'<div style="position:absolute;left:0;right:0;bottom:{int(round(0.06*H))}px;z-index:3;display:flex;'
        f'flex-direction:column;gap:{int(round(16*fs))}px;text-align:center">'
        f'<div style="font-family:&quot;{title_font}&quot;,{_serif_cn};font-size:{_t_fs}px;'
        f'line-height:1.08;letter-spacing:{title_spacing};'
        + (f'margin-left:{title_spacing};' if bottom_ornament else '')
        + f'color:{title_color};text-shadow:{ct};font-weight:700">{T}</div>'
        f'{ornament_html}{sub_html}{meta_html}'
        f'</div>'
        f'</div>'
    )
    return body