#!/usr/bin/env python3
# 版式配方数据表（阶段一补齐：9 套实测流派）
# 每条配方是一个 dict，供 render_engine.py 生成 HTML。
# 参数来源：D:/dsh\ 实测 render_*.py / proto_*.html 的提炼，非臆造。
# 字体路径为真实存在的 D:/dsh\fonts 文件（已核对）。
# 第 3 条之后为阶段一补齐的 6 个新流派（#3/#7/#9/#17/#22/#28）。

FONTS_DIR = 'D:/dsh/fonts'

# ---- @font-face 加载（用 file:/// 绝对路径，chrome headless 可读）----
FONTS_CSS = f'''
@font-face {{ font-family: "BodoniModa"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BodoniModa-Bold.ttf"); }}
@font-face {{ font-family: "CinzelBold"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Cinzel-Bold.ttf"); }}
@font-face {{ font-family: "SpaceMono"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/SpaceMono-Bold.ttf"); }}
@font-face {{ font-family: "Italiana"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Italiana-Regular.ttf"); }}
@font-face {{ font-family: "PlayfairBold"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/PlayfairDisplay-Bold.ttf"); }}
@font-face {{ font-family: "PlayfairItalic"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/PlayfairDisplay-Italic.ttf"); }}
@font-face {{ font-family: "CormorantItalic"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/CormorantGaramond-Italic.ttf"); }}
@font-face {{ font-family: "SourceSerifHeavy"; src: url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Heavy-4.otf"); }}
@font-face {{ font-family: "LXGWWenKai"; src: url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf"); }}
@font-face {{ font-family: "YanShiQiuHong"; src: url("file:///{FONTS_DIR}/免费商用书法字体/演示秋鸿楷2.0.ttf"); }}
@font-face {{ font-family: "YouSheBiaoTiHei"; src: url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/优设系列/优设标题黑.ttf"); }}
'''

SERIF_CN = '"Songti SC","Source Han Serif SC","SimSun","Noto Serif CJK SC",serif'
SANS_CN = '"PingFang SC","Source Han Sans SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif'

# ---- 阶段一 3 条配方 ----
# 每条: flow_id / family / blueprint_id / topology / fonts / scale / anti_camouflage
#       / palette / decor / z_layers / layout(引擎生成 HTML 的骨架参数)
FLOWS = {
    # ===== #1 时尚夜曲封面 (Nocturne / Vogue) =====
    'nocturne_vogue': {
        'family': 'hero_masthead',
        'blueprint_id': 1,
        'topology': 'zenith_center',
        'fonts': {'hero': 'BodoniModa', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        'scale': {'hero_px': 220, 'lead_px': 54, 'micro_px': 9.5,
                  'hero_lh': 0.75, 'hero_letter': '0.08em', 'hero_shadow': '0 4px 30px rgba(0,0,0,0.95)'},
        'palette': {'primary': '#060504', 'accent': '#fcf6ee', 'point': '#d49b6a'},
        'z_layers': {'bg': 1, 'shade': 2, 'masthead': 5, 'subject_overlap': 10, 'caption': 20},
        'layout': {
            'masthead_top_px': 55,          # 刊头 top
            'shade_height_ratio': 0.28,     # 顶部墨韵渐变高度占画布比例
            'shade_grad': 'linear-gradient(180deg, rgba(6,5,4,0.85) 0%, rgba(6,5,4,0.4) 65%, transparent 100%)',
            'subtitle_top_ratio': 0.11,     # 中文副标 top 比例
            'caption_bottom_ratio': 0.08,   # 底部图说卡 bottom 比例
            'issn': 'ISSN 2608-8848',       # 条形码文字
        },
    },

    # ===== #5 东方泼墨长卷 (Zen Landscape) =====
    'zen_landscape': {
        'family': 'oriental_calligraphy',
        'blueprint_id': 5,
        'topology': 'right_wing_axis',
        'fonts': {'hero': 'SourceSerifHeavy', 'emotion': 'YanShiQiuHong', 'data': 'SpaceMono'},
        'scale': {'hero_px': 148, 'lead_px': 38, 'micro_px': 9.5,
                  'hero_lh': 0.95, 'hero_letter': '0.18em', 'hero_shadow': '0 1px 0 rgba(255,255,255,0.9)'},
        'palette': {'primary': '#111518', 'accent': '#222830', 'point': '#b83c23'},
        'z_layers': {'bg': 1, 'calligraphy': 20, 'caption': 20},
        'layout': {
            'calligraphy_top_px': 70,
            'calligraphy_right_px': 110,
            'col_gap_px': 58,               # 竖排列间距
            'lead_margin_top_px': 140,
            'meta_margin_top_px': 260,
            'seal_pos': 'bottom-left',      # 朱印位置
            'seal_rotate': -2,              # 朱印旋转角
        },
    },

    # ===== #8 汉唐金石重器典藏 (Imperial Han Splendor) =====
    'imperial_han': {
        'family': 'oriental_calligraphy',
        'blueprint_id': 8,
        'topology': 'zenith_center',
        'fonts': {'hero': 'CinzelBold', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        'scale': {'hero_px': 260, 'lead_px': 64, 'micro_px': 11,
                  'hero_lh': 0.75, 'hero_letter': '0.04em', 'hero_shadow': '0 10px 40px rgba(0,0,0,0.9)',
                  'hero_color': 'rgba(212,175,55,0.85)'},
        'palette': {'primary': '#000', 'accent': '#d4af37', 'point': '#c43d2f'},
        'z_layers': {'bg': 1, 'masthead': 20, 'subtitle': 25, 'footnote': 30},
        'layout': {
            'masthead_top_px': 40,
            'masthead_center': True,        # 全幅居中
            'subtitle_top_ratio': 0.12,
            'footnote_bottom_px': 35,
            'seal_pos': 'right',            # 南博朱印位置
            'seal_red': '#c43d2f',          # 朱砂
            'seal_grid': ['南', '博', '珍', '藏'],  # 2×2 田字格白文印（繁体全字库）
            'gold_hex': '#D4AF37',
        },
    },

    # ===== #3 先锋大字街拍 (Pulp Street) =====
    'pulp_street': {
        'family': 'hero_masthead',
        'blueprint_id': 3,
        'topology': 'zenith_center',
        'fonts': {'hero': 'YouSheBiaoTiHei', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        'scale': {'hero_px': 160, 'lead_px': 40, 'micro_px': 10.5,
                  'hero_lh': 0.92, 'hero_letter': '0.02em', 'hero_shadow': '0 6px 24px rgba(0,0,0,0.95)'},
        'palette': {'primary': '#101013', 'accent': '#f5f3ec', 'point': '#d49b6a'},
        'z_layers': {'bg': 1, 'shade': 2, 'masthead': 5, 'subject_overlap': 10, 'caption': 20},
        'layout': {
            'shade_height_ratio': 0.32,     # 顶部墨韵渐变（防吞没）
            'shade_grad': 'linear-gradient(180deg, rgba(16,16,19,0.95) 0%, rgba(16,16,19,0.55) 58%, transparent 100%)',
            'hdr_top_px': 38,               # 顶部刊头（ISSUE / VOL 小字）
            'title_top_ratio': 0.115,       # 主标 top 比例（居中偏上）
            'sub_gap_ratio': 0.30,          # 副标 top 比例
            'toc_bottom_ratio': 0.105,      # TOC 目录舱 bottom
            'caption_bottom_ratio': 0.065,  # 底部参数卡 bottom
            'issueno': 'RESCUE PHOTO · 影像档案',
            'issue_meta': 'ISSUE 08 · VOL. XXVI',
            'badge': 'NO.08',
            'toc': ['石佛造像', '千年身姿', '南朝石韵', '指尖光影', '观照'],
            'masthead_brand': 'RESCUE PHOTO STUDY',
        },
    },

    # ===== #7 宣纸金石碑拓 (Stone Inscription) =====
    'stone_inscription': {
        'family': 'oriental_calligraphy',
        'blueprint_id': 7,
        'topology': 'bottom_right_stamp',
        # 繁体验证点：标题用繁体，必须用全字库 SourceSerifHeavy（思源宋特粗）承载；
        # emotion=LXGWWenKai（霞鹜文楷，全字库）；严禁用秋鸿楷/春风楷（简字库缺繁体）。
        'fonts': {'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        'scale': {'hero_px': 156, 'lead_px': 40, 'micro_px': 12,
                  'hero_lh': 1.0, 'hero_letter': '0.30em', 'hero_shadow': '0 2px 6px rgba(0,0,0,0.4)'},
        'palette': {'primary': '#17130d', 'accent': '#f3ead8', 'point': '#b83c23'},
        'z_layers': {'bg': 1, 'wash': 5, 'calligraphy': 20, 'frame': 10, 'seal': 30},
        'layout': {
            'title_top_px': 70,             # 竖排主标 top
            'title_left_px': 60,            # 竖排主标 left（主体在右，落左侧负空间）
            'col_gap_px': 52,               # 竖排列间距
            'lead_margin_top_px': 120,      # 款落款 top 偏移
            'seal_size_ratio': 0.55,        # 印宽 ≤ 主标字高 × 0.55（P0-3 比例上限）
            'seal_rotate': -3,              # 印微转
            'seal_grid': ['金', '石', '永', '固'],  # 2×2 田字格白文印（铺满）
            'frame_border': 'repeating-linear-gradient(45deg, rgba(212,175,55,.055) 0 10px, transparent 10px 20px)',
            'ink_color': '#1c150c',         # 墨色
        },
    },

    # ===== #9 胶片齿孔档案卷 (Film / RSX) =====
    'film_rsx': {
        'family': 'film',
        'blueprint_id': 9,
        'topology': 'right_wing_axis',
        # emotion=桑体/宋体（系统，标题）/ data=Courier New（工业印字 AGFA / 帧号）
        'fonts': {'hero': 'Songti SC', 'emotion': 'Songti SC', 'data': 'Courier New'},
        'scale': {'hero_px': 96, 'lead_px': 30, 'micro_px': 12,
                  'hero_lh': 1.0, 'hero_letter': '0.10em', 'hero_shadow': '0 1px 4px rgba(0,0,0,0.6)'},
        'palette': {'primary': '#241a12', 'accent': '#e8d9b8', 'point': '#ff9a3c'},
        'z_layers': {'bg': 1, 'film': 4, 'grain': 6, 'title': 10, 'cap': 12},
        'layout': {
            'edge_w': 56,                   # 齿孔带宽（px）
            'hole_w': 28,                   # 齿孔宽
            'hole_h': 38,                   # 齿孔高
            'hole_r': 6,                    # 齿孔圆角
            'hole_gap': 107,                # 齿孔间距
            'sepia': 0.55,                  # 暖褐调
            'brand': 'AGFA-GEVAERT',        # 工业印字
            'film_type': 'RSX-II',
            'frame_no': '24A',
            'title_left_px': 150,           # 标题 left（避开左右齿孔带）
            'title_top_px': 90,
        },
    },

    # ===== #17 压底穿插 (Layered Underneath) =====
    'layered_underneath': {
        'family': 'spatial',
        'blueprint_id': 17,
        'topology': 'right_wing_axis',
        # 印章禁用点（P0-3）：现代流派禁用传统红印章，改用几何标贴/条形码/钢印。
        'fonts': {'hero': 'CinzelBold', 'data': 'SpaceMono'},
        'scale': {'hero_px': 300, 'lead_px': 30, 'micro_px': 11,
                  'hero_lh': 0.9, 'hero_letter': '0.02em', 'hero_shadow': '0 16px 60px 12px rgba(0,0,0,0.75)'},
        'palette': {'primary': '#0d0d0f', 'accent': '#f2efe8', 'point': '#d49b6a'},
        # z 分层：巨字 10 + 主图 20（主体在字前）+ 文案 30
        'z_layers': {'bg': 1, 'giant': 10, 'photo': 20, 'caption': 30},
        'layout': {
            'giant_word': 'BUDDHA',         # Cinzel 巨字（拉丁；主体佛像在右侧，文字落左侧负空间）
            'giant_top_ratio': 0.40,        # 巨字 top 比例
            'giant_left_px': -80,           # 巨字 left（可负，压入画外）
            'giant_angle': -4,              # 巨字微倾
            'badge_text': 'MATERIAL ARCHIVE',
            'caption_bottom_px': 60,
        },
    },

    # ===== #22 君临天幕帝国 (Monumental Sky) =====
    'monumental_sky': {
        'family': 'heavenly_dome',
        'blueprint_id': 22,
        'topology': 'zenith_center',
        'fonts': {'hero': 'CinzelBold', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        'scale': {'hero_px': 260, 'lead_px': 58, 'micro_px': 12,
                  'hero_lh': 0.85, 'hero_letter': '0.03em', 'hero_shadow': '0 20px 70px rgba(0,0,0,0.85)',
                  'hero_color': 'rgba(212,175,55,0.85)'},  # 半透明金
        'palette': {'primary': '#000', 'accent': '#d4af37', 'point': '#fff'},
        'z_layers': {'bg': 1, 'masthead': 20, 'subtitle': 25, 'footnote': 30},
        'layout': {
            'masthead_top_px': 40,          # 全幅居中、顶置（top:40）
            'title_center': True,
            'subtitle_top_ratio': 0.34,     # 副标（白字黑晕）
            'footnote_bottom_px': 40,       # 注脚
            'gold_hex': '#D4AF37',
        },
    },

    # ===== #28 科考标本参数卡 (Specimen Field) =====
    'specimen_field': {
        'family': 'scientific',
        'blueprint_id': 28,
        'topology': 'matted_gallery',
        # emotion=PingFang/SourceHanSans（中文主标 900）/ data=Courier New（参数卡）
        # 点睛=Helvetica（栏目小标）
        'fonts': {'hero': 'PingFang SC', 'emotion': 'PingFang SC', 'data': 'Courier New', 'point': 'Helvetica'},
        'scale': {'hero_px': 64, 'lead_px': 30, 'micro_px': 13,
                  'hero_lh': 1.0, 'hero_letter': '0.06em', 'hero_shadow': '0 0 0 rgba(0,0,0,0)'},
        'palette': {'primary': '#12161a', 'accent': '#e9ecef', 'point': '#8ad1a8'},
        'z_layers': {'bg': 1, 'photo': 10, 'crosshair': 15, 'arch': 20},
        'layout': {
            'photo_top_ratio': 0.0,         # 照片窗 top
            'photo_height_ratio': 0.82,     # 上部约 82% 照片窗（放大给主体）
            'arch_top_ratio': 0.83,         # 档案卡 top（下移缩小）
            'arch_height_ratio': 0.17,      # 档案卡 17%（展签级，≤18%，照片让位主体）
            'grid_cols': 4,                 # 4 栏等宽数据卡
            'title_frame': 'SPECIMEN FIELD RECORD',
        },
    },
}

# ---- 流派有限选择（供 CLI 提示）----
FLOW_CHOICES = ['nocturne_vogue', 'zen_landscape', 'imperial_han',
                'pulp_street', 'stone_inscription', 'film_rsx',
                'layered_underneath', 'monumental_sky', 'specimen_field']
