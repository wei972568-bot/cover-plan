#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设计语言族 · 模板 B 文件（新款入库批 2026-09-16，docs/新款入库批-设计.md §1.4 表 D）
=====================================================================
🔴#1 v2 落位（2026-09-16 用户裁定：分档依据 = 模板数，每文件 ≤ 10 个 `_tpl_*`）：
本文件 = 拆分第一步，承载本批两款新模板；`design_engine.py` 底部 import 接入 `_TPL`。
  · `_tpl_modern_spread`   —— 现代网格杂志风（第 18 款）
  · `_tpl_cultural_journal` —— 东方手记风（第 19 款）
  · `_mon_year`            —— 日期派生辅助（语义同源照抄 metaphor_engine._month_en，
                              **不跨模块 import**，避免族间依赖；设计档 §2.5）
承接批（模板拆分批）将把存量款 11–17 迁入本文件（提取边界见设计档 §4 拆分计划）。

模板函数签名同族先例（design_engine.py:211）：fn(uri, cfg, T, S, D, L, W, H, fx, fy, fs,
meta_extra='', bg=None)。两款几何缩放走刚性块 s = min(W/900, H/1200) + ox/oy
（照 torn_journal/torn_deckle 先例，§1.2 表 B：家族默认 fs 在 4:3/16:9 溢出实证否决）。
铁律（§1.2）：_x/_y 只用于绝对定位坐标；一切内部度量（宽高/间距/描边/字号）走 _sv/_svf。
"""
import re

from type_guard import fit_title_fs

# 循环导入的模块属性时序：本模块由 design_engine.py 底部 import（在 _serif_cn/_sans_cn
# 定义 :71-72 之后），故 import 处模块属性已就绪（§2.7 唯一硬前提）。
from design_engine import _serif_cn, _sans_cn

# 月份英文缩写表（语言常量，同 metaphor_engine._month_en 先例——模板内唯一"魔数"豁免面，
# 设计档 §6 #7）
_MON_EN = ('JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
           'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER')


def _mon_year(date):
    """从 date 提取 (month, year)，**两值各自独立可信**（无可信月份 → month=''；无可信年份
    → year=''）。调用方按槽位分别判空（设计档 §2.5 缺省处置）：
      · 页脚 ISSUED 行 / 邮戳中行 `★ {YYYY} ★`：**只需年份**（`if year:`）——无月份也渲；
      · 年份行 `{MON} {YYYY}`：**需两者**（`if month and year:`）——任一缺 → 整行不渲。

    提取口径照 metaphor_engine._month_en（metaphor_engine.py:146-152）三档可信模式，
    语义同源照抄（不跨模块 import）：
      ① 显式英文月份名（含 3 字母前缀）；② YYYY[./-]M[./-]D 取第 2 段为月；
      ③ 兜底：任一带分隔符的 1–12 段（best-effort）。
    {YYYY} 取 (19|20)\\d{2}（同 metaphor_engine._year_roman_or_arabic 口径）。
    """
    d = str(date or '')
    if not d:
        return '', ''
    up = d.upper()
    mon = ''
    for name in _MON_EN:                                   # ① 英文名
        if name in up:
            mon = name[:3]
            break
        if name[:3] in up:
            mon = name[:3]
            break
    if not mon:
        m = re.search(r'(?:19|20)\d{2}[.\-/](\d{1,2})[.\-/]\d{1,2}', d)   # ② 年-月-日
        if m and 1 <= int(m.group(1)) <= 12:
            mon = _MON_EN[int(m.group(1)) - 1][:3]
        else:
            m2 = re.search(r'[.\-/](\d{1,2})[.\-/]', d)    # ③ 兜底
            if m2 and 1 <= int(m2.group(1)) <= 12:
                mon = _MON_EN[int(m2.group(1)) - 1][:3]
    my = re.search(r'\b(?:19|20)\d{2}\b', d)
    return mon, (my.group(0) if my else '')


def _svf(v, s):
    """亚像素度量（0.1px 保留；D-9：探针含 1.5px 线宽与 12.5px 字号，int 化即丢半像素）。
    同源照抄 _sv 的 round(·,1) 口径（§2.2），不从引擎导入。"""
    return round(v * s, 1)


# ===============================================================
# 第 18 款 · modern_spread（现代网格杂志风）
# ===============================================================
def _tpl_modern_spread(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """现代网格杂志风（§2.3 参数表 = 实现契约；探针 _p2_after.html 终值转译）：
    暖亚麻底 #D6CEBB（R7）+ 外框线系统（顶部粗 3px/细 1.5px 双横线 + 左右竖线 + 底线）
    + 居中主标题块（西文 Prata 在上 / 中文思源黑 Heavy 在下，R8/R9）+ 三段式元数据条
    + 内嵌大图（1px 细框；**无画中画**，R1）+ 页脚两行导读。
    text_on_photo=False（护脸）：标题/元数据在照片上方、页脚在下方。
    参数位（S/T/D/L）缺省不渲或落 '—'（§2.5）；元数据条/页脚参数位超长走
    nowrap+ellipsis（D-13，防 scrollW ✗）。"""
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

    pal = cfg['palette']

    # ---- 外框线系统（§2.3 层序：粗横线/细横线/左右竖线/底线）----
    # frame_bottom=35 是**底锚**值（探针 `_p2_after.html:10-12` = `bottom:35px`，§2.3 来源列
    # 即该三行）⇒ 竖线底/底线在**块内** y = 1200 − 35 = 1165。**勿当 top 直接用**：那会给出
    # 竖线负高（−5px）+ 底线落在顶部 y≈33，框线系统整体失效（A1）。
    _bot_y = _y(1200 - lay["frame_bottom"])
    rules = (
        f'<div style="position:absolute;left:{_x(lay["frame_inset"])}px;'
        f'top:{_y(lay["top_rule_bold_y"])}px;'
        f'width:{_sv(900 - 2 * lay["frame_inset"])}px;height:{_svf(lay["top_rule_bold_h"], s)}px;'
        f'background:{pal["accent"]}"></div>'
        f'<div style="position:absolute;left:{_x(lay["frame_inset"])}px;'
        f'top:{_y(lay["top_rule_thin_y"])}px;'
        f'width:{_sv(900 - 2 * lay["frame_inset"])}px;height:{_svf(lay["top_rule_thin_h"], s)}px;'
        f'background:{pal["accent"]}"></div>'
        f'<div style="position:absolute;left:{_x(lay["frame_inset"])}px;'
        f'top:{_y(lay["frame_top"])}px;width:{_svf(lay["vert_rule_w"], s)}px;'
        f'height:{_bot_y - _y(lay["frame_top"])}px;'
        f'background:{pal["accent"]}"></div>'
        f'<div style="position:absolute;left:{_x(900 - lay["frame_inset"]) - _svf(lay["vert_rule_w"], s)}px;'
        f'top:{_y(lay["frame_top"])}px;width:{_svf(lay["vert_rule_w"], s)}px;'
        f'height:{_bot_y - _y(lay["frame_top"])}px;'
        f'background:{pal["accent"]}"></div>'
        f'<div style="position:absolute;left:{_x(lay["frame_inset"])}px;'
        f'top:{_bot_y - _svf(lay["base_rule_w"], s)}px;'
        f'width:{_sv(900 - 2 * lay["frame_inset"])}px;height:{_svf(lay["base_rule_w"], s)}px;'
        f'background:{pal["accent"]}"></div>'
    )

    # ---- 标题块（title_h=130 = 64+18+48 闭式；探针已钉 line-height:1，R9 锚点）----
    # 外框线一律为「div + height + background」（§2.3 层序），线宽走 _svf 亚像素（D-9）；
    # 粗横线高 = top_rule_bold_h（3 ⇒ 3:4 桶输出 `height:3.0px`，非 border-top 形制）。
    en_html = ''
    if S:
        # 西文行（Prata；D-13 兜底：超长省略，防越界）
        en_html = (
            f'<div style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
            f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,serif;'
            f'font-size:{_svf(lay["en_px"], s)}px;line-height:{lay["en_lh"]};'
            f'letter-spacing:{lay["en_letter"]};color:{pal["accent"]};'
            f'padding:0 {_sv(8)}px">{S}</div>')
    zh_html = ''
    if T:
        # 中文行（思源黑 Heavy；fit 一行不折行，超长缩档）
        hfs = fit_title_fs(T, _sv(lay['zh_fit_w']), _sv(cfg['scale']['hero_px']),
                           cfg['scale']['hero_letter'])
        zh_html = (
            f'<div style="margin-top:{_sv(lay["zh_gap"])}px;'
            f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn};'
            f'font-size:{hfs}px;line-height:{cfg["scale"]["hero_lh"]};'
            f'letter-spacing:{cfg["scale"]["hero_letter"]};color:{pal["accent"]};'
            f'text-shadow:{cfg["scale"]["hero_shadow"]}">{T}</div>')
    title_html = ''
    if en_html or zh_html:
        title_html = (f'<div style="position:absolute;left:0;top:{_y(lay["title_top"])}px;'
                      f'width:100%;height:{_sv(lay["title_h"])}px;text-align:center">'
                      f'{en_html}{zh_html}</div>')

    # ---- 元数据条（上下夹线 1.5px + flex space-between 三段；D/L 缺省 '—'，§2.5）----
    meta_l = D if D else '—'
    meta_r = L if L else '—'
    _meta_cell = ('white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0')
    meta_html = (
        f'<div style="position:absolute;left:{_x(lay["frame_inset"])}px;'
        f'top:{_y(lay["meta_top"])}px;width:{_sv(900 - 2 * lay["frame_inset"])}px;'
        f'height:{_sv(lay["meta_h"])}px;'
        f'border-top:{_svf(lay["meta_rule_w"], s)}px solid {pal["accent"]};'
        f'border-bottom:{_svf(lay["meta_rule_w"], s)}px solid {pal["accent"]};'
        f'display:flex;align-items:center;justify-content:space-between;'
        f'padding:0 {_sv(lay["meta_pad_x"])}px;box-sizing:border-box">'
        f'<div style="{_meta_cell};font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["meta_px"], s)}px;letter-spacing:{lay["meta_letter"]};'
        f'color:{pal["accent"]};max-width:32%">{meta_l}</div>'
        f'<div style="{_meta_cell};font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["meta_px"], s)}px;letter-spacing:{lay["meta_letter"]};'
        f'color:{pal["point"]};max-width:32%;text-align:center">{lay["fixed"]["meta_mid"]}</div>'
        f'<div style="{_meta_cell};font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["meta_px"], s)}px;letter-spacing:{lay["meta_letter"]};'
        f'color:{pal["accent"]};max-width:32%;text-align:right">{meta_r}</div></div>')

    # ---- 照片框（<img class="ph"> + 1px 边框；D-10：不覆写 object-position，
    #      继承 _BASE_CSS 的 focus_css → --photo-focus-y 生效）----
    photo_html = (
        f'<div style="position:absolute;left:{_x(lay["photo_left"])}px;'
        f'top:{_y(lay["photo_top"])}px;width:{_sv(lay["photo_w"])}px;'
        f'height:{_sv(lay["photo_h"])}px;box-sizing:border-box;'
        f'border:{_sv(lay["photo_border_w"])}px solid {lay["photo_border_color"]};'
        f'overflow:hidden">'
        f'<img class="ph" src="{uri}"></div>')

    # ---- 页脚（第 1 行〔粗段 + | + 细段，探针 `_p2_after.html` `.f1` 形制 = 内联内容〕
    #      + 右端 ISSUED（探针 `.f1r`：position:absolute;right:0;top:2px，不占行内流）；
    #      第 2 行 space-between）----
    # ⚠️ 形制依据（2026-09-16 实测）：第 1 行若把粗/细段各自包成 flex 子项并把 ISSUED 也作
    # flex 子项，则行内合计（粗 372 + bar 16 + 细 390 + ISSUED 103 = 881px）> 行宽 796px
    # ⇒ 两个文字段被压缩截断（sw>cw）⇒ 质检维度 1 `scrollW` ✗。探针原形制（ISSUED 绝对定位、
    # 第 1 行内容为内联流）无压缩、无越界，且与 §2.3/§2.5 的「右端 ISSUED」定位同源。
    ym = _mon_year(D)
    issued_html = ''
    if ym[1]:
        issued_html = (
            f'<div style="font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_sans_cn};'
            f'font-size:{_svf(lay["f1r_px"], s)}px;letter-spacing:{lay["f1r_letter"]};'
            f'color:{lay["f1r_color"]};position:absolute;right:0;'
            f'top:{_sv(lay["f1r_top"])}px;white-space:nowrap">'
            f'{lay["fixed"]["issued"]} {ym[1]}</div>')
    f2_r = L if L else '—'
    foot_html = (
        f'<div style="position:absolute;left:{_x(lay["foot_side"])}px;'
        f'top:{_y(lay["foot_top"])}px;width:{_sv(900 - 2 * lay["foot_side"])}px">'
        f'<div style="position:relative">'
        # 第 1 行 = 内联内容（探针 `.f1`）：粗段（Heavy，探针 `.f1 b`）+ bar + 细段（Regular）；
        # 全部固定装饰文案（§2.5），无参数位 ⇒ 无需省略号兜底；字号/字距锚 §2.3 f1_px/f1_letter。
        # family 必须显式声明（细段是裸文本节点 → 否则走浏览器默认字体 = 系统静默回退，
        # 违反 §2.3「页脚第 1 行（思源黑 Regular；粗段 = Heavy）」与 §1.7 字体实测生效）。
        f'<div style="white-space:nowrap;font-family:'
        f'&quot;{cfg["layout"]["extra_fonts"][0]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["f1_px"], s)}px;'
        f'letter-spacing:{lay["f1_letter"]};color:{pal["accent"]}">'
        f'<b style="font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_sans_cn}">'
        f'{lay["fixed"]["feat_bold"]}</b>'
        f'<span style="color:{lay["bar_color"]};margin:0 {_sv(lay["bar_pad"])}px">|</span>'
        # 细段/第 2 行 = 思源黑 Regular（§2.3：页脚第 1 行思源黑 Regular、粗段 Heavy；
        # family 名经 layout['extra_fonts'] 声明 → C-2 注入 + 模板引用同源）
        f'{lay["fixed"]["feat_thin"]}'
        f'</div>'
        f'{issued_html}</div>'
        f'<div style="display:flex;justify-content:space-between;'
        f'margin-top:{_sv(lay["f2_gap"])}px">'
        f'<div style="font-family:&quot;{cfg["layout"]["extra_fonts"][0]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["f2_px"], s)}px;letter-spacing:{lay["f2_letter"]};'
        f'color:{lay["f2_color"]};white-space:nowrap;overflow:hidden;'
        f'text-overflow:ellipsis;min-width:0;max-width:70%">{lay["fixed"]["deck"]}</div>'
        f'<div style="font-family:&quot;{cfg["layout"]["extra_fonts"][0]}&quot;,{_sans_cn};'
        f'font-size:{_svf(lay["f2_px"], s)}px;letter-spacing:{lay["f2_letter"]};'
        f'color:{lay["f2_color"]};white-space:nowrap;max-width:28%;'
        f'text-align:right">{f2_r}</div></div></div>')

    return f'''<div class="stage" style="background:{pal["primary"]}">
  {rules}
  {title_html}
  {meta_html}
  {photo_html}
  {foot_html}
</div>'''


# ===============================================================
# 第 19 款 · cultural_journal（东方手记风）
# ===============================================================
def _tpl_cultural_journal(uri, cfg, T, S, D, L, W, H, fx, fy, fs, meta_extra='', bg=None):
    """东方手记风（§2.4 参数表 = 实现契约；探针 _p3fix.html 终值转译）：
    暖纸纹底（feTurbulence data-URI tile，D-12 &quot; 实体包裹）+ 暖色做旧晕 + 头部三行
    标题群（行高钉死 1.0，闭式 14+32+68+35+13 = 162 ⇒ 底边 214，R6 构造保证）+
    凹压钢印 SVG + 单张卡纸装裱照片（10px 卡纸 + 双层投影；**只用一张**，R2/R4）+
    图注 1 行（R5）+ 发丝分隔线 + 手记行（手绘箭头 SVG〔恰 1 枚〕+ EN 手写 + 中文小字）+
    年份行（flex：**内联 SVG 双实心三角标记 + 年份文字**，零字体依赖，J1 裁定 §2.4.1）+
    做旧邮戳 SVG。全部 SVG 资产自包含（无外部图片/字体依赖）；filter id 前缀化
    cj-*（D-11，防裸 id 碰撞）。text_on_photo=False（护脸）。"""
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

    pal = cfg['palette']
    point = pal['point']

    # ---- 纸纹层 + 暖色晕层（CSS 串取 §2.4 参数表布局键 `grain`/`wash`——不藏魔数，
    #      §6 #7；D-12：内联 style 双引号包裹 → data URI 内双引号已实体化
    #      &quot;、SVG 内层单引号、# 写 %23）----
    grain_css = lay['grain']
    wash_css = lay['wash']
    layers = (
        f'<div style="position:absolute;inset:0;background-image:{grain_css};'
        f'background-size:240px 240px;opacity:.42"></div>'
        f'<div style="position:absolute;inset:0;background-image:{wash_css}"></div>')

    # ---- 头部三行标题群（eyebrow → h1 → sub；行高钉死 1.0 闭式，R6/🟡#2）----
    sub_txt = S if S else lay['fixed']['sub']
    # 中文大标 fit 缩档（v3 用户裁定 ② = 自动缩字号、不丢字；§2.4 表后 fit 注）——容器宽 =
    # h1_fit_w 796（**版心宽** 900 − 2×52；头部容器 left:0;width:100% 且无 border/padding
    # ⇒ **无额外扣减**），下限 12px = fit_title_fs 内建（不另设款级下限）；用法同 modern_spread
    # （:145 + design_configs.py:1445）——两款同源同口径。缩档只缩小该行行盒高（容器高 162
    # 不动 ⇒ 底边 214 / photo_top 264 / R6 间距 50px 不变）；T 为空时不渲该行、此值不被使用。
    h1_fs = fit_title_fs(T, _sv(lay['h1_fit_w']), _sv(cfg['scale']['hero_px']),
                         cfg['scale']['hero_letter'])
    head = (
        f'<div style="position:absolute;left:0;top:{_y(lay["head_top"])}px;width:100%;'
        f'height:{_sv(lay["head_h"])}px;text-align:center;overflow:hidden">'
        f'<div style="font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,serif;'
        f'font-size:{_svf(lay["eyebrow_px"], s)}px;line-height:{lay["eyebrow_lh"]};'
        f'letter-spacing:{lay["eyebrow_letter"]};color:{point}">{lay["fixed"]["eyebrow"]}</div>'
        + (f'<div style="margin-top:{_sv(lay["h1_gap"])}px;'
           f'font-family:&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn};font-weight:normal;'
           f'font-size:{h1_fs}px;line-height:{cfg["scale"]["hero_lh"]};'
           f'letter-spacing:{cfg["scale"]["hero_letter"]};color:{pal["accent"]};'
           f'text-shadow:{cfg["scale"]["hero_shadow"]}">{T}</div>'
           if T else '')
        + f'<div style="margin-top:{_sv(lay["sub_gap"])}px;'
        f'font-family:&quot;{cfg["fonts"]["data"]}&quot;,{_serif_cn};'
        f'font-size:{_svf(lay["sub_px"], s)}px;line-height:{lay["sub_lh"]};'
        f'letter-spacing:{lay["sub_letter"]};color:{lay["sub_color"]}">{sub_txt}</div></div>')

    # ---- 凹压钢印 SVG（§2.4 emboss 终值；SVG 资产内坐标 = viewBox 字面量，不乘 s；
    #      元素盒/位置走 _sv/_x/_y；id 前缀 cj-emboss，D-11）----
    em = lay['emboss']
    emx, emy = _x(em['left']), _y(em['top'])
    emboss_svg = (
        f'<svg width="{_sv(em["w"])}" height="{_sv(em["h"])}" viewBox="0 0 112 112" '
        f'style="position:absolute;left:{emx}px;top:{emy}px;transform:rotate({em["rot"]}deg);'
        f'opacity:.17;z-index:15" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><filter id="cj-emboss" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="3" seed="5" '
        f'result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="1.6"/></filter></defs>'
        f'<g filter="url(#cj-emboss)" fill="none" stroke="{pal["accent"]}">'
        f'<circle cx="56" cy="56" r="42" stroke-width="1.4"/>'
        f'<circle cx="56" cy="56" r="37" stroke-width="0.7"/>'
        f'<text x="56" y="52" text-anchor="middle" fill="{pal["accent"]}" stroke="none" '
        f'font-family="&quot;{cfg["fonts"]["emotion"]}&quot;,serif" font-size="9" '
        f'letter-spacing="1.5">{lay["fixed"]["emboss_l1"]}</text>'
        f'<text x="56" y="66" text-anchor="middle" fill="{pal["accent"]}" stroke="none" '
        f'font-family="&quot;{cfg["fonts"]["emotion"]}&quot;,serif" font-size="7.5" '
        f'letter-spacing="1.2">{lay["fixed"]["emboss_l2"]}</text></g></svg>')

    # ---- 照片卡纸（10px 卡纸 border-box + 双层投影；净图像区 776×704）----
    photo_html = (
        f'<div style="position:absolute;left:{_x(lay["photo_left"])}px;'
        f'top:{_y(lay["photo_top"])}px;width:{_sv(lay["photo_w"])}px;'
        f'height:{_sv(lay["photo_h"])}px;box-sizing:border-box;'
        f'border:{_sv(lay["photo_mat"])}px solid {lay["photo_mat_color"]};'
        f'box-shadow:{lay["photo_shadow"]};z-index:10">'
        f'<img class="ph" src="{uri}"></div>')

    # ---- 图注（1 行，R5；Cinzel，容器宽 796 居中）----
    cap_html = (
        f'<div style="position:absolute;left:{_x(lay["photo_left"])}px;'
        f'top:{_y(lay["cap_top"])}px;width:{_sv(lay["photo_w"])}px;text-align:center;'
        f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,serif;'
        f'font-size:{_svf(lay["cap_px"], s)}px;letter-spacing:{lay["cap_letter"]};'
        f'color:{lay["cap_color"]};z-index:10">{lay["fixed"]["caption"]}</div>')

    # ---- 发丝分隔线（linear-gradient 两端渐隐 1px）----
    rule_html = (
        f'<div style="position:absolute;left:{_x(lay["rule_side"])}px;'
        f'top:{_y(lay["rule_top"])}px;width:{_sv(900 - 2 * lay["rule_side"])}px;height:1px;'
        f'background:linear-gradient(90deg,rgba(62,47,38,0),rgba(62,47,38,.35) 12%,'
        f'rgba(62,47,38,.35) 88%,rgba(62,47,38,0));z-index:10"></div>')

    # ---- 手记行（箭头 SVG 恰 1 枚〔R2 保留枚〕+ EN 手写 + 中文小字）----
    ar = lay['arrow']
    note_html = (
        f'<div style="position:absolute;left:{_x(lay["note_left"])}px;'
        f'top:{_y(lay["note_top"])}px;width:{_sv(lay["note_w"])}px;display:flex;'
        f'align-items:center;z-index:10">'
        f'<svg width="{_svf(ar["w"], s)}" height="{_svf(ar["h"], s)}" viewBox="0 0 40 34" '
        f'style="flex:none;transform:rotate({ar["rot"]}deg);opacity:.82" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M4 30 C 12 27.5, 22 21, 31 8" fill="none" stroke="{point}" '
        f'stroke-width="1.5" stroke-linecap="round"/>'
        f'<path d="M24 10.5 L 32 6.5 L 30.5 15" fill="none" stroke="{point}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        f'<div style="margin-left:{_sv(lay["note_en_gap"])}px;'
        # EN 手写注记 = 霞鹜文楷 Regular（§2.4 `note_px` 说明列）；family 经
        # layout['extra_fonts'][1] 声明 → C-2 注入与模板引用同源（D-4/D-5）；
        # 不走 emotion=CinzelBold（Cinzel 无本段手写体语义）
        f'font-family:&quot;{cfg["layout"]["extra_fonts"][1]}&quot;,{_serif_cn};'
        f'font-size:{_svf(lay["note_px"], s)}px;color:{lay["note_color"]};'
        f'white-space:nowrap">{lay["fixed"]["note_en"]}</div>'
        f'<div style="margin-left:{_sv(lay["note_cn_gap"])}px;'
        # 手记中文小字 = 思源宋 Regular（§2.4 `note_cn_px` 说明列；extra_fonts[0]）
        f'font-family:&quot;{cfg["layout"]["extra_fonts"][0]}&quot;,{_serif_cn};'
        f'font-size:{_svf(lay["note_cn_px"], s)}px;color:{lay["note_cn_color"]};'
        f'white-space:nowrap">{lay["fixed"]["note_cn"]}</div></div>')

    # ---- 年份行（右对齐 flex：内联 SVG 双实心三角标记 + 年份文字；J1 裁定 §2.4.1）----
    # 零字体依赖（J1 核心理由，实现注记）：该标记无文本节点 ⇒ 不参与任何字体面——
    # 不入 C-2 @font-face 注入名单、不入 C-3 槽位覆盖表、不入 C-4 fonts.check 名单；
    # layout 不设承载文本键（无字面量即无缺字可能）。原 U+25B8 三角字符在项目字体库
    # 全部候选零覆盖（探针实为系统静默回退）——产物文本节点 U+25B8 计数 = 0（A11）。
    # 元素盒走 _sv；viewBox 内坐标不乘 s（缩放由元素盒承担，
    # preserveAspectRatio="none" 使 viewBox 与元素盒线性对应）；窄缝 = viewBox 资产
    # 常量（B 左缘 13 − A 顶点 11 = 2，layout 不设键，🔵#8 键面澄清）。
    ym = _mon_year(D)
    year_html = ''
    if ym[0] and ym[1]:      # 年份行 = {MON} {YYYY}：§2.5 明定「无年份/月份 → 整行不渲」
        year_html = (
            # 右锚 = _x(year_right)（§2.4.1 骨架 `right:{_x(year_right)}`；§2.4 注
            # 「位置不变：year_top=1098 / year_right=52（_y / _x）」）——勿写成
            # _x(900 - year_right)：那会把整行推到画布左外（3:4 下 right:848px）。
            f'<div class="cj-yearrow" style="position:absolute;top:{_y(lay["year_top"])}px;'
            f'right:{_x(lay["year_right"])}px;display:flex;align-items:center;'
            f'line-height:{lay["year_lh"]};z-index:10">'
            f'<svg class="cj-yearmark" width="{_sv(lay["year_mark_w"])}" '
            f'height="{_sv(lay["year_mark_h"])}" viewBox="0 0 24 12" '
            f'preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            f'<polygon points="0,0 11,6 0,12" fill="{point}"/>'
            f'<polygon points="13,0 24,6 13,12" fill="{point}"/></svg>'
            f'<span style="margin-left:{_sv(lay["year_mark_gap"])}px;'
            f'font-family:&quot;{cfg["fonts"]["emotion"]}&quot;,{_serif_cn};'
            f'font-size:{_svf(lay["year_px"], s)}px;letter-spacing:{lay["year_letter"]};'
            f'color:{lay["year_color"]}">{ym[0]} {ym[1]}</span></div>')

    # ---- 做旧邮戳 SVG（§2.4 postmark 终值；★ 段改覆盖家族 SourceSerifHeavy——
    #      Cinzel 无 U+2605，§2.6 缺字注；id 前缀 cj-rough/cj-ink，D-11）----
    pm = lay['postmark']
    pmx = _x(900 - pm['right']) - _sv(pm['w'])
    pmy = _y(pm['top'])
    ystr = ym[1]
    pm_mid = (f'<text x="74" y="76" text-anchor="middle" '
              f'font-family="&quot;{cfg["fonts"]["hero"]}&quot;,{_serif_cn}" '
              f'font-size="11" letter-spacing="1.2" fill="{point}">★ {ystr} ★</text>'
              if ystr else '')
    city = L if L else lay['fixed']['postmark_city']
    postmark_svg = (
        f'<svg width="{_sv(pm["w"])}" height="{_sv(pm["h"])}" viewBox="0 0 148 132" '
        f'style="position:absolute;left:{pmx}px;top:{pmy}px;z-index:12" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<filter id="cj-rough" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="11" '
        f'result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"/></filter>'
        f'<filter id="cj-ink" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="3" seed="3" '
        f'result="n"/><feColorMatrix in="n" type="matrix" '
        f'values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.9 0" result="a"/>'
        f'<feComposite in="SourceGraphic" in2="a" operator="out"/></filter>'
        f'</defs>'
        f'<g filter="url(#cj-rough)" opacity=".78">'
        f'<circle cx="74" cy="60" r="48" fill="none" stroke="{point}" stroke-width="2.1"/>'
        f'<circle cx="74" cy="60" r="41" fill="none" stroke="{point}" stroke-width="0.9" '
        f'stroke-dasharray="1.6 2.6"/>'
        f'<text x="74" y="50" text-anchor="middle" '
        f'font-family="&quot;{cfg["fonts"]["emotion"]}&quot;,serif" '
        f'font-size="12.5" letter-spacing="1.6" fill="{point}">{city}</text>'
        f'{pm_mid}'
        f'<text x="74" y="92" text-anchor="middle" '
        f'font-family="&quot;{cfg["fonts"]["emotion"]}&quot;,serif" '
        f'font-size="8.5" letter-spacing="2" fill="{point}">'
        f'{lay["fixed"]["postmark_country"]}</text>'
        f'<path d="M30 108 Q 74 100 118 108" fill="none" stroke="{point}" '
        f'stroke-width="1.2" opacity=".55"/>'
        f'<path d="M30 116 Q 74 108 118 116" fill="none" stroke="{point}" '
        f'stroke-width="1.2" opacity=".55"/></g></svg>')

    return f'''<div class="stage" style="background:{pal["primary"]}">
  {layers}
  {head}
  {emboss_svg}
  {photo_html}
  {cap_html}
  {rule_html}
  {note_html}
  {year_html}
  {postmark_svg}
</div>'''
