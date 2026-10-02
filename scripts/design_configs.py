#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 新设计语言六款 + 彩活四款 + 构图三款 + 撕纸手帐（torn_journal） + 展览海报（exhibition_poster） · 设计语言族（design canonical）· 参数化 configs（19 款）
============================================================================
设计稿：docs/批量设计-新设计语言六款-设计.md（v3，探针定稿 = 实现契约；v3 修正三款：
pop_halftone 按 A 探针终图整版重写 / kinfolk_air 补顶部刊头带 / super_index 目录行改单行四栏）。
第 5 族（设计语言族），照蓝图补齐族先例：本文件只收 config，渲染在 design_engine.py。
不动 matting/metaphor/blueprint 三族任何字节（零回归最硬保障）。

彩活四款（2026-09-07，docs/批量设计-彩活四款-设计.md v2）：street_zine / duo_pop（方案 b：
照片原色，波普感全靠版面，禁 duotone）/ doodle_summer / collage_man（单人照限定）。
全部数值入 layout 键（含 duo_pop 12 圆点坐标表、P4 词池 24 词、洗牌 seed 规则、
P3 云朵/贴纸坐标）；模板不藏魔数。
§2 字体规范（2026-09-06 批）：本批新增恰好 3 个 @font-face 常量（_SS_HEAVY_CSS /
_SS_SERIF_MED_CSS / _CAVEAT_CSS，定义在 design_engine.py，照 _BODONI_CSS 按需注入先例）。
思源黑 Heavy 主标款（pop_halftone / super_index / retro_tv）入 font_guard 缺字预检
白名单（接入点 A，《字体驱动与缺字预检-设计.md》§3 先例）。
彩活四款（2026-09-07 批）楷体选型 ZhuoKaiKai 同入白名单，+ _QSSS1_CSS 第 4 个常量。

每款 config 字段（供 design_engine.render 使用）：
  mode          : 'DESIGN'（家族标记，**非分发键**——分发按 template_id；刻意避开装裱族
                  D 类语义〔装裱 D=文字压照片款，跨族同字母异义易误读〕）
  template_id   : 构建函数名（_tpl_pop_halftone / _tpl_kinfolk_air / _tpl_museum_frame /
                  _tpl_swiss_red_grid / _tpl_super_index / _tpl_retro_tv /
                  _tpl_street_zine / _tpl_duo_pop / _tpl_doodle_summer / _tpl_collage_man /
                  _tpl_branch_magazine / _tpl_pop_lichtenstein / _tpl_pop_press /
                  _tpl_torn_journal / _tpl_modern_spread / _tpl_cultural_journal）
  topology      : 绑定拓扑槽位（metadata；权威注册在 topology_registry.py）
  hero_zone     : 主标真实落区枚举（供 validate_layout_consistency 计算）
  text_on_photo : bool —— hero 文字是否压在照片上。
                  True（不护脸，需人工核）：swiss_red_grid（满幅）。
                  False（护脸）：pop_halftone（黑底贴纸款）/ kinfolk_air / museum_frame /
                  super_index / retro_tv。
  base_color    : 画布底色（hex；text_on_photo=False 款的 readability 落点亮度来源）
  tone_filter   : 照片 CSS filter（'' 无）
  fonts         : {'hero': 主标字体, 'emotion': 副标字体, 'data': 等宽数据字体}
  scale         : {'hero_px','lead_px','micro_px','hero_lh','hero_letter','hero_shadow'}
  palette       : {'primary': 底色, 'accent': 文字主色/强调, 'point': 点睛色}
  layout        : 毾款专属结构参数（halftone 斜角、swiss 蒙版参数、museum 双框色对、
                  super 刊头高、tv 故障偏移等）——**全部数值入 config，模板不藏魔数**。

title / sub / date / location 一律由 CLI 参数传入，**不硬编码演示文案**；仅装饰性固定
小字逐款标注（super 的 001/VOL.001、tv 的 SIG.01001101//CH.09 与 BROADCAST、
swiss 的 № 编号由参数派生〔确定性 seed，blueprint _derive 先例〕）。

§2 字体规范：本批新增恰好 3 个 @font-face 常量（_SS_HEAVY_CSS / _SS_SERIF_MED_CSS /
_CAVEAT_CSS，定义在 design_engine.py，照 _BODONI_CSS 按需注入先例）。
新款入库批（2026-09-16）追加 5 个：_PRATA_CSS / _SS_BOLD_CSS / _SS_REG_CSS /
_SS_SERIF_REG_CSS / _LXGW_REG_CSS（经 config.layout['extra_fonts'] 声明式注入，D-4/D-5；
路径盘上 os.path.exists 实测 ✓，见 docs/新款入库批-设计.md §2.6）。
思源黑 Heavy 主标款（pop_halftone / super_index / retro_tv）入 font_guard 缺字预检
白名单（接入点 A，《字体驱动与缺字预检-设计.md》§3 先例）。
"""

# ---- 共享默认（保证字段全集；每款按气质覆盖）----
_DEFAULT = {
    'mode': 'DESIGN',
    'template_id': '',
    'topology': '',
    'hero_zone': '',
    'text_on_photo': False,
    'base_color': '#f7f4ee',
    'tone_filter': '',
    'fonts': {'hero': 'SourceSerifHeavy', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
    'scale': {'hero_px': 45, 'lead_px': 18, 'micro_px': 16,
              'hero_lh': 1.1, 'hero_letter': '0.1em', 'hero_shadow': 'none'},
    'palette': {'primary': '#f7f4ee', 'accent': '#33393d', 'point': '#c8a86a'},
    'layout': {},
}


def _cfg(**kw):
    """基于默认填充一份完整 config，再按款覆盖。保证字段全集、少冗余。"""
    c = dict(_DEFAULT)
    c.update(kw)
    return c


# ===================================================================
# 设计语言 · 6 款（template_id / 拓扑 / hero_zone / text_on_photo / 配方气质）
# 数值均为 900×1200 基准像素；几何一律 int(round(v*fs))（design_engine._canvas_for）。
# ===================================================================
DESIGN_CONFIGS = {
    # ---------- 孟菲斯波点（§1.1 v3：黑底 #111 系 + 黄波点纹 + 四角青/粉/黄点缀块；
    #           粉+青双色边框照片（外粉内青，方正规整）；顶部斜贴纸 EN 标题块（粉底
    #           rotate -2° + 硬偏移青影，黄字字距拉开）；底部中文大字黄字思源黑 Heavy
    #           居中 + 粉/青双色硬偏移阴影；标题全落黑底区 → text_on_photo=False 护脸）----------
    'pop_halftone': _cfg(
        template_id='_tpl_pop_halftone', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=False,
        base_color='#111111', tone_filter='contrast(1.12)',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 62, 'lead_px': 20, 'micro_px': 20,
               'hero_lh': 1.15, 'hero_letter': '0.12em',
               'hero_shadow': '5px 0 0 #e8447a,-5px 0 0 #23c4a7'},
        palette={'primary': '#111111', 'accent': '#f5d327', 'point': '#f5d327'},
        layout={'dot_px': 4,            # 波点半径（radial-gradient 圆点）
                'dot_gap': 46,          # 波点阵列间距（background-size）
                'dot_color': '#f5d327', # 主波点色（黄）
                'dot_opacity': 0.9,
                # 四角点缀块（装饰，无文案）：青条 / 粉块 / 黄短条（探针 A：散布四角）
                'blocks': ({'color': '#23c4a7', 'w': 120, 'h': 14, 'x': 648, 'y': 120, 'rot': -6},
                           {'color': '#e8447a', 'w': 26, 'h': 26, 'x': 96, 'y': 210, 'rot': 12},
                           {'color': '#f5d327', 'w': 64, 'h': 10, 'x': 740, 'y': 300, 'rot': 0},),
                'photo_w': 726,         # 双色框照片框宽（#47：660×1.10）
                'photo_top': 250,       # 照片框顶（顶部给斜贴纸标题块留位）
                'photo_h': 726,         # 照片框高（#47：660×1.10）
                'frame_outer_color': '#e8447a',  # 外框（粉）
                'frame_inner_color': '#23c4a7',  # 内框（青）
                'accent_yellow': '#f5d327',      # 主黄（大标字/贴纸字；=palette.point 字面）
                'frame_outer_px': 10,   # 外框线（粉）
                'frame_gap_px': 8,      # 双框间留白（黑底透出）
                'frame_inner_px': 5,    # 内框线（青）
                'frame_shadow': '0 14px 30px rgba(0,0,0,.4)',  # 轻投影
                # 斜贴纸标题块（本款灵魂，v3 复活；--sub EN 黄字，贴纸可轻出画缘）
                'sticker_px': 40,       # EN 字号（Impact/Courier 系粗体）
                'sticker_letter': '0.18em',
                'sticker_top': 84,      # 块顶（黑底区上部）
                'sticker_pad_x': 34, 'sticker_pad_y': 14,   # 块内边距
                'sticker_max_w': 774,   # 贴纸 fit 容器宽（≈0.86W，允许轻出画缘）
                'sticker_rot': -2,      # 斜置角度（度）
                'sticker_dx': 10, 'sticker_dy': 10,         # 硬偏移青影偏移量
                'sticker_min_w': 320,   # 贴纸最小宽（sub 短时防退化成细条，min-width 兜底）
                'hero_left': 64,        # 主标左右安全内缩（居中排：left/right 对称内缩）
                'hero_bottom': 86,      # 主标距底（2026-09-15 微调批3 A#3：96→86 = ×0.90；单一纵锚，主标+meta 两行整体下移）
                },
    ),
    # ---------- 素白金线（§1.2 v3：米白极简大留白；顶部刊头带〔EN 刊名衬线 34px 字距 .35em
    #           全大写；2026-09-14 微调批2 #48 删小字行 NO./月份〕；照片窗 +10% 满；
    #           金色渐隐分界线；底部中文 29px 思源宋 Medium / EN 13px mono）----------
    'kinfolk_air': _cfg(
        template_id='_tpl_kinfolk_air', topology='face_portrait', hero_zone='bottom_card',
        text_on_photo=False,
        base_color='#f7f4ee', tone_filter='grayscale(.2)',
        fonts={'hero': 'SourceHanSerifMedium', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 29, 'lead_px': 13, 'micro_px': 20,
               'hero_lh': 1.5, 'hero_letter': '0.3em', 'hero_shadow': 'none'},
        palette={'primary': '#f7f4ee', 'accent': '#33393d', 'point': '#c8a86a'},
        layout={'head_en_px': 34,       # 大字行（EN 刊名 = --sub，衬线 34px 字距 .35em 全大写）
                'head_en_top': 70,      # EN 行 top（= 原 head_no_top 56 + head_en_gap 14；
                                        # 2026-09-14 微调批2 #48 删小字行后取绝对锚，EN 行位置零位移）
                'photo_inset_x': 68,    # 照片窗左右内缩（比标准窗 +10% 满）
                'photo_top': 186,
                'photo_h': 836,
                'photo_shadow': '0 18px 44px rgba(40,36,30,.18)',
                'line_px': 1,           # 金色渐隐线 1px（transparent→金→transparent）
                'line_gap': 24,         # 金线距照片底缘
                'line_inset_x': 150,    # 金线左右内缩（比照片窗更深，两端渐隐留白；随 fx 缩放）
                'line_fade': 18,        # 渐变站点：18% 处达全金、82% 起隐（% 保持相对）
                'text_bottom': 44,      # 底部文字带距底
                },
    ),
    # ---------- 馆签双框（§1.3：双线展签框；框色随图自动（确定性函数）；顶部信息条；
    #           底部文字块下移加深）----------
    'museum_frame': _cfg(
        template_id='_tpl_museum_frame', topology='matted_gallery', hero_zone='bottom_card',
        text_on_photo=False,
        base_color='#efeae0', tone_filter='grayscale(.15)',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 40, 'lead_px': 20, 'micro_px': 20,
               'hero_lh': 1.2, 'hero_letter': '0.32em', 'hero_shadow': 'none'},
        palette={'primary': '#efeae0', 'accent': '#1c2126', 'point': '#6f6244'},
        layout={'frame_inset': 34,      # 外框内缩
                'frame_outer_px': 3,    # 外框线
                'frame_gap_px': 2,      # 框间距留白（底色透出）
                'frame_inner_px': 2,    # 内框线
                'info_top': 58,         # 顶部信息条（mono 大写：左=date 右=location）
                'info_x': 74,
                'rule_top': 104,        # 信息条下分隔线
                'photo_top': 150, 'photo_x': 74, 'photo_bottom': 170,
                'photo_shadow': '0 14px 36px rgba(60,50,30,.25)',
                'hero_bottom': 76,      # 底部文字块下移（基线 76px）
                # 框色随图自动（_frame_palette 确定性）：暖调→描金，冷调→银灰
                'warm_color': '#b8955f', 'cool_color': '#8a8f98', 'warm_threshold': 12,
                },
    ),
    # ---------- 红格瑞士（§1.4：去色满幅 + 红细网格径向蒙版（transparent 在中心 40%，
    #           方向勿反）；左下白衬线主标 + 角标 №/日期）----------
    'swiss_red_grid': _cfg(
        template_id='_tpl_swiss_red_grid', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#101013', tone_filter='grayscale(1) contrast(1.08) brightness(.96)',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        scale={'hero_px': 104, 'lead_px': 44, 'micro_px': 22,
               'hero_lh': 1.06, 'hero_letter': '0.02em',
               'hero_shadow': '0 2px 14px rgba(0,0,0,.55)'},
        palette={'primary': '#101013', 'accent': '#c41c1c', 'point': '#f3d9d9'},
        layout={'grid_px': 90,          # 网格间距
                'grid_line_px': 1,      # 网格线宽
                'grid_alpha': 0.4,      # rgba(196,28,28,.4)
                'mask_cx': 50, 'mask_cy': 46,   # 椭圆中心
                'mask_ex': 62, 'mask_ey': 55,   # 椭圆半径
                'mask_transparent': 40, # 中心 40% 无网格（方向勿反——探针返工教训）
                'mask_full': 92,        # 92% 全显
                'hero_left': 46, 'hero_bottom': 96,
                'en_gap': 6,            # EN 副标与主标间距
                'corner_x': 46, 'corner_top': 40,  # 角标内缩/距顶
                'date_px': 20,          # 右上白日期
                'no_max': 24,           # № 编号上限（seed 派生 01~24，结构标签）
                },
    ),
    # ---------- 刊头索引（§1.5：奶白刊头带 330px + 满幅照片；思源黑 Heavy 刊名 +
    #           " :" 冒号贴上沿；v3 单行四栏目录行——"编号+值"同行，值过长 fit 缩字号，
    #           缺省 "—"）----------
    'super_index': _cfg(
        template_id='_tpl_super_index', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#efeae0', tone_filter='contrast(1.04)',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'SourceHanSerifMedium', 'data': 'SpaceMono'},
        scale={'hero_px': 92, 'lead_px': 19, 'micro_px': 20,
               'hero_lh': 1.1, 'hero_letter': '0.01em', 'hero_shadow': 'none'},
        palette={'primary': '#efeae0', 'accent': '#141414', 'point': '#5c5648'},
        layout={'band_h': 330,          # 刊头带高（随 fs 缩放，横版边界用例显式核）
                'head_x': 48, 'head_top': 44,
                'colon_px': 40,         # " :" 冒号贴字面上沿
                'colon_va': '0.62em',
                'num_px': 34,           # 右上 001（Courier 系 mono Bold；固定装饰）
                'num_top': 64,
                'sub_top': 168,         # 副标行
                'dir_top': 214,         # 四栏目录行（v3 单行结构："编号+值"同行，20px 思源宋 Medium，lh 1.6）
                'dir_gap': 26,
                'dir_x': 48,
                'dir_px': 20,           # 目录行字号（v3 显式入 config；随 fs 缩放）
                'dir_default': '—',     # 栏内容缺省（禁硬编码目录词）
                'rule_color': '#c9c2b2',
                'rule_px': 1.5,         # 目录行下细分隔线
                'rule_lift': 26,        # 分隔线距刊头带底的抬升量
                'foot_px': 20,          # 照片右下 白 mono 日期 · VOL.001（VOL 固定装饰；§2 小字 20px 起步）
                'foot_bottom': 36, 'foot_right': 48,
                },
    ),
    # ---------- 复古电视（§1.6：深炭底 + 大圆角照片窗；左上手写英文 Caveat-Bold；
    #           右下主标思源黑 Heavy + RGB 故障错位 text-shadow（单元素多层，禁三层
    #           span 叠法）；故障带 + 二进制小字（固定装饰文案））----------
    'retro_tv': _cfg(
        template_id='_tpl_retro_tv', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=False,
        base_color='#17171c', tone_filter='saturate(1.15) contrast(1.05)',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'CaveatBold', 'data': 'SpaceMono'},
        scale={'hero_px': 88, 'lead_px': 30, 'micro_px': 20,
               'hero_lh': 1.05, 'hero_letter': '0.06em',
               'hero_shadow': '0 6px 18px rgba(0,0,0,.6)'},
        palette={'primary': '#17171c', 'accent': '#fdf6ec', 'point': '#f3b6c3'},
        layout={'photo_top': 120, 'photo_x': 56, 'photo_h': 820,
                'radius': 30,           # 大圆角
                'border_px': 5, 'border_color': '#2c2c34',
                'photo_shadow': '0 16px 44px rgba(0,0,0,.5)',
                'sub_top': 52, 'sub_left': 56,   # 左上手写英文（--sub）
                # 右上红/黄圆点装饰（固定件；落照片窗上方深底区，不被照片盖住）
                'dot1': {'right': 70, 'top': 56, 'd': 22, 'color': '#e8443f'},
                'dot2': {'right': 96, 'top': 92, 'd': 12, 'color': '#f5d327'},
                'hero_right': 56, 'hero_bottom': 64,
                'glitch_dx': 5,         # RGB 故障错位（-dx,-dy 红 / +dx,+dy 青；单元素多层 shadow）
                'glitch_dy': 3,
                'glitch_red': 'rgba(232,68,63,.8)', 'glitch_cyan': 'rgba(55,216,200,.7)',
                'glitch_line_w': 400, 'glitch_line_h': 3,   # 故障带红青渐变细线
                'sig_px': 20,           # SIG.01001101 // CH.09（固定装饰文案）
                'broadcast_bottom': 44, # 左下 BROADCAST · date（mono）
                },
    ),
    # =================================================================
    # 彩活四款（2026-09-07，docs/批量设计-彩活四款-设计.md §1 终值 = 实现契约，不得偏离）
    # =================================================================
    # ---------- 街头小志（§1.1：照片满幅原色 + 顶部渐变黑带内 EN 刊名红块白字 + 黄字副行 +
    #           黄贴纸 editors pick ✂ + 底部右对齐中文大字楷体白字 + VOL/日期青块 +
    #           黄箭头 ➜ rotate(-45°) 指右上 + 红标"看這裡!"。hero=bottom_right，
    #           text_on_photo=True（标题压照片下部，需人工核，不护脸）；
    #           拓扑注册填 bottom_right 槽〔v2 修：原 bedrock_base 与 hero 落区不符〕）----------
    'street_zine': _cfg(
        template_id='_tpl_street_zine', topology='bottom_right', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#1a1a1a', tone_filter='',
        fonts={'hero': 'ZhuoKaiKai', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 96, 'lead_px': 20, 'micro_px': 20,
               'hero_lh': 1.05, 'hero_letter': '0.04em',
               'hero_shadow': '-4px 4px 0 #e8443f,-8px 8px 0 rgba(0,0,0,.45)'},
        palette={'primary': '#1a1a1a', 'accent': '#e8443f', 'point': '#ffd23f'},
        layout={'band_px': 55, 'band_color': 'rgba(0,0,0,.55)',  # 顶部渐变黑带（180deg→transparent）
                'band_pad_x': 30, 'band_pad_y': 26,
                'name_px': 74, 'name_pad_x': 18, 'name_pad_y': 2,   # EN 刊名红块白字（#e8443f 底）
                'name_letter': '.02em',
                'subline_px': 26, 'subline_gap': 8, 'subline_letter': '.1em',
                'subline_text': '本週注目 ★ 街頭速報',     # 固定装饰文案（繁体；随 title_font 预检，
                                                            # fg_texts 声明；以 title_font 渲染）
                # font_guard 预检范围声明（设计稿 §2）：参与缺字预检的装饰文案 layout 键
                'fg_texts': ('subline_text', 'mark_text'),
                'sticker_top': 196, 'sticker_left': 30, 'sticker_px': 22,
                'sticker_pad_x': 14, 'sticker_pad_y': 10, 'sticker_rot': -6,
                'sticker_text': 'editors pick ✂',           # 固定装饰文案（装饰小字）
                'hero_right': 26, 'hero_bottom': 36,        # 底部右对齐（v2 调整：右移）
                'vol_px': 20, 'vol_gap': 10, 'vol_letter': '.18em',
                'vol_text': 'VOL.12 · STREET EDITION',      # 固定装饰文案
                'date_px': 20, 'date_rot': 1.5, 'date_color': '#083b32', 'date_bg': '#23c4a7',
                'arrow_px': 52, 'arrow_bottom': 170, 'arrow_left': 60, 'arrow_rot': -45,
                'mark_bottom': 250, 'mark_left': 110, 'mark_px': 19, 'mark_rot': -8,
                'mark_text': '看這裡!',                      # 固定装饰文案（繁体；fg_texts 预检，
                                                             # 以 title_font 渲染）
                'name_font': 'SourceHanSansHeavy',  # EN 刊名红块 = 黑体 Heavy（设计稿 §1.1 契约）
                },
    ),
    # ---------- 双色波普（§1.2 方案 b：照片原色满幅〔contrast(1.05) saturate(1.05)，
    #           **禁 duotone 滤镜链**——a 方案实证人像翻车〕+ 顶部三色跑马条 15px +
    #           底部红色文字块 270px（白字大标 100px 黑影 + EN Impact 黄字 40px + 日期行
    #           mono 20px）+ 12 颗无规律波普圆点（坐标写死 SVG circle，确定性）+
    #           右下大圆点青底 120px 黄描边环 14px。hero=bottom_center，
    #           text_on_photo=True（底部红块 270px+圆点实际覆盖满幅照片下部，需人工核）
    #           2026-09-14 微调批2 #54：条 14→15px（+10%）、块 300→270px（−10%）+
    #           中英文标题同步下移 6%（主标 214→201 / EN 180→169；meta 60 不动））----------
    'duo_pop': _cfg(
        template_id='_tpl_duo_pop', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#1b6fae', tone_filter='contrast(1.05) saturate(1.05)',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 100, 'lead_px': 40, 'micro_px': 20,
               'hero_lh': 1.0, 'hero_letter': '0.01em',
               'hero_shadow': '6px 6px 0 rgba(0,0,0,.28)'},
        palette={'primary': '#1b6fae', 'accent': '#e8443f', 'point': '#ffd23f'},
        layout={'bar_px': 15,          # 顶部三色跑马条高（#54：14×1.10 → 15）
                'bar_colors': ('#ffd23f', '#e8443f', '#23c4a7'),  # 各 40px repeating 90deg
                'bar_seg': 40,
                'block_px': 270,       # 底部红色文字块高（#e8443f；#54：300×0.90）
                'hero_bottom': 201, 'hero_left': 48,   # #54 同步下移 6%（214×0.94）
                'en_bottom': 169, 'en_left': 52, 'en_px': 40, 'en_letter': '.06em',   # #54（180×0.94）
                'meta_bottom': 60, 'meta_left': 52, 'meta_px': 20, 'meta_letter': '.22em',
                'meta_suffix': 'DUOTONE POP SERIES',   # 固定装饰文案（EN 词头，date 参数化）
                # 12 颗无规律波普圆点（v3 定稿数量；坐标写死 SVG circle，确定性：
                # 同图同点；cx/cy 为 900×300 viewBox 基准，rx=r，stroke 空=纯色）
                'dots': ({'cx': 90, 'cy': 60, 'r': 26, 'fill': '#ffd23f', 'opacity': .85},
                         {'cx': 230, 'cy': 200, 'r': 14, 'fill': '#23c4a7', 'opacity': .9},
                         {'cx': 420, 'cy': 90, 'r': 38, 'fill': '#f7f4ee', 'opacity': .7},
                         {'cx': 560, 'cy': 230, 'r': 20, 'fill': '#ffd23f', 'opacity': .8},
                         {'cx': 700, 'cy': 50, 'r': 12, 'fill': '#1b6fae', 'opacity': .85},
                         {'cx': 820, 'cy': 180, 'r': 30, 'fill': '#23c4a7', 'opacity': .65},
                         {'cx': 330, 'cy': 260, 'r': 10, 'fill': '#f7f4ee', 'opacity': .8},
                         {'cx': 640, 'cy': 140, 'r': 16, 'fill': '#e8443f', 'opacity': .55,
                          'stroke': '#fff', 'stroke_w': 3},
                         {'cx': 150, 'cy': 250, 'r': 8, 'fill': '#1b6fae', 'opacity': .8},
                         {'cx': 300, 'cy': 40, 'r': 18, 'fill': '#23c4a7', 'opacity': .5,
                          'stroke': '#fff', 'stroke_w': 2},
                         {'cx': 500, 'cy': 180, 'r': 9, 'fill': '#ffd23f', 'opacity': 1},
                         {'cx': 760, 'cy': 120, 'r': 24, 'fill': '#f7f4ee', 'opacity': .55}),
                'big_dot': {'d': 120, 'ring': 14, 'color': '#23c4a7',
                            'ring_color': 'rgba(255,210,63,.9)', 'bottom': 96, 'right': 48},
                },
    ),
    # ---------- 涂鸦夏日（§1.3：照片洗白 + 白色上下渐隐 + 中文大标题楷体 #2e5e3f 92px
    #           （left calc 基点 -5%，标题完整在画面内）rotate(-2°) 白描影+绿投影 +
    #           EN 贴纸右下（白底 .92 橘字 26px 左黄边条 4px rotate -3°）+ 云朵三枚
    #           （top 250/180/296，left 均 calc(x - 5%)）+ 橘红虚线飞镖箭头 SVG + 太阳 SVG +
    #           左上黄胶带 + 底部固定文案。hero=bottom_center，text_on_photo=True
    #           （标题/固定文案/EN 贴纸落洗白照片的渐隐带上=压照片，探针定稿语义，需人工核））----------
    'doodle_summer': _cfg(
        template_id='_tpl_doodle_summer', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#f7f7f2', tone_filter='saturate(.82) brightness(1.1) contrast(.94)',
        fonts={'hero': 'ZhuoKaiKai', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 92, 'lead_px': 26, 'micro_px': 17,
               'hero_lh': 1.12, 'hero_letter': '0.02em',
               'hero_shadow': '0 2px 0 #fff,3px 5px 10px rgba(46,94,63,.25)'},
        palette={'primary': '#f7f7f2', 'accent': '#2e5e3f', 'point': '#e07a3f'},
        layout={'fade_stops': ((0, 'rgba(255,255,255,.5)'), (30, 'rgba(255,255,255,0)'),
                               (62, 'rgba(255,255,255,0)'), (88, 'rgba(236,244,234,.88)')),
                'hero_top': 66, 'hero_left_base': 60, 'hero_left_pct': '-5%',  # calc(60px-5%)
                'hero_rot': -2,
                'en_bottom': 120, 'en_right': 36, 'en_px': 26, 'en_rot': -3,
                'en_pad_x': 16, 'en_pad_y': 8, 'en_bg': 'rgba(255,255,255,.92)',
                'en_border_left': 4, 'en_border_color': '#f2b134',
                'arrow_top': 60, 'arrow_right': 40, 'arrow_w': 220, 'arrow_h': 150,
                'sun_bottom': 250, 'sun_left': 60, 'sun_px': 120,
                'tape_top': 0, 'tape_left': 40, 'tape_w': 110, 'tape_h': 30, 'tape_rot': -4,
                # 云朵三枚（v2+1：大云 top 250 + 小云 top 180 + 微云 top 296；left 均 calc(x-5%)）
                'clouds': ({'top': 250, 'left': 46, 'w': 150, 'h': 90, 'op': .9},
                           {'top': 180, 'left': 150, 'w': 90, 'h': 54, 'op': .85},
                           {'top': 296, 'left': 20, 'w': 70, 'h': 42, 'op': .8}),
                'foot_px': 24, 'foot_bottom': 96, 'foot_letter': '.3em',
                'foot_text': '綠野 · 晚風 · 逃跑計畫',      # 固定装饰文案（繁体；随 title_font 预检，
                                                            # fg_texts 声明；以 title_font 渲染）
                'fg_texts': ('foot_text',),                 # font_guard 预检范围声明（设计稿 §2）
                'meta_px': 17, 'meta_bottom': 46, 'meta_letter': '.24em',
                'meta_suffix': 'SKETCH DIARY',              # 固定装饰文案（date 参数化）
                },
    ),
    # ---------- 杂拼人物（§1.4 v3 融合版：底 #f3efe6 + 全高文字墙（§0.5 三层词池：
    #           款格词 A+B 24 词 + 真实元数据词 + --words 用户词；seed=照片内容哈希洗牌
    #           〔实现=读盘字节 md5，design_engine._photo_seed；非 mtime 防重渲漂移，
    #           换路径/复制渲染布局不变〕；
    #           五档字号 26/34/44/58/72；四类形态：竖排 14%/斜置 10%/空心 6%/反白 6%/常规 64%）
    #           + 蛋形窗 605×691 居中 top 190 + 顶部红标 EN + 全元素融合（v3 定稿 11 件装饰）
    #           + 虚线箭头+看這裡!! 在蛋框左下（v3 终版：仅一条箭头指蛋框，右侧旧箭头已删）
    #           + 底部中文大标黑体 Heavy 76px 黑字红影。hero=bottom_center，
    #           text_on_photo=False（蛋窗+bottom 文字=护脸）；**单人照限定**——多人照质检提示换款）----------
    'collage_man': _cfg(
        template_id='_tpl_collage_man', topology='face_portrait', hero_zone='bottom_center',
        text_on_photo=False,
        base_color='#f3efe6', tone_filter='',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'SpaceMono', 'data': 'SpaceMono'},
        scale={'hero_px': 76, 'lead_px': 22, 'micro_px': 18,
               'hero_lh': 1.0, 'hero_letter': '0.01em',
               'hero_shadow': '3px 3px 0 #d33'},
        palette={'primary': '#f3efe6', 'accent': '#111111', 'point': '#d33'},
        layout={
            # §0.5 款格词（A 展览先锋 12 + B 市井烟火 12，共 24；①层选词不指称照片内容；
            # 调整词表属微调通道——改 config 即生效，无需动引擎）
            'words_a': ('BEHOLD', '目击', '侧写', '旁白', 'NOW', '走!!', '無限', '大字報',
                        '凝視', '参与者', '记录', '艺术家'),   # 2026-09-25 死词中性化：探针原型词"型不设防"→凝視（同族艺术词）
            'words_b': ('冰棍', '汽水', '巷口', '老冰柜', '廣播', '售罄', '慢走', '夏日限定',
                        '街角', '偶遇', '快门', '城市'),
            'wall_top': 26, 'wall_lh': 1.35, 'wall_opacity': .92, 'wall_word_gap': 8,
            'wall_margins': 14,     # 词间距 margin:0 14px
            'wall_sizes': (26, 34, 44, 58, 72),     # 五档字号
            'wall_colors': ('#d33', '#1a1a1a', '#666'),
            # 形态四类占比（设计语义）：竖排 14% / 斜置 10% / 空心 6% / 反白 6% / 常规 64%
            'wall_ratio': {'vertical': .14, 'tilt': .10, 'outline': .06, 'inverse': .06},
            'wall_tilt_max': 10,    # 斜置 ±5–10°
            'wall_max_h': 200,      # 竖排 max-height（探针口径）
            'egg_w': 605, 'egg_h': 691, 'egg_top': 200,   # egg_top：#56 下移 5%（190×1.05 → 200）
            'egg_radius': '50% 50% 46% 54%/56% 44% 56% 44%',
            'egg_border': 10, 'egg_shadow': '0 24px 60px rgba(0,0,0,.35)',
            'tag_top': 120, 'tag_px': 22, 'tag_rot': -3, 'tag_letter': '.3em',
            # 全元素融合（v3 定稿 11 件；坐标 900×1200 基准，随 fs 缩放）
            'elems': (
                {'kind': 'tape',    'top': 0,    'left': 60,  'w': 120, 'h': 34, 'rot': -4},
                {'kind': 'halftone_red',   'top': 130,  'right': 24, 'w': 180, 'h': 180, 'rot': 8, 'op': .45, 'cell': 12},
                {'kind': 'halftone_blue',  'bottom': 20, 'left': 16,  'w': 170, 'h': 170, 'rot': -5, 'op': .4, 'cell': 11},
                {'kind': 'sticker', 'top': 150,  'left': 44,  'rot': -7, 'text': 'NEW ✦',
                 'bg': '#ffd23f', 'color': '#111', 'px': 18, 'pad_x': 14, 'pad_y': 8, 'shadow': '3px 3px 0 rgba(0,0,0,.3)'},
                {'kind': 'stamp_red',  'top': 340,  'left': 30, 'rot': -6, 'text': 'APPROVED', 'px': 15, 'color': '#d33'},
                {'kind': 'sticker', 'bottom': 340, 'right': 36, 'rot': 5, 'text': '限定 →',
                 'bg': '#1a1a1a', 'color': '#ffd23f', 'px': 17, 'pad_x': 12, 'pad_y': 7, 'shadow': ''},
                {'kind': 'stamp_blue', 'bottom': 430, 'right': 30, 'rot': 5, 'text': 'CHECK ✓',
                 'px': 15, 'color': '#1b6fae', 'bg': 'rgba(243,239,230,.7)'},
                {'kind': 'tape',    'bottom': 330, 'right': 60, 'w': 110, 'h': 30, 'rot': -6},
                {'kind': 'go',      'bottom': 470, 'right': 44, 'rot': 8, 'text': 'GO!!', 'px': 30},
                {'kind': 'halftone_red',   'bottom': 240, 'right': 20, 'w': 150, 'h': 150, 'rot': -5, 'op': .4, 'cell': 11},
                {'kind': 'walk',    'bottom': 150, 'left': 40, 'rot': -3, 'text': 'WALK THIS WAY ↑↓', 'px': 16},
            ),
            # 虚线箭头+看這裡!! 在蛋框左下（v3 终版：仅一条，指向蛋框；黑虚线 rotate(-30°)）
            'arrow_bottom': 200, 'arrow_left': 96, 'arrow_w': 150, 'arrow_h': 100, 'arrow_rot': -30,
            'mark_bottom': 158, 'mark_left': 60, 'mark_px': 18, 'mark_rot': -6,
            'mark_bg': '#e8443f',
            'mark_text': '看這裡!!',     # 固定装饰文案（繁体；随所在款 title_font 预检，
                                         # fg_texts 声明；hero=SourceHanSansHeavy 本就为渲染字体）
            'fg_texts': ('mark_text',),  # font_guard 预检范围声明（设计稿 §2）
            'hero_bottom': 108,
            'meta_px': 18, 'meta_bottom': 56, 'meta_letter': '.26em',
            'meta_suffix': '日常观察展',         # 款固定文案（§1.4）；2026-09-25 死词中性化：
                                                 # 探针原型展名"型不设防城市展"与任意照片无关（图下方 date · 行）
            },
    ),
    # =================================================================
    # 构图三款（2026-09-08，docs/批量设计-构图三款-设计.md §1 终值 = 实现契约，不得偏离；
    # 数值以探针源码为参数真值——branch_magazine 探针终版 HTML（branch_折枝杂志__*.html，
    # 与 _gen_v5.py A4 段同源分叉）与 _gen_popart_c.py（pop02c/pop04c + pop04d 渐隐）。
    # fg_texts 支持新形态 dict {key: font_family}：按文案自身 font 逐字 cmap 预检
    # （设计稿 §0.5 覆盖口径），tuple 旧形态（随 title_font）彩活四款继续沿用）
    # =================================================================
    # ---------- 折枝杂志（§1.1：米白纸底 #f6f2ea + 双 radial 纸纹 + 左上文字块
    #           （黑体 Heavy 88px + EN Courier 24px + 红杠 72×3 + 两行宋体固定文案）+
    #           右上竖排小字 + 花枝 SVG（坐标表写死 branch_paths）+ 双层照片窗
    #           （外 760×760 只裁左下；内窗 676×676 rotate(-8°) right:30——A4 源码
    #           勘误值，见 layout 注；img rotate(8°)
    #           scale(1.18) object-position center 30%）。
    #           hero=bottom_right 槽（文字块+竖排小字+花枝全落留白区），
    #           text_on_photo=False 护脸（照片在独立斜切窗内）。
    #           无日期行、无红章（v5 终版用户拍板删除））----------
    'branch_magazine': _cfg(
        template_id='_tpl_branch_magazine', topology='bottom_right', hero_zone='bottom_center',
        text_on_photo=False,
        base_color='#f6f2ea', tone_filter='saturate(.94) contrast(1.02)',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'Courier New', 'data': 'Courier New'},
        scale={'hero_px': 88, 'lead_px': 22, 'micro_px': 20,
               'hero_lh': 1.12, 'hero_letter': '.02em', 'hero_shadow': 'none'},
        palette={'primary': '#f6f2ea', 'accent': '#22211e', 'point': '#b3442f'},
        layout={
            # 双 radial 纸纹（探针 GRAIN 原样；装饰无文案）
            'grain': ('radial-gradient(circle at 20% 12%, rgba(214,196,150,.35), transparent 42%),'
                      'radial-gradient(circle at 85% 88%, rgba(180,160,120,.28), transparent 40%)'),
            # 左上文字块（title 经 fit_title_fs；fit 容器宽=探针版面可用宽，长 title 缩档一行）
            # §1.1 勘误（2026-09-08 实现核对）：文字块/窗坐标以 _gen_v5.py A4 段（设计稿
            # §0.5 指认的参数真值+探针终图 v5_A4）为准——§1.1 原数值抄自更早的
            # branch_折枝杂志__*.html（21:20 终版，无竖排小字版本），与 A4 终图不符
            # （top80/290/346/390+窗 right:-20 会使竖排小字被窗右上角裁断，实测已复现）
            'title_top': 64, 'title_left': 56, 'title_fit_w': 714,
            'en_top': 248, 'en_left': 58, 'en_px': 24, 'en_letter': '.34em',
            'en_color': '#9a8a68', 'en_fit_w': 640,
            'rule_top': 310, 'rule_left': 58, 'rule_w': 72, 'rule_h': 3,
            # 两行宋体固定文案（繁体「為」随自身 font=思源宋 Heavy 预检；fg_texts dict 形态）
            'kengei_top': 348, 'kengei_left': 58, 'kengei_px': 23,
            'kengei_letter': '.18em', 'kengei_lh': 1.75, 'kengei_color': '#6f6a5c',
            'kengei_l1': '一枝探出瓶外', 'kengei_l2': '余幅皆為留白',   # 固定装饰文案
            # 右上竖排小字（固定装饰文案）
            'vtext_top': 70, 'vtext_right': 50, 'vtext_px': 24, 'vtext_letter': '.4em',   # right 64→50（微调批3 A#1b：右移 14px，脱离内窗叠压）
            'vtext_color': '#8a9a7b',
            'vtext': '折枝入畫 · 餘幅皆白',                              # 固定装饰文案
            # 花枝 SVG（297×285 @top146/right230，viewBox 0 0 330 300；坐标表写死，
            # 主枝曲线+叶 4 片+花头大+花苞 5 颗+枝尾 2 小苞，探针 A4 终版原样）
            'branch_top': 146, 'branch_right': 230, 'branch_w': 297, 'branch_h': 285,
            'branch_paths': (
                {'d': 'M30 270 Q110 210 210 120 Q260 78 300 40', 'stroke': '#8a9a7b',
                 'sw': 6, 'fill': 'none'},
                {'d': 'M118 200 Q78 186 64 148 Q108 158 118 200 Z', 'fill': '#8a9a7b', 'op': .85},
                {'d': 'M150 172 Q186 158 198 122 Q156 128 150 172 Z', 'fill': '#7d8f70', 'op': .75},
                {'d': 'M212 116 Q246 100 256 66 Q218 74 212 116 Z', 'fill': '#8a9a7b', 'op': .8},
                {'d': 'M96 232 Q60 238 34 262 Q76 262 96 232 Z', 'fill': '#7d8f70', 'op': .6},
                {'cx': 300, 'cy': 40, 'r': 17, 'fill': '#d98a94'},
                {'cx': 322, 'cy': 24, 'r': 10, 'fill': '#e8b0b6'},
                {'cx': 278, 'cy': 20, 'r': 8, 'fill': '#d98a94'},
                {'cx': 316, 'cy': 58, 'r': 8, 'fill': '#e8b0b6'},
                {'cx': 242, 'cy': 92, 'r': 7, 'fill': '#d98a94', 'op': .9},
                {'cx': 264, 'cy': 70, 'r': 6, 'fill': '#e8b0b6', 'op': .8},
                {'cx': 222, 'cy': 130, 'r': 5, 'fill': '#d98a94', 'op': .7},
                {'cx': 60, 'cy': 252, 'r': 6, 'fill': '#e8b0b6', 'op': .7},
                {'cx': 46, 'cy': 234, 'r': 4, 'fill': '#d98a94', 'op': .6},
            ),
            # 双层照片窗（外裁剪容器只裁左下；内窗 rotate -8°；
            # §1.1 勘误：以 A4 源码为准 win(bottom=110, right=30, size=676)——
            # 「right -20 临界值」属 §1.1 原文与 §0.5 真值文件的混抄，A4 段无此参数；
            # 实测 §1.1 数值会裁断竖排小字与窗右上角）
            # 2026-09-14 微调批2 #57：内窗 +10%（676→744）；外容器仅尺寸随动 760→828
            # （保 x 轴 54px 裁剪缓冲）；内窗上移 5%（底部锚 30→55 = 顶边 504 的 5%）——
            # win_outer_bottom 保持 −10（外容器跟随位移会使内窗绝对位移翻倍成 50px）。
            # 2026-09-15 微调批3 A#1a：外容器再放大 828→864（装下 rotate(−8°) 包围盒 840.3px，
            # 顶端不再被裁 19.15px）；内窗锚定外容器右/下边 → 只长大不位移（绝对位置零变化）。
            'win_outer_w': 864, 'win_outer_h': 864, 'win_outer_bottom': -10,
            'win_outer_right': 0,
            'win_w': 744, 'win_h': 744, 'win_bottom': 55, 'win_right': 30,   # #57（+10% / 上移 5%）
            'win_rot': -8, 'win_border': 14, 'win_border_color': '#f6f2ea',
            'win_outline': '1px solid rgba(90,80,60,.25)',
            'win_shadow': '-18px 18px 44px rgba(40,36,30,.28)',
            'img_rot': 8, 'img_scale': 1.18, 'img_pos': 'center 30%',
            # 横版覆盖（H<W 时生效，变更记录 2026-09-09 横版人工核补账）：横版画布矮，
            # 窗顶抬升会叠压竖排小字尾字/花枝下段——竖排小字上移 34px、花枝上移 50px+
            # 左移 70px+缩 10%；竖版（H>=W）坐标零改动
            'landscape_overrides': {'vtext_top': 36, 'branch_top': 96,
                                    'branch_right': 300, 'branch_w': 267, 'branch_h': 257},
            # fg_texts dict 形态：按文案自身 font 逐字预检（设计稿 §0.5）
            'fg_texts': {'kengei_l1': 'SourceSerifHeavy', 'kengei_l2': 'SourceSerifHeavy',
                         'vtext': 'SourceSerifHeavy'},
            },
    ),
    # ---------- 波普宣言（§1.2：黄底 #ffcc00 Ben-Day 圆点 + 内框 4px #111 + 原色照片窗
    #           （top 78/侧 24/高 76%，contrast 1.06 saturate 1.08 禁黑白——v2 用户拍板
    #           原色版）+ 大红爆炸星 148px 破界压照片底缘（clip-path 十角星 rotate -8°，
    #           内嵌 BebasNeue WOW!/POP!；**有意构图，保留**）+ 漫画对话框（白底黑边
    #           椭圆 rotate 4°，LXGWWenKai bold 17px {title}/太可愛了！）+ 底部黑条
    #           （SourceSerifHeavy 28px 黄字 title + Courier 11px 白字 meta）+ 黑条星群
    #           12 颗（8 锚位贯穿/两层错落/11-44px/四色轮换；±35° 转角 seed=7 **预计算**
    #           写死 stars 表，引擎内不跑 random）。
    #           hero=bottom_center，text_on_photo=True（星/星群破界压照片底缘，需人工核）。
    #           pop02c 探针移植（D:\dsh\render_popart_2_4_merged.py 血统，900×1200 直出））----------
    'pop_lichtenstein': _cfg(
        template_id='_tpl_pop_lichtenstein', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#ffcc00', tone_filter='contrast(1.06) saturate(1.08)',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'Courier New'},
        scale={'hero_px': 28, 'lead_px': 17, 'micro_px': 11,
               'hero_lh': 1.2, 'hero_letter': '.14em', 'hero_shadow': 'none'},
        palette={'primary': '#ffcc00', 'accent': '#111111', 'point': '#ff2d55'},
        layout={
            'frame_pad': 18, 'frame_border': 4, 'frame_color': '#111111',
            # Ben-Day 圆点铺底（radial 3.5px/#111 2.8px/15px 网格/opacity .15）
            'dot_px': 3.5, 'dot_inner': 2.8, 'dot_gap': 15, 'dot_opacity': .15,
            'dot_color': '#111111',
            # 原色照片窗（object-position:top 探针口径；照片顶对齐）
            'photo_top': 78, 'photo_side': 24, 'photo_h_pct': 76, 'photo_border': 4,
            'photo_pos': 'top',
            # 大红爆炸星（破界压照片底缘：top 936 = 中心 y 1010 - 148/2；有意构图）
            'star_px': 148, 'star_top': 936, 'star_left': 31, 'star_rot': -8,
            'star_color': '#ff2d55', 'star_border': '#111111',
            'star_shadow': '3px 4px 0 rgba(17,17,17,.9)',
            'star_clip': ('polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,'
                          '21% 91%,32% 57%,2% 35%,39% 35%)'),
            'star_text': 'WOW!', 'star_text2': 'POP!',
            'star_text_px': 24, 'star_text2_px': 14,
            # 漫画对话框（白底 3.5px 黑边圆角 50%；bub_max_w：长文案换行兜底，缺省不触）
            'bub_top': 17, 'bub_right': 21, 'bub_border': 3.5, 'bub_pad_y': 18,
            'bub_pad_x': 21, 'bub_rot': 4, 'bub_shadow': '4px 6px 0 #111111',
            'bub_px': 17, 'bub_lh': 1.3, 'bub_max_w': 420,
            'bubble_text': '太可愛了！',                       # 固定装饰文案（繁体；LXGWWenKai 预检）
            # 底部黑条（bottom 24/侧 24；padding 13/18；suffix 固定装饰文案）
            'bar_bottom': 24, 'bar_side': 24, 'bar_pad_y': 13, 'bar_pad_x': 18,
            'bar_meta_px': 11, 'bar_meta_letter': '.3em', 'bar_suffix': 'POP ART',
            # 黑条星群 12 颗（坐标表写死：8 锚位 right 66→790 贯穿/纵向 -44~48 两层错落/
            # 大小 11-44px 两端大中间小/四色轮换；rot=±35° 转角 seed=7 预计算，
            # random.Random(7).randint(-35,35) 序列，引擎内不跑 random）
            'stars': ({'right': 66,  'top': -38, 'size': 34, 'color': '#23c4a7', 'rot': 6},
                      {'right': 128, 'top': -10, 'size': 16, 'color': '#f2ecdc', 'rot': -16},
                      {'right': 180, 'top': 34,  'size': 12, 'color': '#ff2d55', 'rot': 15},
                      {'right': 238, 'top': -30, 'size': 22, 'color': '#ffcc00', 'rot': -29},
                      {'right': 300, 'top': 18,  'size': 15, 'color': '#f2ecdc', 'rot': -26},
                      {'right': 356, 'top': -42, 'size': 44, 'color': '#ff2d55', 'rot': 33},
                      {'right': 420, 'top': 30,  'size': 13, 'color': '#23c4a7', 'rot': -23},
                      {'right': 480, 'top': -8,  'size': 18, 'color': '#ffcc00', 'rot': 11},
                      {'right': 545, 'top': 40,  'size': 11, 'color': '#f2ecdc', 'rot': -28},
                      {'right': 610, 'top': -20, 'size': 26, 'color': '#23c4a7', 'rot': 29},
                      {'right': 690, 'top': 20,  'size': 14, 'color': '#ff2d55', 'rot': -8},
                      {'right': 790, 'top': -34, 'size': 20, 'color': '#f2ecdc', 'rot': -31}),
            'star_field_color': '#111111',                     # 星描边色
            # fg_texts dict 形态：按文案自身 font 逐字预检（设计稿 §0.5）
            'fg_texts': {'bubble_text': 'LXGWWenKai'},
            },
    ),
    # ---------- 报纸印刷波普（§1.3：外框 #e8e2d2 padding 17 + 内版 #f2ecdc 3.5px 黑边 +
    #           三段律（刊头 13% | 照片 74% | 底部 13%）+ 刊头半调网点满铺 + 渐隐 mask
    #           加速版（.85@0→.65@30%→.18@45%→transparent@62%；45% 衰减中点=v4d 用户
    #           拍板参数，非原稿 55%）+ 原色照片 + 白网点 overlay（radial 2.1px/6.3px
    #           网格/overlay 混合/opacity .5——原色上的制版感）+ 底部镜像渐隐 +
    #           底部文字 padding-bottom 26px（v5 用户拍板上移）。
    #           hero=bottom_center，text_on_photo=True（星无/网点满铺，需人工核）。
    #           pop04c+pop04d 渐隐参数探针移植）----------
    'pop_press': _cfg(
        template_id='_tpl_pop_press', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        base_color='#e8e2d2', tone_filter='contrast(1.05) saturate(1.1)',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'Courier New'},
        scale={'hero_px': 46, 'lead_px': 15, 'micro_px': 13,
               'hero_lh': 1.0, 'hero_letter': '.22em', 'hero_shadow': 'none'},
        palette={'primary': '#e8e2d2', 'accent': '#111111', 'point': '#f2ecdc'},
        layout={
            'frame_pad': 17, 'inner_border': 3.5, 'inner_color': '#f2ecdc',
            # 三段律（等高对称）
            'head_h_pct': 13, 'photo_h_pct': 74, 'foot_h_pct': 13,
            # 半调网点（刊头/底部共用参数）
            'halo_px': 2.8, 'halo_inner': 2.2, 'halo_gap': 8.4,
            # 渐隐 mask 加速版（v4d 用户拍板：45% 衰减中点，非原稿 55%）
            'fade_stops': ((0, .85), (30, .65), (45, .18), (62, 0)),
            # 刊头文字（padding-top 34；纸色光晕 text-shadow；EN 黑底白字条）
            'head_pad_top': 34, 'head_glow': '0 0 6px #f2ecdc,0 0 10px #f2ecdc',
            'en_bar_px': 13, 'en_bar_letter': '.3em', 'en_bar_pad_y': 3, 'en_bar_pad_x': 14,
            'en_bar_max_w': 560,        # 长 EN 截断兜底（缺省文本不触，视觉零变化）
            # 照片区（原色 + 白网点 overlay）
            'photo_side': 24, 'photo_border': 3.5, 'photo_pos': 'top',
            'ov_px': 2.1, 'ov_inner': 1.6, 'ov_gap': 6.3, 'ov_opacity': .5,
            # 底部（镜像渐隐 0deg；文字容器 padding-bottom 26）
            'foot_title_px': 34, 'foot_title_letter': '.16em',
            'foot_sep_color': '#b3442f',
            'foot_city': '網點城市',                           # 固定装饰文案（繁体；宋 Heavy 预检）
            'foot_text_px': 15, 'foot_text_letter': '.22em',
            'foot_text': '每一個網點，都是一扇亮著的窗。',       # 固定装饰文案（LXGWWenKai 预检）
            'foot_pad_bottom': 26,
            # fg_texts dict 形态：按文案自身 font 逐字预检（设计稿 §0.5）
            'fg_texts': {'foot_city': 'SourceSerifHeavy', 'foot_text': 'LXGWWenKai'},
            },
    ),

    # =================================================================
    # 撕纸手帐（2026-09-09，docs/批量设计-torn_journal-设计.md §1 · 第 14 款）
    # 数值为 900×1200 基准像素。本款特殊：撕纸装裱=刚性块禁非等比缩放（撕边咬口会
    # 变形），统一缩放因子 s=min(W/900,H/1200)、原点偏移 ox/oy——由模板
    # _tpl_torn_journal 内实现（非家族通用 fx=fy=fs）。
    # 点表/飞点为探针 v6 固定 seed 预计算字面量（scripts/_gen_torn_config.py 复算并与
    # 探针 HTML 逐点校验一致后脚本化转写；引擎内不跑 random——pop_lichtenstein seed=7
    # 同口径）。滤镜 5 只 feTurbulence 参数与涂鸦 14 件 d 路径/位置从探针逐字转录。
    # =================================================================
    'torn_journal': _cfg(
        template_id='_tpl_torn_journal', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True,
        base_color='#f2eddf', tone_filter='',          # 照片原色（拼贴是纸面装裱，不动照片调子）
        fonts={'hero': 'ZhuoKaiKai', 'emotion': 'CaveatBold', 'data': 'LXGWWenKai'},
        scale={'hero_px': 84, 'lead_px': 42, 'micro_px': 26,
               'hero_lh': 1.1, 'hero_letter': '6px', 'hero_shadow': 'none'},
        palette={'primary': '#f2eddf', 'accent': '#3a6ea5', 'point': '#c23b2e'},
        layout={
            # ---- 帧几何（基准 900×1200；探针 v6 终值）----
            'frame_top': 288, 'photo_w': 572, 'photo_h': 657,   # 照片窗终值；2026-09-25 直撕后模板不引用（参数保留，见设计档 §1.3）
            'photo_dx': 69, 'photo_dy': 64,      # 照片窗在 wrap 内偏移（探针 SX/SY）；直撕后模板不引用（参数保留）
            'wrap_w': 701, 'wrap_h': 784,        # wrap 外沿（=外环最大值+10）
            'frame_rot': -1.4,                   # 撕纸整体微旋转 deg
            'paper_color': '#faf7ee',            # 撕纸白边色
            # ---- 撕边生成参数（探针 v6 复算口径记录；点表即其确定性产物）----
            'torn_params': {'inner_seed': 901, 'coarse': 4, 'fine_inner': 2, 'nicks_inner': 0,
                            'outer_seed': 777, 'side': (30, 40), 'cap': (30, 40),
                            'fine_outer': 8, 'nicks_side': 4, 'nicks_cap': 3,
                            'cap_bite': (70, 100)},
            # ---- 撕边点表（探针 v6 预计算字面量，各 222 点；渲染端 polygon=round(x·s,1)px
            #      ——s=1 时与探针 HTML 逐字节一致）----
            'torn_inner': (
                (69, 59.7),
                (80.2, 64.1),
                (91.4, 65.7),
                (102.6, 64.9),
                (113.9, 65.5),
                (125.1, 66.7),
                (136.3, 69.9),
                (147.5, 72.7),
                (158.7, 70.2),
                (169.9, 67.3),
                (181.2, 62.4),
                (192.4, 62.2),
                (203.6, 65.1),
                (214.8, 66.3),
                (226, 70.8),
                (237.2, 71.1),
                (248.5, 69.2),
                (259.7, 64),
                (270.9, 62.9),
                (282.1, 60.4),
                (293.3, 62.4),
                (304.5, 59.3),
                (315.7, 60.3),
                (327, 55.9),
                (338.2, 56.4),
                (349.4, 59.8),
                (360.6, 66.5),
                (371.8, 66.7),
                (383, 64.7),
                (394.3, 61.8),
                (405.5, 58.7),
                (416.7, 58),
                (427.9, 58.4),
                (439.1, 62.9),
                (450.3, 63.5),
                (461.5, 67),
                (472.8, 66.3),
                (484, 66.1),
                (495.2, 67.4),
                (506.4, 71.7),
                (517.6, 71.4),
                (528.8, 68.3),
                (540.1, 63.4),
                (551.3, 59.9),
                (562.5, 59.3),
                (573.7, 64.7),
                (584.9, 68.2),
                (596.1, 70),
                (607.4, 70.8),
                (618.6, 65.8),
                (629.8, 64.4),
                (641, 61.3),
                (640.4, 64),
                (638.2, 75.3),
                (636.1, 86.7),
                (638.7, 98),
                (642.6, 109.3),
                (648.3, 120.6),
                (649.1, 132),
                (645.3, 143.3),
                (643, 154.6),
                (643.4, 165.9),
                (644.6, 177.3),
                (644.3, 188.6),
                (644.1, 199.9),
                (644.3, 211.3),
                (638.8, 222.6),
                (640.6, 233.9),
                (641.5, 245.2),
                (644.6, 256.6),
                (648.7, 267.9),
                (647.5, 279.2),
                (645.1, 290.6),
                (640.9, 301.9),
                (638.1, 313.2),
                (640, 324.5),
                (640.4, 335.9),
                (639.6, 347.2),
                (636.6, 358.5),
                (636.1, 369.8),
                (633.8, 381.2),
                (639.3, 392.5),
                (644.3, 403.8),
                (643.2, 415.2),
                (640.5, 426.5),
                (640.1, 437.8),
                (633.1, 449.1),
                (634.5, 460.5),
                (634.8, 471.8),
                (638.3, 483.1),
                (638.5, 494.4),
                (637.6, 505.8),
                (635.4, 517.1),
                (635.7, 528.4),
                (639, 539.8),
                (643.5, 551.1),
                (643.9, 562.4),
                (645, 573.7),
                (639.6, 585.1),
                (637.2, 596.4),
                (636.1, 607.7),
                (640.9, 619.1),
                (642, 630.4),
                (644.2, 641.7),
                (645.4, 653),
                (644.6, 664.4),
                (643.9, 675.7),
                (646.7, 687),
                (647.4, 698.3),
                (649.2, 709.7),
                (645.5, 721),
                (641, 724.5),
                (629.8, 728.6),
                (618.6, 729.8),
                (607.4, 726.5),
                (596.1, 723.7),
                (584.9, 721.9),
                (573.7, 722.7),
                (562.5, 725.5),
                (551.3, 724.7),
                (540.1, 722.5),
                (528.8, 718.6),
                (517.6, 720.1),
                (506.4, 721.8),
                (495.2, 725.3),
                (484, 725.1),
                (472.8, 725.9),
                (461.5, 720.9),
                (450.3, 722.4),
                (439.1, 719.4),
                (427.9, 719.8),
                (416.7, 722.9),
                (405.5, 718.5),
                (394.3, 714.9),
                (383, 713.4),
                (371.8, 713),
                (360.6, 716.4),
                (349.4, 720.4),
                (338.2, 723.7),
                (327, 719.2),
                (315.7, 718),
                (304.5, 720.9),
                (293.3, 722.6),
                (282.1, 723.6),
                (270.9, 721.7),
                (259.7, 719.1),
                (248.5, 718.3),
                (237.2, 717.7),
                (226, 719.6),
                (214.8, 723.4),
                (203.6, 726.5),
                (192.4, 725.4),
                (181.2, 723.4),
                (169.9, 724.5),
                (158.7, 723.6),
                (147.5, 729.2),
                (136.3, 726.5),
                (125.1, 727.5),
                (113.9, 720.3),
                (102.6, 718.9),
                (91.4, 716.2),
                (80.2, 719.6),
                (69, 723.7),
                (67, 721),
                (68, 709.7),
                (69.6, 698.3),
                (68.2, 687),
                (66.2, 675.7),
                (62.9, 664.4),
                (60.1, 653),
                (63.9, 641.7),
                (66, 630.4),
                (69.9, 619.1),
                (70.3, 607.7),
                (69, 596.4),
                (67.1, 585.1),
                (71.7, 573.7),
                (72, 562.4),
                (73.8, 551.1),
                (68.1, 539.8),
                (67.1, 528.4),
                (64.9, 517.1),
                (68, 505.8),
                (74.4, 494.4),
                (76, 483.1),
                (72.5, 471.8),
                (71.9, 460.5),
                (73.4, 449.1),
                (75.5, 437.8),
                (76.3, 426.5),
                (74, 415.2),
                (68.7, 403.8),
                (63, 392.5),
                (64.4, 381.2),
                (68.9, 369.8),
                (72, 358.5),
                (70, 347.2),
                (67.3, 335.9),
                (66.3, 324.5),
                (66.9, 313.2),
                (69.6, 301.9),
                (71.8, 290.6),
                (67.7, 279.2),
                (62.8, 267.9),
                (61.6, 256.6),
                (61.6, 245.2),
                (65, 233.9),
                (70, 222.6),
                (66.1, 211.3),
                (66, 199.9),
                (69, 188.6),
                (72.6, 177.3),
                (73.2, 165.9),
                (75.7, 154.6),
                (70.6, 143.3),
                (65.9, 132),
                (67.7, 120.6),
                (70.3, 109.3),
                (74, 98),
                (74, 86.7),
                (72, 75.3),
                (69.1, 64),
            ),
            'torn_outer': (
                (69.2, 25.2),
                (87.8, 35.7),
                (92.6, 32.2),
                (102.5, 26.6),
                (118.4, 10.1),
                (132.9, 26.6),
                (148.1, 26),
                (148, 31),
                (151.5, 40.5),
                (157.3, 30.9),
                (173, 26.2),
                (196.4, 28.2),
                (209.5, 31.9),
                (224.2, 29.5),
                (233.9, 34),
                (235.1, 40.2),
                (237.1, 33.1),
                (248.1, 23.3),
                (265.8, 31.8),
                (281.4, 21.3),
                (291.4, 22.7),
                (300.3, 15.7),
                (310.9, 27.6),
                (321.9, 26.9),
                (345.4, 14.3),
                (361.9, 32),
                (371.4, 31.3),
                (369.3, 35.7),
                (376.2, 33),
                (383.5, 21.2),
                (399.9, 26.1),
                (416.2, 24.6),
                (434.9, 26.6),
                (448.5, 21.5),
                (455.6, 35),
                (466.1, 30.6),
                (471.3, 27.8),
                (485.8, 29.8),
                (502.1, 39.4),
                (512.3, 38.8),
                (511.8, 32.2),
                (513.9, 26.8),
                (525.7, 25.2),
                (544.1, 20.5),
                (572.1, 14.1),
                (586.5, 32.4),
                (592.7, 35.5),
                (601.6, 22.9),
                (601.2, 38),
                (608.2, 29.7),
                (623.7, 33.7),
                (640.2, 38.3),
                (682.9, 72.6),
                (671.5, 81.6),
                (669.3, 86),
                (664.4, 90.7),
                (663.2, 100.5),
                (686.9, 109.5),
                (691.3, 137.6),
                (686.5, 154.4),
                (673.1, 157.1),
                (687.6, 162.8),
                (679.9, 175.9),
                (680.9, 189.4),
                (678.7, 200),
                (679.8, 219.6),
                (671, 227.8),
                (679.4, 229.2),
                (672.3, 239.9),
                (674.2, 247.1),
                (686.9, 263),
                (685.9, 285.5),
                (675.7, 299.5),
                (675.6, 312.5),
                (668.5, 314.4),
                (677.8, 320.8),
                (678.8, 336.5),
                (682.7, 354.5),
                (666.5, 363.2),
                (673, 374.3),
                (666.1, 376.6),
                (674.1, 376.5),
                (685.9, 396.7),
                (689, 422.8),
                (672.1, 430.8),
                (673.6, 448.8),
                (658, 455.3),
                (665.3, 458.1),
                (662, 467.1),
                (675, 477.1),
                (675.5, 495.7),
                (672.7, 510.6),
                (675.7, 520.5),
                (666.5, 523.5),
                (679.3, 525.8),
                (682.1, 542.9),
                (669.7, 560.7),
                (686.9, 581.6),
                (667.5, 594.7),
                (663.1, 600.4),
                (669.2, 602.4),
                (680.3, 608.7),
                (680.9, 624.7),
                (678.5, 636.6),
                (685.6, 652.3),
                (682.5, 666.8),
                (669.2, 673.4),
                (663.8, 684.4),
                (670.2, 695.8),
                (682.1, 712.4),
                (672.8, 736.1),
                (652, 747.2),
                (640.5, 774.4),
                (615.5, 762.9),
                (598, 760.8),
                (588.2, 762),
                (583.6, 753.5),
                (580, 761.1),
                (566.2, 768.3),
                (546.8, 757.6),
                (529.1, 763),
                (525.9, 746.3),
                (521.7, 748),
                (513.6, 753),
                (500.5, 761.8),
                (484.9, 759.6),
                (465.9, 762.7),
                (456.6, 751.7),
                (448.6, 747.3),
                (435.4, 752),
                (432.3, 747.6),
                (414.7, 756.8),
                (390.1, 761.5),
                (385.2, 755.4),
                (379.9, 750.2),
                (376.9, 750.8),
                (373, 753.8),
                (359, 750.1),
                (336, 763.5),
                (321, 742.6),
                (318.2, 748.9),
                (313.2, 763.2),
                (298.2, 762.9),
                (281.1, 748.7),
                (264.6, 752.6),
                (254.5, 753.9),
                (246.2, 753.8),
                (239.5, 755.7),
                (235.6, 757.1),
                (224.2, 754.1),
                (207.2, 767.5),
                (186.4, 767.7),
                (179.9, 754.8),
                (170.3, 764.1),
                (166.4, 759.9),
                (152.5, 767.2),
                (134.1, 755),
                (115.6, 761.7),
                (102.3, 750.5),
                (95.6, 757.2),
                (92.4, 746.2),
                (91.6, 753.8),
                (72.3, 754.4),
                (40.4, 722.9),
                (29, 705.2),
                (32.4, 698.1),
                (37.4, 691.7),
                (31.7, 683.7),
                (47.6, 668.5),
                (43.4, 652.3),
                (38.5, 635.1),
                (27.9, 620.3),
                (36, 612.6),
                (37.1, 609.2),
                (30.9, 601.8),
                (36, 581.2),
                (34.7, 565.7),
                (37.4, 559.3),
                (36.4, 557.5),
                (42.6, 547.3),
                (31, 533.6),
                (25.2, 515.5),
                (43.3, 495.4),
                (37.4, 481.4),
                (37.1, 486.4),
                (34.8, 478.6),
                (27.5, 458.6),
                (38.9, 443.6),
                (38.3, 433.1),
                (45.6, 428.5),
                (35.6, 428.1),
                (35.9, 419.8),
                (29.6, 398.7),
                (21.1, 369.9),
                (31, 357.1),
                (43.5, 357.1),
                (37.7, 354),
                (33.7, 341.3),
                (38.3, 325),
                (36.5, 308.9),
                (39.8, 295.5),
                (42.1, 292.9),
                (34.1, 292.7),
                (28, 277.2),
                (24.4, 258.4),
                (22.9, 239.6),
                (36.1, 223.2),
                (32.5, 220.7),
                (30, 217.6),
                (24.2, 194.6),
                (37.6, 179.6),
                (33.1, 170),
                (38.6, 161.1),
                (31.4, 159.7),
                (31.2, 160.3),
                (10.5, 139),
                (22.9, 112),
                (37, 100.1),
                (38.5, 92.3),
                (38.6, 89.7),
                (39.3, 82.4),
                (37.8, 70),
            ),
            # ---- 纤维飞点 46 条（seed 20260911；(x,y,deg,len) 基准坐标随 s 缩放）----
            'flecks': (
                (721.853, 437.342, 80.7439, 4.639),
                (821.109, 605.628, 73.7475, 7.42288),
                (129.598, 909.29, 135.416, 4.61181),
                (341.885, 709.814, 117.559, 10.6371),
                (437.502, 741.604, 131.795, 8.24402),
                (411.449, 1149.81, 135.537, 9.62343),
                (149.635, 1102.6, 24.8936, 8.07933),
                (31.9205, 795.293, 158.959, 4.38859),
                (217.478, 676.551, 33.2555, 9.37235),
                (314.792, 666.056, 118.482, 7.35489),
                (500.822, 649.285, 123.552, 8.6175),
                (171.493, 909.705, 122.567, 6.5245),
                (513.167, 827.009, 40.2614, 10.0379),
                (711.263, 827.393, 163.282, 6.30256),
                (226.851, 597.399, 97.6481, 6.90232),
                (293.228, 916.225, 30.9761, 4.15539),
                (703.915, 700.245, 117.215, 10.8584),
                (503.437, 550.019, 98.0998, 5.05129),
                (757.194, 951.741, 129.415, 10.6899),
                (242.502, 610.616, 90.7686, 10.1928),
                (722.263, 1042.95, 59.3213, 4.15855),
                (678.158, 989.155, 10.2284, 5.40324),
                (615.124, 636.23, 13.3268, 4.45433),
                (126.901, 1019.31, 1.23509, 6.34538),
                (286.545, 893.832, 52.8749, 4.2412),
                (161.343, 838.594, 20.9966, 10.8977),
                (421.709, 805.249, 47.3172, 9.40107),
                (249.692, 739.263, 157.712, 6.6198),
                (103.994, 640.533, 145.218, 6.3003),
                (446.439, 131.771, 165.64, 6.22482),
                (871.208, 437.775, 10.4716, 7.09206),
                (582.743, 472.546, 113.261, 10.4231),
                (51.3176, 102.622, 22.5913, 7.55598),
                (269.988, 178.347, 178.97, 8.23914),
                (20.3908, 1011.14, 168.307, 10.7496),
                (602.266, 227.368, 100.961, 4.75338),
                (662.717, 824.259, 168.321, 4.80789),
                (561.78, 1012.73, 53.2773, 10.0891),
                (342.356, 1134.06, 156.629, 6.02323),
                (351.659, 864.159, 40.1198, 9.23825),
                (191.147, 893.644, 35.7679, 4.40866),
                (763.318, 931.767, 124.733, 6.48837),
                (473.456, 817.574, 170.901, 4.61827),
                (449.572, 379.672, 102.059, 10.1958),
                (493.553, 814.942, 25.1693, 5.51466),
                (399.731, 559.833, 157.462, 7.23759),
            ),
            # ---- 滤镜 5 只 feTurbulence（参数+feColorMatrix 从探针 v6 逐字转录）----
            'filter_fiber':      {'bf': 0.13,  'oct': 2, 'seed': 11, 'disp_scale': 9},
            'filter_mottle':     {'bf': 0.013, 'oct': 3, 'seed': 5,
                                  'matrix': '0 0 0 0 0.72  0 0 0 0 0.66  0 0 0 0 0.54  0 0 0 0.34 0'},
            'filter_grainf':     {'bf': 0.26,  'oct': 2, 'seed': 9,
                                  'matrix': '0 0 0 0 0.66  0 0 0 0 0.61  0 0 0 0 0.50  0 0 0 0.22 0'},
            'filter_sheen':      {'bf': 0.018, 'oct': 3, 'seed': 21,
                                  'matrix': '0 0 0 0 1  0 0 0 0 1  0 0 0 0 0.96  0 0 0 0.14 0'},
            'filter_papernoise': {'bf': 0.02,  'oct': 3, 'seed': 13,
                                  'matrix': '0 0 0 0 0.70  0 0 0 0 0.65  0 0 0 0 0.54  0 0 0 0.15 0'},
            # ---- 文字区（基准坐标）----
            'hero_top': 100, 'sub_top': 234,
            'hero_rot_cycle': (-2.5, 2.0, -1.5, 2.5),   # 逐字循环微旋转
            'hero_accent_px': 1.1,                       # 中间字朱红强调字号倍率（em）
            'rail_loc_x': 56, 'rail_loc_y': 336,         # 左轨 loc
            'rail_phrase_x': 22, 'rail_phrase_y': 342,   # 左轨短语
            'rail_date_right': 36, 'rail_date_y': 320,   # 右轨 date（x=right）
            'photo_phrase_right': 10, 'photo_phrase_y': 368,  # 白竖排短语（x=right）→ 2026-09-25 1/3 裁定：出照片落右缘 stage（色同步改深）
            'vtext_px': 26, 'phrase_px': 21, 'photo_phrase_px': 22,  # 字号
            # ---- 固定文案（fg_texts dict 形态——按文案自身 font 逐字 cmap 预检，构图三款先例）----
            'left_phrase': 'そら、はれた。',
            'bubble_l1': '今日も', 'bubble_l2': '晴れかな',   # 模板拼 <br>（fg 预检不含标签）
            'tr_vtext': 'よき一日を',   # 右上竖排短语（cat_phrase 位）
            'photo_phrase': '思い出を、ここに。',
            'foot_jp': '— 素晴らしい —',
            'foot_en': 'TRAVEL TO SOMEWHERE',                # CaveatBold 纯 ASCII 不入预检
            'small_note': '雲の隙間、光の差す方へと歩いていきたい。',
            # ---- 底部/涂鸦附属文字定位（探针 :260/:305/:308-317 基准坐标）----
            'foot_jp_y': 1062, 'foot_jp_px': 24, 'foot_en_y': 1094, 'foot_en_px': 32,
            'note_y': 1136, 'note_px': 17,
            'fg_texts': {'left_phrase': 'LXGWWenKai', 'bubble_l1': 'LXGWWenKai',
                         'bubble_l2': 'LXGWWenKai', 'tr_vtext': 'LXGWWenKai',
                         'photo_phrase': 'LXGWWenKai', 'foot_jp': 'LXGWWenKai',
                         # 审查修复 F3（2026-09-25）：small_note 补入预检——设计档 §1.3 固定
                         # 文案表声明参与 fg_texts（日文长句，LXGW 缺字时兜底而非静默 tofu）。
                         'small_note': 'LXGWWenKai'},
            # ---- 涂鸦 14 件（d 路径与位置逐字从探针 v6 HTML 转录；蓝系线稿+纸色填充）----
            'doodles': {
                'wave_top':    {'top': 24, 'left': 300, 'w': 300, 'h': 60,
                                'paths': [('M0 34 Q25 4 50 32 T100 30 T150 34 T200 28 T250 34 T300 30', '#7fa8d9', 6)]},
                'rain_line':   {'top': 66, 'left': 158, 'w': 90, 'h': 36,
                                'paths': [('M6 4 q-5 12 0 20', '#7fa8d9', 5), ('M30 2 q-5 12 0 20', '#7fa8d9', 5),
                                          ('M54 4 q-5 12 0 20', '#7fa8d9', 5), ('M78 2 q-5 12 0 20', '#7fa8d9', 5)]},
                'title_arc':   {'top': 190, 'left': 260, 'w': 380, 'h': 34,
                                'paths': [('M8 20 c-8 -16 18 -24 22 -6 c2 9 -11 13 -15 4 M22 16 Q120 2 210 12 T372 8', '#7fa8d9', 5)]},
                'cat_phrase':  {'top': 56, 'right': 34, 'px': 22},   # tr_vtext（右上竖排短语）落位
                'cat':         {'top': 80, 'right': 104, 'w': 64, 'h': 92, 'stroke': '#3a3a3a',
                                'items': ['M20 24 L26 8 L34 20', 'M40 18 L48 6 L54 22',
                                          'C:37,34,17', 'M22 88 q1 -32 15 -32 q15 0 16 32',
                                          'M53 82 q14 -2 10 -17', 'D:31,32,1.6', 'D:43,32,1.6',
                                          'M34 40 q3 3 6 0']},
                'dots_row':    {'top': 270, 'left': 48, 'w': 170, 'h': 16,
                                'circles': ((8, 8, 6), (32, 8, 6), (56, 8, 6), (80, 8, 6), (104, 8, 6),
                                            (128, 8, 6), (152, 8, 6))},
                'bubble':      {'top': 973, 'left': 0, 'w': 160, 'h': 140, 'txt_top': 999, 'txt_left': 10, 'txt_w': 140,
                                # ↑ 2026-09-25 四裁：上移（1010→973）+ 压照放宽 10 个点 ——
                                #  压入 61×99 ≈ 27%（用户"多10%"口径内，仍 <1/3）。
                                'paths': [('M30 64 a18 18 0 1 1 28 -26 a20 20 0 1 1 34 8 a16 16 0 1 1 8 26 a14 14 0 0 1 -22 10 a18 18 0 0 1 -30 -4 a14 14 0 0 1 -18 -10 z', '#6f9fd8', 4)],
                                'extra_circles': ((52, 112, 5, 3), (44, 128, 3, 2.5))},
                'megaphone':   {'top': 1075, 'left': 804, 'w': 86, 'h': 72,
                                'items': [('M10 30 L38 12 v44 L10 40 z', 'F'), ('38,22,9,24', 'R'),
                                          ('M56 26 q9 9 0 18', 'A'), ('M66 18 q15 15 0 34', 'A')]},
                'xxx':         {'top': 40, 'left': 0, 'w': 120, 'h': 30,
                                'paths': [('M8 8 L26 24 M26 8 L8 24', '#7fa8d9', 7), ('M50 8 L68 24 M68 8 L50 24', '#7fa8d9', 7), ('M92 8 L110 24 M110 8 L92 24', '#7fa8d9', 7)]},
                'spiral':      {'top': 680, 'right': 48, 'w': 60, 'h': 110,
                                'paths': [('M50 12 A15 15 0 1 0 22 32 A9 9 0 1 0 36 42', '#7fa8d9', 5),
                                          ('M28 50 Q18 72 30 92', '#7fa8d9', 5), ('M20 80 L30 94 L38 78', '#7fa8d9', 5)]},
                'tshirt':      {'top': 815, 'right': 8, 'w': 88, 'h': 100,
                                'items': [('M22 10 L36 2 q9 9 18 0 L68 10 L82 32 L66 42 L64 30 L64 92 H26 L26 30 L24 42 L8 32 Z', 'S')]},
                'badge':       {'top': 946, 'right': 14, 'w': 76, 'h': 50,
                                'ellipse': (38, 25, 34, 21), 'txt_top': 956, 'txt_right': 14, 'txt_px': 27, 'text': 'go!'},

                'plane':       {'top': 1084, 'left': 700, 'w': 70, 'h': 48,
                                'items': [('M4 24 L64 6 L38 40 L30 26 Z', 'S'), ('M30 26 L64 6', 'S'),
                                          ('M6 36 q10 -3 15 3', 'W')]},
                'wave_foot':   {'top': 1166, 'left': 30, 'w': 840, 'h': 18,
                                'paths': [('M0 10 Q30 0 60 10 T120 10 T180 10 T240 10 T300 10 T360 10 T420 10 T480 10 T540 10 T600 10 T660 10 T720 10 T780 10 T840 10', '#7fa8d9', 4)]},
            },
            # 涂鸦渲染参数（探针对齐：item 编码 S=描边线稿 F=实心填充 R=矩形 A=弧线
            # W=细轨迹线 C=circle D=实心点；蓝系色已在各 item/paths 内逐件标注）
            'accent_2': '#7fa8d9',       # 浅蓝（涂鸦/波浪/虚点）
            'accent_3': '#6f9fd8',       # 中蓝（气泡/喇叭/T恤）
            'ink': '#2b2b2b',            # 主标色
            'sub_color': '#4a4a4a', 'tr_vtext_color': '#4a4a4a',
            'bubble_color': '#2e5e8f', 'small_note_color': '#8a8578',
            'foot_en_color': '#4a5a74',
            'grain_stroke': '#cfc6ae', 'grain_w': 1.6, 'grain_op': 0.55,   # flecks 渲染
            },
        ),
    # =================================================================
    # 展览海报（2026-09-10，docs/批量设计-展览海报-设计.md §1 · 第 15 款）
    # 数值为 900×1200 基准像素。本款特殊：固定几何（照片窗 + 左右竖排翼 + 底栏）
    # 禁非等比缩放 → 统一缩放因子 s=min(W/900,H/1200)、原点偏移 ox/oy——由模板
    # _tpl_exhibition_poster 内实现（照 torn_journal 先例，非家族通用 fx=fy=fs）。
    # 竖排大字为霞鹜文楷 LXGWWenKai（emotion 位触发 _LXGW_CSS 注入）；主标为
    # SourceSerifHeavy（思源宋 CN Heavy，基础常量零新增分支）；配色 = 墨黑 +
    # 朱砂红点睛（accent #b82828 = 左上角标方块 + 右侧展签）；text_on_photo=False
    # 护脸安全（文字全落纸面）。左右竖排大字/展签/底栏装饰位 = fg_texts 固定文案。
    # =================================================================
    'exhibition_poster': _cfg(
        template_id='_tpl_exhibition_poster', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#ffffff', tone_filter='',          # 照片原色（装裱不动照片调子，P0-1）
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 116, 'lead_px': 13, 'micro_px': 10,
               'hero_lh': 0.95, 'hero_letter': '8px', 'hero_shadow': 'none'},
        palette={'primary': '#ffffff', 'accent': '#b82828', 'point': '#1a1a1a'},
        layout={
            # ---- 帧几何（基准 900×1200；探针真机 _shot_exhibition_poster.py 转录）----
            'img_w': 710, 'img_h': 820, 'img_x': 94, 'img_y': 252,
            'img_focus': 'center 20%',
            'wing_w': 94, 'wing_top': 252, 'wing_h': 820,
            # ---- 顶部区（徽标页眉一行 → 主标独立一行 → 英文副标；垂直分离避与徽标冲突）----
            'badge_top': 24, 'badge_left': 24, 'badge_logo_px': 14, 'badge_dot': 10,
            'hero_top': 96, 'hero_sub_top': 216, 'hero_sub_px': 13, 'hero_sub_letter': '6px',
            # ---- 竖排翼（左右对称；霞鹜文楷大字 + 伴随小字英文 + 展签）----
            'v_name_px': 50, 'v_name_letter': '10px',
            'v_role_px': 10, 'v_role_letter': '3px', 'v_gap': 6,
            'tag_px': 10, 'date_rail_px': 11, 'meta_px': 10,
            # ---- 底部三栏（上细黑线 + 左标题/中日期/右展馆）----
            'foot_bottom': 32, 'foot_x': 94, 'foot_w': 710, 'foot_rule': 2,
            'f_title_px': 16, 'f_desc_px': 9, 'f_time_px': 13, 'f_hours_px': 9,
            'f_venue_px': 13, 'f_adm_px': 9,
            # ---- 装饰位固定文案值（槽位 -> 文案；纯装饰小字，不走 fg_texts 缺字预检——
            #      字体靠模板内 CSS 回退链〔_serif_cn/_sans_cn〕兜底，避免 BodoniModa 缺字
            #      升格 ✗。模板在参数缺省时用 fixed 值兜底：「极简输入也能成画」）----
            'fixed': {
                'badge_logo': 'TOKYO ART MUSEUM',
                'badge_sub': 'CONTEMPORARY EXHIBITION',
                'left_meta_top': 'EXHIBITION • 2026',
                'left_name': '大石',
                'left_role': 'ARCHITECT • TOKYO',
                'left_meta_bot': 'MUSEUM ARCHIVE',
                'right_name': '鉄男',
                'right_role': 'SCULPTOR • KYOTO',
                'right_tag': '特別企画',
                'f_title': '光の教会 · 安藤忠雄建築展',
                'f_desc': '建筑与光影的几何叙事',
                'f_hours': '10:00 - 18:00 (周一休馆)',
                'f_venue': '国立新美术馆 / 企划展厅',
                'f_adm': '免费入场 · 特别企划',
            },
        },
    ),

    # =================================================================
    # 撕纸 · 破洞窥视（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 16 款）
    # 牛皮纸封面撕洞窥夜：零裁剪 contain 洞（洞内矩形 = 原图等比，照片 100% 可见）+
    # 撕边恒朝外（细毛边 6~15 / 深咬口 15~28，咬牛皮纸不咬照片，img = R + 38 盖最深齿）+
    # 4 根不对称锋刺（横图冲出画布缘锐 V / 竖图·长条画布内钝 V）+ 纸纤维底纹 0.20/0.16。
    # 照片原色（P0-1 零像素改动）。基准 900×1200；几何缩放 s = min(W/900, H/1200) + ox/oy。
    # text_on_photo = False（文字全落牛皮纸封面、照片在洞中，护脸安全）。
    # 主标阴影走 scale.hero_shadow、揭语阴影走 layout.lead_shadow（白字压牛皮纸保读 = 探针定稿
    # 设计语义；质检 contrast ✗ 为 SVG 渐变伪影，见 validate_quality.WHITELIST['torn_peephole']）。
    # =================================================================
    'torn_peephole': _cfg(
        template_id='_tpl_torn_peephole', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#e9e2cf', tone_filter='',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 74, 'lead_px': 25, 'micro_px': 12,
               'hero_lh': 1.12, 'hero_letter': '0.22em',
               'hero_shadow': '0 3px 14px rgba(60,38,10,0.6)'},
        palette={'primary': '#e9e2cf', 'accent': '#b82828', 'point': '#fdf8ec'},
        layout={
            # ---- 洞几何（基准 900×1200；模板按原图比例 contain 自适应 → 零裁剪）----
            'hole_aw': 819, 'hole_ah': 776,        # 洞可用区宽高（91% 画布宽 × 64.7% 画布高）
            'hole_cx': 450, 'hole_cy': 613,        # 洞中心
            'hole_pad': 10, 'img_pad': 38,         # 洞 = R + hole_pad；img = R + img_pad（盖最深齿）
            # ---- 撕边（恒朝外咬牛皮纸；约 80% 细毛边 + 20% 深咬口）----
            'n': 30, 'fine_lo': 6, 'fine_hi': 15, 'deep_lo': 15, 'deep_hi': 28, 'deep_ratio': 0.2,
            # ---- 锋刺（idx 取右/左边点列起点偏移；inset = 根部内收；dy = 尖端纵向偏移）----
            # 横图：尖端冲到画布缘外（锐 V，冲出量 = edge_out）
            'edge_out': 18,
            'spike_out_r': [(10, 46, 6), (21, 56, -10)],
            'spike_out_l': [(9, 46, -12), (20, 56, 8)],
            # 竖图/长条：尖端留在画布内（钝 V；out = 尖端伸出洞缘距离，inset = 根部内收）
            'spike_in_r': [(10, 42, 22, 6), (21, 16, 18, -10)],
            'spike_in_l': [(9, 36, 22, -12), (20, 10, 18, 8)],
            # ---- 文字区 ----
            'hero_top': 82, 'sub_top': 168, 'sub_px': 12, 'sub_letter': '0.42em',
            'lead_bottom': 64, 'micro_bottom': 32,
            # 副标/揭语阴影（白字压牛皮纸保读；单值不随字号缩放，同 head_glow 先例）
            'lead_shadow': '0 2px 9px rgba(60,38,10,0.6)',
            # ---- 胶带（宽高 + (left, top, rotate) ×2）----
            'tape_w': 105, 'tape_h': 26,
            'tape1': (42, 29, -8), 'tape2': (745, 1144, -6),
            # ---- 纸纤维底纹强度（横/竖两组 repeating-linear-gradient）----
            'fiber_h': 0.20, 'fiber_v': 0.16,
            # ---- 装饰位固定文案（参数缺省时兜底）----
            'fixed': {
                'sub': 'TEAR OPEN · PEEK THE NIGHT',
                'lead': '把封面撕開一個洞，夜色就漏了出來。',
                'micro': 'PEEPHOLE COVER · NO.04',
            },
        },
    ),

    # =================================================================
    # 撕纸 · 双层撕纸（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 17 款）
    # 大毛边照片（白边底层 jag 2.5 + 照片层 jag 1.3）+ 骑线标题纸片（约 1/4 压照片、
    # 3/4 落灰底；长标题 word-break 自动换行、overflow 兜底）+ 左下手记小纸片 +
    # 左下牛皮纸条（上下缘撕口 strip_poly 79/jag 8）+ NO.08 骑线圆戳 + 纸纤维底纹
    # 0.20/0.16。照片原色（P0-1）。
    # 基准 900×1200；几何缩放 s = min(W/900, H/1200) + ox/oy。
    # text_on_photo = False（纸片位置固定右下角、不涉人脸区；用户 2026-09-10 拍板不作
    # 人工核脸款——纸片骑线仅轻压照片底部 6.5%（56/864px、占纸片高 1/4），拼贴语义同
    # torn_journal）。
    # =================================================================
    'torn_deckle': _cfg(
        template_id='_tpl_torn_deckle', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#d8d4cc', tone_filter='',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 62, 'lead_px': 16, 'micro_px': 9,
               'hero_lh': 1.18, 'hero_letter': '0.16em', 'hero_shadow': 'none'},
        palette={'primary': '#d8d4cc', 'accent': '#b5976b', 'point': '#1c1812'},
        layout={
            # ---- 照片窗口（基准 900×1200；白边底层 jag_back + 照片层 jag_photo）----
            'win_top': 56, 'win_left': 34, 'win_right': 34, 'win_h': 864,
            'jag_back': 2.5, 'jag_photo': 1.3, 'photo_focus': 'top',
            # ---- 骑线标题纸片（约 1/4 压照片）----
            'plate_right': 68, 'plate_top': 864, 'plate_w': 423, 'plate_h': 228,
            'plate_jag_back': 2.6, 'plate_jag_photo': 1.4, 'plate_pad': (18, 30),
            'plate_gap': 8,
            # ---- 左下手记小纸片 + 骑线圆戳 ----
            'note_left': 51, 'note_top': 979, 'note_w': 232, 'note_h': 75,
            'note_jag_back': 2.2, 'note_jag_photo': 1.1, 'note_pad': (24, 28),
            'note_gap': 9,
            'stamp_size': 51, 'stamp_right': -17, 'stamp_top': -17, 'stamp_rot': 9,
            # ---- 左下牛皮纸条 ----
            'strip_left': 56, 'strip_bottom': 43, 'strip_pad': (14, 24),
            'strip_rot': -2, 'strip_jag': 8,        # 牛皮纸条上下缘撕口振幅（% 盒高）：盒高 51px → 名义 ±4.1px。
                                                    # 因 % 坐标以盒边为基准，外凸半幅画在盒外（无 content）不呈现，
                                                    # 实际可见 = 单向内凹锯齿 0~4.1px（实测与多边形预言 r=0.93）。
                                                    # 探针原值 1.2%≈0.6px 亚像素不可见（2026-09-10 用户拍板放大）
            # ---- 胶带 ----
            'tape_w': 73, 'tape_h': 18, 'tape1': (818, 44, -6),
            # ---- 纸纤维底纹强度 ----
            'fiber_h': 0.20, 'fiber_v': 0.16,
            # ---- 装饰位固定文案 ----
            'fixed': {
                'lead_en': 'Torn Night',
                'micro': 'DOUBLE DECKLE · VOL.08 · 2026.09',
                'note': '月台的燈，亮到很晚。',
                'note_meta': 'PLATFORM NOTES · 23:47',
                'stamp': 'NO.08',
                'strip': '拍攝手記：先撕紙，再撕夜。',
            },
        },
    ),

    # =================================================================
    # 现代网格杂志风（2026-09-16，docs/新款入库批-设计.md §2.3 · 第 18 款）
    # 暖亚麻底 #D6CEBB（R7）+ 外框线系统（粗 3px/细 1.5px 双横线 + 左右竖线 + 底线）
    # + 居中主标题（西文 Prata 在上 / 中文思源黑 Heavy 在下，R8/R9）+ 三段式元数据条
    # + 内嵌大图（1px 细框；无画中画，R1）+ 页脚两行。
    # 基准 900×1200；几何缩放 s = min(W/900, H/1200) + ox/oy（§1.2 表 B：家族默认 fs
    # 在 4:3/16:9 溢出实证否决）。text_on_photo=False（文字全落照片区外，护脸）。
    # =================================================================
    'modern_spread': _cfg(
        template_id='_tpl_modern_spread', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#D6CEBB', tone_filter='',
        fonts={'hero': 'SourceHanSansHeavy', 'emotion': 'Prata', 'data': 'SourceHanSansBold'},
        scale={'hero_px': 48, 'lead_px': 18, 'micro_px': 12.5,
               'hero_lh': 1.0, 'hero_letter': '0.10em', 'hero_shadow': 'none'},
        palette={'primary': '#D6CEBB', 'accent': '#191B1D', 'point': '#294B68'},
        layout={
            # ---- 外框线系统（§2.3 参数表；线宽走 _svf 亚像素，D-9）----
            'frame_inset': 37, 'frame_top': 40, 'frame_bottom': 35,
            'vert_rule_w': 1.5, 'base_rule_w': 1.5,
            'top_rule_bold_y': 40, 'top_rule_bold_h': 3,
            'top_rule_thin_y': 48, 'top_rule_thin_h': 1.5,
            # ---- 标题块（title_h=130 = 64+18+48 闭式；探针已钉 line-height:1，R9 锚点）----
            'title_top': 62, 'title_h': 130,
            'en_px': 64, 'en_lh': 1.0, 'en_letter': '0.02em',
            'zh_gap': 18, 'zh_fit_w': 826,          # = 900 − 2×37
            # ---- 元数据条（上下夹线 1.5px + 三段式 flex space-between）----
            'meta_top': 215, 'meta_h': 37, 'meta_rule_w': 1.5,
            'meta_pad_x': 15, 'meta_px': 14, 'meta_letter': '0.06em',
            # ---- 照片框（O-4 修正终值 52+796+52=900 对称；高 807 不变）----
            'photo_left': 52, 'photo_top': 265, 'photo_w': 796, 'photo_h': 807,
            'photo_border_w': 1, 'photo_border_color': '#191B1D',
            # ---- 页脚（第 1 行 = 内联流 + 右端 ISSUED 绝对定位；第 2 行 space-between；
            #      右端 ISSUED 与细段交叠 = 探针原样，用户 2026-09-16 裁定保持，勿当缺陷修〔设计 §8〕）----
            'foot_top': 1092, 'foot_side': 52,
            'f1_px': 18, 'f1_letter': '0.02em',
            'bar_color': '#C28362', 'bar_pad': 8,
            'f1r_px': 15, 'f1r_color': '#294B68', 'f1r_letter': '0.06em', 'f1r_top': 2,
            'f2_px': 12.5, 'f2_letter': '0.04em', 'f2_color': '#4A4A4A', 'f2_gap': 14,
            # ---- 字体新增注入（D-4：config 声明式；页脚细字思源黑 Regular）----
            'extra_fonts': ('SourceHanSansRegular',),
            # ---- 装饰位固定文案（§2.5；参数位 D/L 缺省落 '—'、S/T 缺省不渲）----
            'fixed': {
                'meta_mid': 'JOURNEYS INTO HERITAGE',
                'feat_bold': '[FEATURE] THE SOUL OF WATER TOWNS',
                'feat_thin': "EXPLORING JIANGNAN'S HIDDEN ALLEYWAYS",
                'issued': 'ISSUED',
                'deck': 'A JOURNEY THROUGH ANCIENT PAVEMENTS, RIVERS AND LANTERN-LIT NIGHTS',
            },
        },
    ),

    # =================================================================
    # 东方手记风（2026-09-16，docs/新款入库批-设计.md §2.4/§2.4.1 · 第 19 款）
    # 暖纸纹底（feTurbulence tile）+ 暖色做旧晕 + 头部三行标题群（行高钉死 1.0，
    # 闭式 14+32+68+35+13 = 162 ⇒ 底边 214，R6 构造保证）+ 单张卡纸装裱照片
    # （10px 卡纸 + 双层投影；只用一张，R2/R4）+ 图注 1 行（R5）+ 手绘箭头（恰 1 枚）
    # + 做旧邮戳 + 凹压钢印 + 年份行（SVG 双实心三角标记，零字体依赖，J1 裁定）。
    # 几何缩放同 modern_spread（§1.2 表 B）。text_on_photo=False（护脸）。
    # =================================================================
    'cultural_journal': _cfg(
        template_id='_tpl_cultural_journal', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False,
        base_color='#F4EDE1', tone_filter='',
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'CinzelBold', 'data': 'SourceHanSerifMedium'},
        scale={'hero_px': 68, 'lead_px': 15, 'micro_px': 12,
               'hero_lh': 1.0, 'hero_letter': '0.10em',
               'hero_shadow': '0 1px 0 rgba(255,255,255,.35)'},
        palette={'primary': '#F4EDE1', 'accent': '#3E2F26', 'point': '#A85A3C'},
        layout={
            # ---- 纸纹 / 做旧晕（§2.4 参数表布局键；D-12：内联 style 双引号包裹 ⇒
            #      data URI 内双引号实体化 &quot;、SVG 内层单引号、# 写 %23）----
            'grain': ("url(&quot;data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' "
                      "width='240' height='240'><filter id='n'><feTurbulence "
                      "type='fractalNoise' baseFrequency='0.82' numOctaves='4' seed='7'/>"
                      "<feColorMatrix type='saturate' values='0'/></filter>"
                      "<rect width='240' height='240' filter='url(%23n)' opacity='0.30'/>"
                      "</svg>&quot;)"),
            'wash': ('radial-gradient(16% 8% at 16% 8%,rgba(168,90,60,.07) 0%,'
                     'rgba(168,90,60,0) 46%),radial-gradient(88% 94% at 88% 94%,'
                     'rgba(62,47,38,.06) 0%,rgba(62,47,38,0) 44%),'
                     'linear-gradient(180deg,rgba(214,168,91,.05) 0%,rgba(214,168,91,0) 30%)'),
            # ---- 纸纹/做旧晕（模板内 D-12 实体包裹 data-URI；点缀秋葵暖黄供 wash 用）----
            'warm_yellow': '#D6A85B',
            # ---- 头部三行标题群（闭式：14 + h1_gap + 68 + sub_gap + 13 = 162，🟡#2）----
            'head_top': 52, 'head_h': 162,
            'eyebrow_px': 14, 'eyebrow_letter': '0.34em', 'eyebrow_lh': 1.0,
            'h1_px': 68, 'h1_letter': '0.10em', 'h1_gap': 32,
            'h1_fit_w': 796,                     # fit 容器宽 = 版心宽 900 − 2×52（§2.4 fit 注）
            'sub_px': 13, 'sub_letter': '0.3em', 'sub_gap': 35, 'sub_lh': 1.0,
            'sub_color': '#7A6350',
            # ---- 照片卡纸（R4 终值 796×724；10px 卡纸 border-box + 双层投影）----
            'photo_left': 52, 'photo_top': 264, 'photo_w': 796, 'photo_h': 724,
            'photo_mat': 10, 'photo_mat_color': '#FBF6EC',
            'photo_shadow': '0 12px 30px rgba(62,47,38,.30), 0 3px 7px rgba(62,47,38,.20), '
                            'inset 0 0 0 1px rgba(62,47,38,.16)',
            # ---- 图注（1 行，R5）+ 发丝分隔线 ----
            'cap_top': 1004, 'cap_px': 11, 'cap_letter': '0.15em', 'cap_color': '#A85A3C',
            'rule_top': 1056, 'rule_side': 52,
            # ---- 手记行（箭头 SVG 恰 1 枚〔R2 保留枚〕+ EN 手写 + 中文小字）----
            'note_top': 1086, 'note_left': 52, 'note_w': 620,
            'note_px': 15, 'note_color': '#6B5344',
            'note_cn_px': 12, 'note_cn_color': '#8A6A55', 'note_cn_gap': 10, 'note_en_gap': 8,
            'arrow': {'w': 34, 'h': 29.24, 'rot': -22},
            # ---- 年份行（右对齐 flex：SVG 双实心三角标记 + 年份文字；J1 裁定 §2.4.1；
            #      窄缝 slit=2 = viewBox 资产常量，不设 layout 键，🔵#8）----
            'year_right': 52, 'year_top': 1098, 'year_lh': 1.0,
            'year_px': 12, 'year_letter': '0.2em', 'year_color': '#A85A3C',
            'year_mark_w': 24, 'year_mark_h': 12, 'year_mark_gap': 7,
            # ---- 凹压钢印 / 做旧邮戳（SVG 资产；几何/文字终值 §2.4 表）----
            'emboss': {'left': 56, 'top': 44, 'w': 100, 'h': 100, 'rot': -13},
            'postmark': {'right': 56, 'top': 32, 'w': 132, 'h': 120},
            # ---- 字体新增注入（D-4/D-5：手记中文小字宋 Regular / 手写注记霞鹜文楷 Regular）----
            'extra_fonts': ('SourceHanSerifRegular', 'LXGWWenKaiReg'),
            # ---- 装饰位固定文案（§2.5；城市/副标有固定兑底，通用标签非地名）----
            'fixed': {
                'eyebrow': 'MEMORY OF THE OLD TOWN',
                'sub': '纪录片系列 · DOCUMENTARY SERIES',
                'caption': 'Old Town Alley: Twilight Hour',
                'note_en': 'The smell of aged wood & rain.',
                'note_cn': '古镇的雨意与木香',
                'postmark_city': 'GUZHEN',
                'postmark_country': 'CHINA',
                'emboss_l1': 'EMBOSSED',
                'emboss_l2': 'ARCHIVE',
            },
        },
    ),

}

# 供 engine_v2 的 --genre choices 并入
DESIGN_IDS = list(DESIGN_CONFIGS)


if __name__ == '__main__':
    # 自检：字段全集（必填 + 可选）+ 数量 + template_id 映射完整性 + hero/text_on_photo 合法值
    _req = ('mode', 'template_id', 'topology', 'hero_zone', 'text_on_photo',
            'base_color', 'fonts', 'scale', 'palette', 'layout')
    _opt = ('tone_filter',)                  # 可选字段：照片调子（'' 无）
    _known = list(_req) + list(_opt)
    assert len(DESIGN_CONFIGS) == 19, f"config 数量应为 19，实际 {len(DESIGN_CONFIGS)}"

    bad = {g: [f for f in _req if f not in c] for g, c in DESIGN_CONFIGS.items()
           if not all(f in c for f in _req)}
    unknown = {g: [f for f in c if f not in _known] for g, c in DESIGN_CONFIGS.items()
               if any(f not in _known for f in c)}
    assert not bad, f"字段缺失: {bad}"
    assert not unknown, f"未知字段: {unknown}"

    # mode 必须为 'DESIGN'；template_id 一一对应且端点明确；
    # hero_zone / text_on_photo 逐款锁设计稿 §1 终值（不得偏离）
    _spec = {
        'pop_halftone':    ('_tpl_pop_halftone',    'bedrock_base',   'bottom_center', False),
        'kinfolk_air':     ('_tpl_kinfolk_air',     'face_portrait',  'bottom_card',   False),
        'museum_frame':    ('_tpl_museum_frame',    'matted_gallery', 'bottom_card',   False),
        'swiss_red_grid':  ('_tpl_swiss_red_grid',  'bedrock_base',   'bottom_center', True),
        'super_index':     ('_tpl_super_index',     'zenith_center',  'top_center',    False),
        'retro_tv':        ('_tpl_retro_tv',        'bedrock_base',   'bottom_center', False),
        # 彩活四款（2026-09-07，§1 终值锁死；street_zine 拓扑=bottom_right〔v2 修〕）
        'street_zine':     ('_tpl_street_zine',     'bottom_right',   'bottom_center', True),
        'duo_pop':         ('_tpl_duo_pop',         'bedrock_base',   'bottom_center', True),
        'doodle_summer':   ('_tpl_doodle_summer',   'bedrock_base',   'bottom_center', True),
        'collage_man':     ('_tpl_collage_man',     'face_portrait',  'bottom_center', False),
        # 构图三款（2026-09-08，§1 终值锁死；pop 二款 pop04d 渐隐/星群 seed=7 预计算）
        'branch_magazine': ('_tpl_branch_magazine', 'bottom_right',   'bottom_center', False),
        'pop_lichtenstein': ('_tpl_pop_lichtenstein', 'bedrock_base', 'bottom_center', True),
        'pop_press':       ('_tpl_pop_press',       'bedrock_base',   'bottom_center', True),
        'torn_journal':    ('_tpl_torn_journal',    'zenith_center',  'top_center',    True),
        'exhibition_poster': ('_tpl_exhibition_poster', 'zenith_center', 'top_center',  False),
        'torn_peephole':   ('_tpl_torn_peephole',   'zenith_center',  'top_center',    False),
        'torn_deckle':     ('_tpl_torn_deckle',     'zenith_center',  'top_center',    False),
        # 新款入库批（2026-09-16，docs/新款入库批-设计.md §2.1 终值锁死；均 zenith_center）
        'modern_spread':   ('_tpl_modern_spread',   'zenith_center',  'top_center',    False),
        'cultural_journal': ('_tpl_cultural_journal', 'zenith_center', 'top_center',   False),
    }
    for g, c in DESIGN_CONFIGS.items():
        tpl, topo, hero, ton = _spec[g]
        assert c['mode'] == 'DESIGN', f"{g} mode 应为 'DESIGN'，实际 {c['mode']!r}"
        assert c['template_id'] == tpl, f"{g} template_id 应为 {tpl!r}"
        assert c['topology'] == topo, f"{g} topology 应为 {topo!r}"
        assert c['hero_zone'] == hero, f"{g} hero_zone 应为 {hero!r}"
        assert c['text_on_photo'] is ton, f"{g} text_on_photo 应为 {ton}"
        assert set(c['base_color'].lower()) <= set('#0123456789abcdef') and len(c['base_color']) == 7, \
            f"{g} base_color 应为 #rrggbb"

    # 子字段全集
    _sub = {
        'fonts': ('hero', 'emotion', 'data'),
        'scale': ('hero_px', 'lead_px', 'micro_px', 'hero_lh', 'hero_letter', 'hero_shadow'),
        'palette': ('primary', 'accent', 'point'),
    }
    bad_sub = {g: {k: [f for f in v if f not in c[k]] for k, v in _sub.items()
                  if any(f not in c[k] for f in v)} for g, c in DESIGN_CONFIGS.items()
               if any(any(f not in c[k] for f in v) for k, v in _sub.items())}
    assert not bad_sub, f"子字段缺失: {bad_sub}"

    # scale 数值须为正数
    bad_scale = {g: {k: v for k, v in c['scale'].items() if k in ('hero_px', 'lead_px', 'micro_px')
                     and not (isinstance(v, (int, float)) and v > 0)} for g, c in DESIGN_CONFIGS.items()
                 if any(k in ('hero_px', 'lead_px', 'micro_px')
                        and not (isinstance(v, (int, float)) and v > 0)
                        for k, v in c['scale'].items())}
    assert not bad_scale, f"scale 数值须为正: {bad_scale}"

    assert len(DESIGN_IDS) == 19, "DESIGN_IDS 应为 19"
    # 彩活四款专项：duo_pop 12 圆点 + P4 词池 24 词 + P3 云朵三枚（§1/§0.5 数值入 config 自检）
    _d = DESIGN_CONFIGS['duo_pop']['layout']['dots']
    assert len(_d) == 12, f"duo_pop 圆点应为 12 颗（v3 定稿），实际 {len(_d)}"
    cm = DESIGN_CONFIGS['collage_man']['layout']
    assert len(cm['words_a']) == 12 and len(cm['words_b']) == 12, "P4 词池应 A+B 各 12 词"
    assert len(cm['wall_sizes']) == 5, "P4 词墙应五档字号"
    assert abs(sum(cm['wall_ratio'].values()) - 0.36) < 1e-9, "P4 四类形态占比应合计 36%（常规 64%）"
    assert len(DESIGN_CONFIGS['doodle_summer']['layout']['clouds']) == 3, "P3 云朵应三枚"
    assert DESIGN_CONFIGS['branch_magazine']['layout']['win_right'] == 30, \
        "branch_magazine 内窗 right=30（A4 源码勘误值，竖排小字完整入画的前提）"
    # 构图三款专项（§1 数值入 config 自检）：星群 12 颗/花枝坐标表 14 件/fg_texts dict 形态
    _pl = DESIGN_CONFIGS['pop_lichtenstein']['layout']
    assert len(_pl['stars']) == 12, f"pop_lichtenstein 星群应 12 颗，实际 {len(_pl['stars'])}"
    assert all(-35 <= s['rot'] <= 35 for s in _pl['stars']), "星群转角应预计算在 ±35° 内（seed=7）"
    _bm = DESIGN_CONFIGS['branch_magazine']['layout']
    assert len(_bm['branch_paths']) == 14, "branch_magazine 花枝坐标表应 14 件（枝1+叶4+花苞9）"
    assert _bm['win_right'] == 30, "branch_magazine 内窗 right=30（A4 源码勘误值，不得改回 -20）"
    # 微调批3（2026-09-15）固定追加三条：容器双值 + 竖排小字移量 + 照片框下文字位
    assert _bm['win_outer_w'] == 864 and _bm['win_outer_h'] == 864, \
        "branch_magazine 外裁剪容器应 864×864（微调批3 A#1a：828→864，装下 rotate(-8°) 包围盒 840.3px）"
    assert _bm['vtext_right'] == 50, \
        "branch_magazine 竖排小字 right=50（微调批3 A#1b：64→50 右移 14px，脱离内窗叠压）"
    assert DESIGN_CONFIGS['pop_halftone']['layout']['hero_bottom'] == 86, \
        "pop_halftone hero_bottom=86（微调批3 A#3：96→86，照片框下两行文字整体下移 10%）"
    # 撕纸手帐专项（2026-09-09，§1.3 终值锁死）：点表/飞点/生成参数
    _tj = DESIGN_CONFIGS['torn_journal']['layout']
    assert len(_tj['torn_inner']) == len(_tj['torn_outer']) > 200, \
        f"torn_journal 内外环点数应相等且 >200，实际 {len(_tj['torn_inner'])}/{len(_tj['torn_outer'])}"
    assert len(_tj['flecks']) == 46, f"torn_journal 纤维飞点应 46 条，实际 {len(_tj['flecks'])}"
    assert _tj['torn_params']['cap_bite'] == (70, 100), "torn_journal 深咬口应 (70,100)"
    assert _tj['torn_params']['side'] == (30, 40), "torn_journal 白边 side 应 (30,40)"
    # 展览海报专项（2026-09-10，§1.3 终值锁死）：帧几何/竖排 px/主标字体
    _ep = DESIGN_CONFIGS['exhibition_poster']['layout']
    assert _ep['img_w'] == 710 and _ep['img_h'] == 820, "exhibition_poster 照片窗应 710×820"
    assert _ep['img_x'] == 94 and _ep['img_y'] == 252, "exhibition_poster 照片窗左上应 (94,252)"
    assert _ep['v_name_px'] == 50, "exhibition_poster 竖排大字应 50px（霞鹜文楷）"
    assert _ep['wing_w'] == 94, "exhibition_poster 左右竖排翼应 94px"
    assert DESIGN_CONFIGS['exhibition_poster']['fonts']['hero'] == 'SourceSerifHeavy', \
        "exhibition_poster 主标字体应 SourceSerifHeavy（基础常量零新增分支）"
    assert DESIGN_CONFIGS['exhibition_poster']['fonts']['emotion'] == 'LXGWWenKai', \
        "exhibition_poster 竖排大字应 LXGWWenKai"
    assert DESIGN_CONFIGS['exhibition_poster']['text_on_photo'] is False, \
        "exhibition_poster 应护脸安全（text_on_photo=False）"
    for g, c in DESIGN_CONFIGS.items():
        ft = c['layout'].get('fg_texts')
        if ft is not None:
            if isinstance(ft, dict):
                assert all(isinstance(v, str) and v for v in ft.values()), f"{g} fg_texts dict 值应为字体名"
            else:
                assert all(isinstance(v, str) for v in ft), f"{g} fg_texts tuple 应为键名序列"
    print(f"design_configs OK · {len(DESIGN_CONFIGS)} 款 · 字段全集(必填{len(_req)}+可选{len(_opt)})"
          f" · mode=('DESIGN'×{len(DESIGN_CONFIGS)}) · "
          f"护脸款{sum(1 for c in DESIGN_CONFIGS.values() if not c['text_on_photo'])}/{len(DESIGN_CONFIGS)}")
