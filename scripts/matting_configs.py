#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装裱/影格流派族 · 参数化 configs（13 款，2026-09-05 真删除 24 款 38→14 + 字体驱动 5 款 14→19；2026-09-14 −fashion_vogue → 18；2026-09-14 微调批2 −5 款 → 13）
===========================================
独立流派族，不与蓝图 28 套 / engine_v2 现有 14 套合并命名。
2026-09-05 真删除（docs/批量设计-真删除与字体驱动款-设计.md §1）：删 24 款 config + 4 条别名
（chroma/polaroid/victorian/stamp，其目标款已删），38→14；删后基线存 examples/_baseline_34/。
2026-09-05 字体驱动 5 款（§2.1 配对表）：par_avion_marcellus（2026-09-14 微调批2 删 elegance_yeseva /
oriental_zhuokai / film_xingkai / warm_zhuokai_card 4 款后，本组余此 1 款；无新模板，
复制骨架 config 改字体/字号/字距）。缺字预检见 font_guard.py（title_font ∈ 白名单的款）。

每款 config 字段（供 matting_engine.render 使用）：
  mode          : 'F' 窗式（照片窗 + 卡框/黑边 + 底部文字带）| 'T' 顶栏式（全幅照片+渐变）
                  | 'O' 纹饰式（照片窗 + svg/CSS 纹饰框）
  topology      : 绑定拓扑槽位（metadata；权威注册在 topology_registry.py）
  hero_zone     : 主标真实落区枚举（供 validate_layout_consistency 计算）
  text_on_photo : bool —— hero 文字是否落在照片上。False=字落独立卡纸/黑边带（护脸判别键）
  mat_bg        : 卡纸/装裱底色（hex；此即"大框底色"）
  band_bg       : 文字带底色（可选 hex；缺省=mat_bg。设不同值 → 文字带与大框底色形成含蓄色差）
  texture       : 卡纸纹理 key（'' 无纹理；geometric_line / diagonal_silk / gold_line /
                  ice_crack / xuan_paper / letterbox_bars / letterbox_subtitles）
  outline_style : 独立外框完整内联样式（可选，如 'inset:16px;border:2px solid #d3cbba'；
                  渲染为叠在 stage 最外层的细框，把照片窗+文字带包成一个装裱件。缺省=无外框）
  photo_border  : 照片白内框完整内联样式（可选，如 '14px solid #ffffff'；缺省=该款各自 frame_border，
                  见 _frame_border。给照片四周加白/浅色粗边 → 与卡纸外框形成"双层框"）
  frame_inset   : 卡纸边宽（px，照片窗外缘到画布边的留白）
  band_h        : 底部文字带高度（px；F/O 用；T 全幅不用）
  title_font    : 主标字体（对应 @font-face family）
  title_size    : 主标字号（px）
  title_color   : 主标颜色（hex）
  en_font       : 副标/西文字体
  meta_style    : 元信息行样式 key（mono_caps / italic / vogue_meta / swiss_meta / vinyl_meta /
                  stamp_meta...）
  svg_ornament  : 纹饰 key（仅 mode=='O'；None 否则）
  tone_filter   : 照片 CSS filter（'' 无；如 sepia(0.2) saturate(1.2)）

title / sub / date / location 一律由 CLI 参数传入，**不硬编码文案**。
"""

# ---- 13 款 config 的共享默认（保证字段全集；每款按气质覆盖）----
_DEFAULT = {
    'mode': 'F',
    'topology': 'face_portrait',
    'hero_zone': 'bottom_card',
    'text_on_photo': False,
    'mat_bg': '#f7f4ee',
    'texture': '',
    'frame_inset': 46,
    'band_h': 230,
    'title_font': 'SourceSerifHeavy',
    'title_size': 46,
    'title_color': '#20242a',
    'en_font': 'SpaceMono',
    'meta_style': 'mono_caps',
    'svg_ornament': None,
    'tone_filter': '',
}


def _cfg(**kw):
    """基于默认填充一份完整 config，再按款覆盖。保证 15 字段全集、少冗余。"""
    c = dict(_DEFAULT)
    c.update(kw)
    return c


MATTING_CONFIGS = {
    # ===============================================================
    # 任务2 · 剩余款（2026-09-05 §1 真删除后 14 款；分组注释保留历史脉络）
    # ===============================================================
    # ---------- A 画廊/卡纸窗（F，face_portrait，text_on_photo=False）----------
    'dark_contact_print': _cfg(
        mat_bg='#0d0d0d', frame_inset=0, band_h=210,
        title_font='CinzelBold', title_size=61, title_color='#f0f0f0',
        en_font='SpaceMono', tone_filter='grayscale(1)',
    ),
    'gallery_ice_crack': _cfg(
        mat_bg='#e8ece9', texture='ice_crack', frame_inset=48, band_h=230,
        title_font='SourceSerifHeavy', title_size=64, title_color='#24302b',
        en_font='SpaceMono', tone_filter='saturate(0.9)',
    ),
    'gallery_centered_axis': _cfg(
        photo_border='9px solid #ffffff',
        mat_bg='#f5f2ec', frame_inset=36, band_h=240,
        title_font='SourceSerifHeavy', title_size=65, title_color='#222222',
        en_font='SpaceMono',
    ),

    # ---------- D 现代/素笺（T 顶栏式，text_on_photo==True，不标护脸）----------
    # 2026-09-14 用户拍板：fashion_vogue 彻底删除（顶栏大字压照片顶部的 vogue 款下线；
    # D 族余 oriental_plain_paper / french_elegance 等）。
    # “vogue 底部变体”原款 vogue_bottom 亦于 2026-09-14（微调批2 #17）按用户拍板彻底删除——
    # 其“文字全落底部堆叠 + 自下而上弱渐变 + BodoniModa 主标”布局由 script_bottom 接棒
    # （layout='bottom' 参数化路径保留，家族可调键见 matting_engine._render_bottom）。
    # —— 底部落字家族扩展（§5.2，2026-09-05 用户拍板，探针 examples/_bottom_family_probes/ 定稿）——
    # script_bottom（手账甜美）：BodoniModa 主标 76px + ✦✦✦ 点缀 + 斜体副标
    # （2026-09-14 微调批2 #18：字体 + 字号继承原 vogue_bottom，其余参数一概不动）
    'script_bottom': _cfg(
        mode='T', topology='bedrock_base', hero_zone='bottom_center', text_on_photo=True,
        layout='bottom',
        mat_bg='#111111', band_h=0,
        title_font='BodoniModa', title_size=76, title_color='#f5f5f5',
        title_spacing='.22em', bottom_ornament='stars',
        en_font='Georgia', sub_italic=True, meta_style='vogue_meta',
        tone_filter='saturate(1.05)',
    ),
    # cinzel_bottom（罗马碑刻）：CinzelBold 主标 + 两侧渐隐金线+金菱形点缀 + #efe6cf 副标
    'cinzel_bottom': _cfg(
        mode='T', topology='bedrock_base', hero_zone='bottom_center', text_on_photo=True,
        layout='bottom',
        mat_bg='#111111', band_h=0,
        title_font='CinzelBold', title_size=60, title_color='#f5f5f5',
        title_spacing='.3em', bottom_ornament='romann',
        en_font='Georgia', sub_color='#efe6cf', meta_style='vogue_meta',
        tone_filter='saturate(1.05)',
    ),
    'french_elegance': _cfg(
        photo_border='14px solid #ffffff',
        mode='T', topology='dual_poles', hero_zone='top_and_bottom', text_on_photo=True,
        mat_bg='#14110c', band_h=0,
        title_font='CormorantItalic', title_size=64, title_color='#f3ead9',
        en_font='PlayfairItalic', meta_style='italic', tone_filter='sepia(0.12) saturate(1.05)',
    ),
    'oriental_plain_paper': _cfg(
        mode='T', topology='right_wing', hero_zone='right_vertical', text_on_photo=True,
        mat_bg='#f2efe8', band_h=0,
        title_font='LXGWWenKai', title_size=56, title_color='#f4f1ea',
        en_font='SpaceMono', meta_style='mono_caps', tone_filter='sepia(0.1)',
    ),

    # ---------- E 装饰/齿孔（O 纹饰式，perimeter_orbit，text_on_photo 多数 False）----------
    'french_par_avion': _cfg(
        photo_border='14px solid #ffffff',
        mode='O', topology='perimeter_orbit', hero_zone='bottom_card', text_on_photo=False,
        mat_bg='#f4efe7', frame_inset=46, band_h=230,
        title_font='CormorantItalic', title_size=64, title_color='#2b3a4a',
        en_font='SpaceMono', meta_style='stamp_meta', svg_ornament='par_avion',
        tone_filter='sepia(0.12)',
    ),
    'art_deco_gatsby': _cfg(
        photo_border='14px solid #ffffff',
        mode='O', topology='perimeter_orbit', hero_zone='bottom_card', text_on_photo=False,
        mat_bg='#12262e', frame_inset=50, band_h=220,
        title_font='PlayfairItalic', title_size=67, title_color='#e9d9a8',
        en_font='SpaceMono', meta_style='stamp_meta', svg_ornament='gatsby_deco',
        tone_filter='saturate(1.05) contrast(1.05)',
    ),
    'nordic_meander': _cfg(
        mode='O', topology='perimeter_orbit', hero_zone='bottom_card', text_on_photo=False,
        mat_bg='#eef0ef', frame_inset=48, band_h=230,
        title_font='CinzelBold', title_size=64, title_color='#2b3130',
        en_font='SpaceMono', meta_style='mono_caps', svg_ornament='meander',
        tone_filter='saturate(0.9)',
    ),
    'film_rsx_sprocket': _cfg(
        mode='O', topology='perimeter_orbit', hero_zone='bottom_card', text_on_photo=False,
        mat_bg='#0c0a08', frame_inset=30, band_h=210,
        title_font='SpaceMono', title_size=58, title_color='#e8dfc8',
        en_font='SpaceMono', meta_style='cinema_meta', svg_ornament='sprocket',
        tone_filter='sepia(0.2) saturate(1.1)',
    ),

    # ===============================================================
    # 任务3 · 剩余 1 款（画廊框 × 色差；F / face_portrait / bottom_card / text_on_photo=False）
    # ===============================================================
    # 独立外框（outline_style）+ 文字带色差（band_bg 与大框 mat_bg 含蓄不同 → 文字带是独立文字框）。
    'gallery_frame_warm': _cfg(
        mat_bg='#ede1cc', band_bg='#e8d8c0', outline_style='inset:8px;border:2px solid #d8c9ae',
        frame_inset=26, band_h=205,
        title_font='SourceSerifHeavy', title_size=54, title_color='#33271a',
        en_font='SpaceMono', tone_filter='sepia(0.04) saturate(1.03)',
    ),

    # ===============================================================
    # 字体驱动段（原 5 款，2026-09-05 §2.1 配对表：<骨架词干>_<字体词干>；无新模板，
    # 复制骨架 config 改 title_font/title_size/字距。3 款书法款 title_size 降 10% 起步
    # ——书法字体行高偏大，fit_title_fs 收敛兜底）
    # 2026-09-14 微调批2：删 elegance_yeseva / oriental_zhuokai / film_xingkai /
    # warm_zhuokai_card 4 款 → 本段现役仅 1 款。
    # ===============================================================
    # 罗马碑刻×航空信笺：Marcellus × french_par_avion（顶栏+笺，O 纹饰式）
    'par_avion_marcellus': _cfg(
        photo_border='14px solid #ffffff',
        mode='O', topology='perimeter_orbit', hero_zone='bottom_card', text_on_photo=False,
        mat_bg='#f4efe7', frame_inset=46, band_h=230,
        title_font='Marcellus', title_size=64, title_color='#2b3a4a',
        en_font='SpaceMono', meta_style='stamp_meta', svg_ornament='par_avion',
        tone_filter='sepia(0.12)',
    ),
    # —— 2026-09-14 微调批2 删 4 款（用户拍板「第28/29/30/31 款删除」）——
    # 原条目：elegance_yeseva（YesevaOne×french_elegance）/ oriental_zhuokai（ZhuoKai×
    # oriental_plain_paper）/ film_xingkai（XingKai×film_rsx_sprocket）/ warm_zhuokai_card
    # （ZhuoKai×gallery_frame_warm）。对应 @font-face 常量/注入分支按口径④保留（死代码，
    # 清单见 docs/微调批2-设计.md §14.3）。
}

# 供 engine_v2 的 --genre choices 并入
MATTING_IDS = list(MATTING_CONFIGS)

# ===================================================================
# 蓝图原 id → 装裱款 id 的「纯别名」映射（2026-09-02 用户拍板；2026-09-05 删 4 条）
# ===================================================================
# 蓝图 28 套原概念 id 中 2 个未单独实现（french/gatsby），通过 --genre 直达时**纯别名**
# 映射到对应装裱款，复用其渲染模板，零重复模板。
# **不加入 MATTING_CONFIGS**（否则 len 变破坏现有断言/计数）；alias 是独立映射。
# 别名只影响 engine_v2 的分发；资源/出图用解析后的装裱款 config。
# 原 id 继承装裱款的语义（如 text_on_photo=False → 护脸款，绑 face_portrait）。
# 2026-09-05 真删除：chroma→chroma_passepartout / polaroid→polaroid_wide /
# victorian→victorian_gilt / stamp→swiss_perforated_stamp 4 条随目标款删除而删。
MATTING_ALIAS = {
    'french':    'french_par_avion',
    'gatsby':    'art_deco_gatsby',
}


if __name__ == '__main__':
    # 自检：字段全集 + 数量
    _req = ('mode', 'topology', 'hero_zone', 'text_on_photo', 'mat_bg', 'texture',
            'frame_inset', 'band_h', 'title_font', 'title_size', 'title_color',
            'en_font', 'meta_style', 'svg_ornament', 'tone_filter')
    bad = {g: [f for f in _req if f not in c] for g, c in MATTING_CONFIGS.items() if not all(f in c for f in _req)}
    assert len(MATTING_CONFIGS) == 13, f"config 数量应为 13，实际 {len(MATTING_CONFIGS)}"
    assert not bad, f"字段缺失: {bad}"
    assert len(MATTING_IDS) == 13, "MATTING_IDS 应为 13"
    # O 模式必须有 ornament；非 O 必须无
    for g, c in MATTING_CONFIGS.items():
        if c['mode'] == 'O':
            assert c['svg_ornament'], f"{g} 是 O 模式但缺 svg_ornament"
        else:
            assert not c['svg_ornament'], f"{g} 非 O 模式却含 svg_ornament"
    # MATTING_ALIAS：每个别名目标必须在 MATTING_CONFIGS；别名键不得与现有 set 重复。
    # 注：engine_v2 在分发前先解析别名（if genre in MATTING_ALIAS），故别名键还需与引擎 GENRE / METAPHOR_IDS / BLUEPRINT_IDS 保持互斥，
    # 否则会静默误路由到 matting。本模块保持解耦不 import 这些，互斥由 engine_v2 分发点负责（见 engine_v2 别名解析处注释）。
    for alias, target in MATTING_ALIAS.items():
        assert target in MATTING_CONFIGS, f"别名 {alias} 的目标 {target} 不在 MATTING_CONFIGS"
        assert alias not in MATTING_CONFIGS, f"别名 {alias} 不应是 MATTING_CONFIGS 的既有键"
    print(f"matting_configs OK · {len(MATTING_CONFIGS)} 款 · 字段全集 · 别名 {len(MATTING_ALIAS)} 条")
