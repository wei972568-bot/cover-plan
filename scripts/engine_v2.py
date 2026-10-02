#!/usr/bin/env python3
# 版式引擎 v2 · 13 套精品流派（GENRE 驱动；TOPOLOGY/MATERIAL 为登记表，不驱动自由组合）
# 9 套原流派 + 4 套新增（bauhaus/dual_portals/blue_note/slender_zen）。—— B11 已删 nordic。
# 独立新文件，不破坏 flows.py / render_engine.py（可对照/回退）。
import argparse, os, shutil, hashlib, base64, html as _html

# ---- 装裱/影格流派族接入（仅分发，不改 14 套旧逻辑）----
from matting_configs import MATTING_CONFIGS, MATTING_IDS, MATTING_ALIAS
import matting_engine
# ---- 载体隐喻流派族接入（仅分发，不改 14 套旧逻辑）----
from metaphor_configs import METAPHOR_CONFIGS, METAPHOR_IDS
import metaphor_engine
# ---- 蓝图补齐流派族接入（仅分发，不改 14 套旧逻辑）----
from blueprint_configs import BLUEPRINT_CONFIGS, BLUEPRINT_IDS
import blueprint_engine
from design_configs import DESIGN_CONFIGS, DESIGN_IDS
import design_engine
# ---- 共享排版守卫（收敛宽度自适应 / 落点亮度对比 / clip-safe）----
from type_guard import fit_title_fs, luma, readability, clip_safe

SIZES = {'3:4':(1080,1350),'4:3':(1350,1080),'16:9':(1350,759),'9:16':(759,1350),'1:1':(1080,1080)}

# ---- 字体（复用 flows 的 FONTS_CSS 思路，硬编码路径）----
FONTS_DIR = 'D:/dsh/fonts'
FONTS_CSS = f'''
@font-face {{ font-family: "BodoniModa"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/BodoniModa-Bold.ttf"); }}
@font-face {{ font-family: "CinzelBold"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Cinzel-Bold.ttf"); }}
@font-face {{ font-family: "SpaceMono"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/SpaceMono-Bold.ttf"); }}
@font-face {{ font-family: "Italiana"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Italiana-Regular.ttf"); }}
@font-face {{ font-family: "PlayfairBold"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/PlayfairDisplay-Bold.ttf"); }}
@font-face {{ font-family: "CormorantItalic"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/CormorantGaramond-Italic.ttf"); }}
@font-face {{ font-family: "SourceSerifHeavy"; src: url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Heavy-4.otf"); }}
@font-face {{ font-family: "LXGWWenKai"; src: url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf"); }}
@font-face {{ font-family: "YanShiQiuHong"; src: url("file:///{FONTS_DIR}/免费商用书法字体/演示秋鸿楷2.0.ttf"); }}
@font-face {{ font-family: "YouSheBiaoTiHei"; src: url("file:///{FONTS_DIR}/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/优设系列/优设标题黑.ttf"); }}
@font-face {{ font-family: "ArchivoBlack"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/ArchivoBlack-Regular.ttf"); }}
@font-face {{ font-family: "BarlowCondensed-Black"; src: url("file:///{FONTS_DIR}/Barlow-Condensed-Medium/barlowcondensed/BarlowCondensed-Black.ttf"); }}
@font-face {{ font-family: "Oswald"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Oswald.ttf"); }}
@font-face {{ font-family: "Syne"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Syne-ExtraBold.ttf"); }}
@font-face {{ font-family: "Unbounded"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/Unbounded-Black.ttf"); }}
@font-face {{ font-family: "SourceSerifCN-Light"; src: url("file:///{FONTS_DIR}/SiYuanSongTiRegular/SourceHanSerifCN-Light-5.otf"); }}
@font-face {{ font-family: "CormorantGaramond-Italic"; src: url("file:///{FONTS_DIR}/精选西文大刊与特色开源/CormorantGaramond-Italic.ttf"); }}
'''
SERIF_CN = '"Songti SC","Source Han Serif SC","SimSun","Noto Serif CJK SC",serif'
SANS_CN = '"PingFang SC","Source Han Sans SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif'

# ---- 胶片颗粒（供 film 流派使用）----
_GRAIN = ("<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
          "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.4' numOctaves='3'/>"
          "<feColorMatrix type='saturate' values='0'/></filter>"
          "<rect width='300' height='300' filter='url(#n)' opacity='0.7'/></svg>")
GRAIN_URI = 'data:image/svg+xml;base64,' + base64.b64encode(_GRAIN.encode()).decode()

# ================= TOPOLOGY_REGISTRY（8 槽位） =================
TOPOLOGY = {
    'zenith_center': {'label':'正中天穹','pos':'top_center','main':'X50% Y5-25%'},
    'bedrock_base': {'label':'底部泰山','pos':'bottom_center','main':'X50% Y70-95%'},
    'right_wing': {'label':'右翼竖轴','pos':'right_vertical','main':'X60-95%'},
    'dual_poles': {'label':'天地双极','pos':'top_bottom','main':'Y5%+Y85%'},
    'bottom_left': {'label':'左下锚点','pos':'bottom_left','main':'X5-45% Y65-88%'},
    'perimeter_orbit': {'label':'四周环绕','pos':'perimeter','main':'沿边10px'},
    'bottom_right': {'label':'右下印章','pos':'bottom_right','main':'X55-90% Y70-90%'},
    'matted_gallery': {'label':'画廊卡纸','pos':'matted','main':'照片居中+下方卡'},
}

# ================= MATERIAL_REGISTRY（材质装裱族） =================
MATERIAL = {
    'none': {'label':'无边框','layer':'none'},
    'oriental_cloud': {'label':'东方云雷纹','layer':'gold_frame','pattern':'repeating-linear-gradient(45deg, rgba(212,175,55,.055) 0 10px, transparent 10px 20px)'},
    'film_rsx': {'label':'35mm胶片','layer':'film'},
    'matted_paper': {'label':'米白卡纸','layer':'paper_matte'},
    'black_gallery': {'label':'典藏黑框','layer':'black_gallery'},
}

# ================= GENRE_REGISTRY（流派叙事，9 套全部迁入） =================
GENRE = {
    'zen': {
        'blueprint_id': 5, 'label':'东方泼墨',
        'default_topology':'right_wing', 'default_material':'oriental_cloud',
        'fonts': {'hero':'SourceSerifHeavy','emotion':'YanShiQiuHong','data':'SpaceMono'},
        'scale': {'hero_px':148,'lead_px':38,'micro_px':9.5,'hero_lh':0.95,'hero_letter':'0.18em','hero_shadow':'0 1px 0 rgba(255,255,255,0.9)'},
        'palette': {'primary':'#111518','accent':'#222830','point':'#b83c23'},
        'layout': {'calligraphy_top_px':70,'calligraphy_right_px':44,'col_gap_px':58,   # 2026-09-25 用户修单：主标组左移（110→44 ×0.9=40 贴副标 left6，15%画布=135px 会出界，取可行域极限）
                   'lead_margin_top_px':140,'meta_margin_top_px':260,'seal_rotate':-2,
                   'seal_chars':['石','佛','無','言']},
        'z_layers': {'bg':1,'calligraphy':20,'caption':20},
    },
    'pulip': {
        'blueprint_id': 3, 'label':'先锋街拍',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'YouSheBiaoTiHei','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':150,'lead_px':40,'micro_px':10.5,'hero_lh':0.92,'hero_letter':'0.62em','hero_shadow':'0 2px 5px rgba(10,10,12,.85),0 0 1px rgba(10,10,12,.9)'},
        'palette': {'primary':'#101013','accent':'#f5f3ec','point':'#d49b6a'},
        'layout': {'shade_height_ratio':0.32,'hdr_top_px':38,'title_top_ratio':0.115,
                   'sub_gap_ratio':0.19,'toc_bottom_ratio':0.105,'caption_bottom_ratio':0.065,
                   'issueno':'RESCUE PHOTO · 影像档案','issue_meta':'ISSUE 08 · VOL. XXVI','badge':'NO.08',
                   'toc':['本期精选','编辑手记','城市漫游','光影笔记','时光切片'],'masthead_brand':'RESCUE PHOTO STUDY'},
        'z_layers': {'bg':1,'shade':2,'masthead':5,'subject_overlap':10,'caption':20},
    },
    'bauhaus': {
        'blueprint_id': 4, 'label':'包豪斯几何大刊',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'ArchivoBlack','emotion':'SourceSerifHeavy','data':'BarlowCondensed-Black'},
        'scale': {'hero_px':150,'lead_px':42,'micro_px':11,'hero_lh':0.9,'hero_letter':'0.01em','hero_shadow':'0 4px 18px rgba(0,0,0,0.55)'},
        'palette': {'primary':'#121212','accent':'#D52B1E','point':'#F4F1EA'},
        'layout': {'masthead_top_px':44,'title_top_ratio':0.085,'sub_top_ratio':0.208,'grid_cols':4,
                   'rule_h':3,'issue':'BAUHAUS 04 · MODERNIST','foot':'GEOMETRIC GRID · RED/NOIR'},
        'z_layers': {'bg':1,'masthead':5,'subtitle':8,'geometry':12,'caption':20},
    },
    'dual_portals': {
        'blueprint_id': 23, 'label':'天地双极巨门',
        'default_topology':'dual_poles', 'default_material':'none',
        'fonts': {'hero':'SourceSerifHeavy','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':150,'lead_px':44,'micro_px':11,'hero_lh':0.9,'hero_letter':'0.092em','hero_shadow':'0 6px 26px rgba(0,0,0,0.8)'},
        'palette': {'primary':'#0d0d0e','accent':'#e8e4da','point':'#b8b2a6'},
        'layout': {'top_max_top_ratio':0.055,'top_title_fs':150,'bot_max_bottom_ratio':0.055,'bot_title_fs':162,
                   'mid_frame':40,'foot_bottom_ratio':0.028,'brand':'天地 雙極'},
        'z_layers': {'bg':1,'top':20,'bottom':20,'foot':30},
    },
    'blue_note': {
        'blueprint_id': 26, 'label':'Blue Note 爵士黑胶封套',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'Unbounded','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':96,'lead_px':30,'micro_px':10,'hero_lh':0.95,'hero_letter':'0.04em','hero_shadow':'0 4px 18px rgba(0,0,0,0.4)'},
        'palette': {'primary':'#0B1F3A','accent':'#FF4A1F','point':'#F5F1E8'},
        'layout': {'beam_top_px':34,'beam_h':64,'title_top_ratio':0.07,'track_bottom_ratio':0.075,'rpm':'33⅓ RPM · STEREO','cat':'BLP 0402 · A'},
        'z_layers': {'bg':1,'beam':10,'title':20,'track':30},
    },
    'slender_zen': {
        'blueprint_id': 6, 'label':'日系清秀手札',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'SourceSerifCN-Light','emotion':'LXGWWenKai','data':'CormorantGaramond-Italic'},
        'scale': {'hero_px':128,'lead_px':30,'micro_px':11,'hero_lh':1.02,'hero_letter':'0.14em','hero_shadow':'0 1px 0 rgba(255,255,255,0.85)'},
        'palette': {'primary':'#2b2b2b','accent':'#454545','point':'#9a9a9a'},
        'layout': {'mast_top_px':64,'title_right_px':80,'lead_margin_top_px':120,'poem_margin_top_px':210,
                   'song_lines':['静 け さ','光 と 影','時 の 面 影'],'seal_chars':['春','風','一','葉']},
        'z_layers': {'bg':1,'masthead':20,'poem':22,'seal':25},
    },
    'monumental': {
        'blueprint_id': 22, 'label':'君临天幕',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'CinzelBold','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':260,'lead_px':58,'micro_px':12,'hero_lh':0.85,'hero_letter':'0.03em','hero_shadow':'0 20px 70px rgba(0,0,0,0.85)','hero_color':'rgba(212,175,55,0.85)'},
        'palette': {'primary':'#000','accent':'#d4af37','point':'#fff'},
        'layout': {'masthead_top_px':40,'title_center':True,'subtitle_top_ratio':0.22,'footnote_bottom_px':40,'gold_hex':'#D4AF37'},
        'z_layers': {'bg':1,'masthead':20,'subtitle':25,'footnote':30},
    },
    'nocturne': {
        'blueprint_id': 1, 'label':'时尚夜曲',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'BodoniModa','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':220,'lead_px':54,'micro_px':9.5,'hero_lh':0.75,'hero_letter':'0.08em','hero_shadow':'0 4px 30px rgba(0,0,0,0.95)'},
        'palette': {'primary':'#060504','accent':'#fcf6ee','point':'#d49b6a'},
        'layout': {'masthead_top_px':55,'shade_height_ratio':0.28,
                   'shade_grad':'linear-gradient(180deg, rgba(6,5,4,0.85) 0%, rgba(6,5,4,0.4) 65%, transparent 100%)',
                   'subtitle_top_ratio':0.11,'caption_bottom_ratio':0.08,'issn':'ISSN 2608-8848'},
        'z_layers': {'bg':1,'shade':2,'masthead':5,'subject_overlap':10,'caption':20},
    },
    'imperial': {
        'blueprint_id': 8, 'label':'汉唐金石',
        'default_topology':'zenith_center', 'default_material':'none',
        'fonts': {'hero':'CinzelBold','emotion':'SourceSerifHeavy','data':'SpaceMono'},
        'scale': {'hero_px':260,'lead_px':64,'micro_px':11,'hero_lh':0.75,'hero_letter':'0.04em','hero_shadow':'0 10px 40px rgba(0,0,0,0.9)','hero_color':'rgba(212,175,55,0.85)'},
        'palette': {'primary':'#000','accent':'#d4af37','point':'#c43d2f'},
        'layout': {'masthead_top_px':40,'masthead_center':True,'subtitle_top_ratio':0.13,
                   'footnote_bottom_px':35,'seal_pos':'right','seal_red':'#c43d2f',
                   'seal_grid':['御','园','清','赏'],'gold_hex':'#D4AF37'},
        'z_layers': {'bg':1,'masthead':20,'subtitle':25,'footnote':30},
    },
    'stone': {
        'blueprint_id': 7, 'label':'金石碑拓',
        'default_topology':'right_wing', 'default_material':'oriental_cloud',
        'fonts': {'hero':'SourceSerifHeavy','emotion':'LXGWWenKai','data':'SpaceMono'},
        'scale': {'hero_px':156,'lead_px':40,'micro_px':12,'hero_lh':1.0,'hero_letter':'0.30em','hero_shadow':'0 2px 6px rgba(0,0,0,0.4)'},
        'palette': {'primary':'#17130d','accent':'#f3ead8','point':'#b83c23'},
        'layout': {'title_top_px':70,'title_left_px':60,'col_gap_px':52,'lead_margin_top_px':120,
                   'seal_size_ratio':0.55,'seal_rotate':-3,'seal_grid':['石','上','花','开'],
                   'frame_border':'repeating-linear-gradient(45deg, rgba(212,175,55,.055) 0 10px, transparent 10px 20px)',
                   'ink_color':'#1c150c'},
        'z_layers': {'bg':1,'wash':5,'calligraphy':20,'frame':10,'seal':30},
    },
    'film': {
        'blueprint_id': 9, 'label':'胶片齿孔',
        'default_topology':'right_wing', 'default_material':'film_rsx',
        'fonts': {'hero':'Songti SC','emotion':'Songti SC','data':'Courier New'},
        'scale': {'hero_px':96,'lead_px':30,'micro_px':12,'hero_lh':1.0,'hero_letter':'0.10em','hero_shadow':'0 1px 4px rgba(0,0,0,0.6)'},
        'palette': {'primary':'#241a12','accent':'#e8d9b8','point':'#ff9a3c'},
        'layout': {'edge_w':56,'hole_w':28,'hole_h':38,'hole_r':6,'hole_gap':107,'sepia':0.55,
                   'brand':'AGFA-GEVAERT','film_type':'RSX-II','frame_no':'24A',
                   'title_left_px':150,'title_top_px':90},
        'z_layers': {'bg':1,'film':4,'grain':6,'title':10,'cap':12},
    },
    'layered': {
        'blueprint_id': 17, 'label':'压底穿插',
        'default_topology':'right_wing', 'default_material':'none',
        'fonts': {'hero':'CinzelBold','data':'SpaceMono'},
        'scale': {'hero_px':300,'lead_px':30,'micro_px':11,'hero_lh':0.9,'hero_letter':'0.02em','hero_shadow':'0 16px 60px 12px rgba(0,0,0,0.75)'},
        'palette': {'primary':'#0d0d0f','accent':'#f2efe8','point':'#d49b6a'},
        'layout': {'giant_word':'LAYERS','giant_top_ratio':0.40,'giant_left_px':-80,'giant_angle':-4,
                   'badge_text':'MATERIAL ARCHIVE','caption_bottom_px':60},
        'z_layers': {'bg':1,'giant':10,'photo':20,'caption':30},
    },
    'specimen': {
        'blueprint_id': 28, 'label':'科考标本',
        'default_topology':'matted_gallery', 'default_material':'none',
        'fonts': {'hero':'PingFang SC','emotion':'PingFang SC','data':'Courier New','point':'Helvetica'},
        'scale': {'hero_px':64,'lead_px':30,'micro_px':13,'hero_lh':1.0,'hero_letter':'0.06em','hero_shadow':'0 0 0 rgba(0,0,0,0)'},
        'palette': {'primary':'#12161a','accent':'#e9ecef','point':'#8ad1a8'},
        'layout': {'photo_top_ratio':0.0,'photo_height_ratio':0.82,
                   'arch_top_ratio':0.83,'arch_height_ratio':0.17,'grid_cols':4,
                   'title_frame':'SPECIMEN FIELD RECORD'},
        'z_layers': {'bg':1,'photo':10,'crosshair':15,'arch':20},
    },
}

# ---- 主体感知（复用 v1 的 detect_subject_zone，简化版）----
def detect_subject_zone(photo):
    try:
        from PIL import Image
        im=Image.open(photo).convert('L').resize((16,16)); px=list(im.getdata())
        def cell(x0,x1,y0,y1):
            v=[px[y*16+x] for y in range(y0,y1) for x in range(x0,x1)]
            m=sum(v)/len(v); e=sum(abs(a-b) for a,b in zip(v,v[1:]))/len(v); return m,e
        TL=cell(0,8,0,8);TR=cell(8,16,0,8);BL=cell(0,8,8,16);BR=cell(8,16,8,16)
        def w(c): m,e=c; return e*(1+abs(m-128)/128)
        wl=w(TL)+w(BL);wr=w(TR)+w(BR);wt=w(TL)+w(TR);wb=w(BL)+w(BR)
        h='center'
        if wr>wl*1.12:h='right'
        elif wl>wr*1.12:h='left'
        v='center'
        if wb>wt*1.12:v='bottom'
        elif wt>wb*1.12:v='top'
        return {'h':h,'v':v}
    except Exception:
        return {'h':'center','v':'center'}



def esc(s): return _html.escape(s, quote=True)

def _exif_lens(photo):
    """读取镜头参数（焦距/光圈/ISO），无 EXIF 返回 ''（沿用旧引擎缺省回退）。"""
    try:
        from PIL import Image as _I
        ex = _I.open(photo).getexif(); lp = []
        _fl = ex.get(37386); _fn = ex.get(33437); _iso = ex.get(34855)
        if _fl: lp.append(f'{int(_fl)}MM')
        if _fn: lp.append(f'F{float(_fn):.1f}')
        if _iso: lp.append(f'ISO {int(_iso)}')
        if lp: return ' · '.join(lp)
    except Exception:
        pass
    return ''

def _exif_location(photo):
    """读取 GPS 坐标，无 EXIF 返回 ''（沿用旧引擎缺省回退）。"""
    try:
        from PIL import Image as _I
        from PIL.ExifTags import TAGS as _T, GPSTAGS as _G
        exif = _I.open(photo).getexif(); gps = {}
        for tag, val in exif.items():
            t = _T.get(tag, tag)
            if t == 'GPSInfo':
                for k, v in val.items(): gps[_G.get(k, k)] = v
        def deg(v):
            d, m, s = v; return float(d) + float(m)/60 + float(s)/3600
        if 'GPSLatitude' in gps and 'GPSLongitude' in gps:
            lat = deg(gps['GPSLatitude']); lon = deg(gps['GPSLongitude'])
            latref = gps.get('GPSLatitudeRef') or 'N'
            lonref = gps.get('GPSLongitudeRef') or 'E'
            if latref == 'S': lat = -lat
            if lonref == 'W': lon = -lon
            return f"{abs(lat):.4f}°{latref} {abs(lon):.4f}°{lonref}"
    except Exception:
        pass
    return ''
# ---- 印章文字（P0-3/P0-4 章法：--seal > 自动取 > 默认）----
_RANGE_CJK = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF))   # 扩展A / 统一表意 / 兼容
def _is_cjk(ch):
    """是否为 CJK 汉字（印章只取汉字，滤掉空白/标点/英文/数字）。"""
    o = ord(ch)
    return any(a <= o <= b for a, b in _RANGE_CJK)

# 简体专用字（与繁体不同形）启发式：串中含任一 → 判为简体 → 不自动取印（P0-3 印用繁体）。
# 仅收录"简体形 ≠ 繁体形"的字（无→無/静→靜/风→風/叶→葉/烟→煙 等）；两体同形字（石/山/水）不入集合，
# 不影响纯繁体判定。设计承认此判断为"尽力而为"，超出引擎能力——契题繁体印文由 skill 层传 `--seal` 保证。
_SIMPLIFIED = set(
    "无与为东丝两严个丰临举么义乌乐乔习乡书买乱争于亏云亚产亩亲亿仅从仑仓仪们众优会伞伟传伤伦体余"
    "经线织约网罗华万兰关兴养兽内冈册写军农冯决况净凉减凑凛几凤凭凯击凿划刘则刚创删剧剑剥办动劳势勋劲励"
    "欧铸银钢铁锋错钱钥长门问间闻闷闲阳阴阵际陆陈险随隐马鸟鱼麦见贝车东乐龙宝国学书"
    "云风叶烟静栈"
)
def _is_simplified(cs):
    """含任一简体专用字 → True（判为简体串，不自动取印）。"""
    return any(c in _SIMPLIFIED for c in cs)

def _norm_seal(cs):
    """去空白/标点，仅保留 CJK 汉字；**只认 4 字** → 返回 cs[:4]，否则 None。
    归一化（P0-4，B13）：印文只允许 4 字田字格；**单字/2 字印不作**（用户拍板：2 字印字压边，取消）。
    其余（1/2/3/5 字等）回退默认。"""
    cs = [c for c in cs if _is_cjk(c)]
    return cs[:4] if len(cs) == 4 else None

def _resolve_seal(seal, title, sub, default):
    """印文三档回退：--seal > 自动从 title/sub 取（仅繁体 4 字）> 默认（现状）。
    返回 4 字田字格。B13 从严：显式 --seal 也只取 4 字（**无 2 字/单字印**），
    2 字 --seal（如"古巷"）/单字 --seal（如"貓"）不取，走自动/默认回退。P0-3：自动取仅当 title/sub 为繁体中文（不含简体专用字）；
    简体/英文/编号不自动取（回退默认，因引擎无法保证繁体，契题印文靠 skill 层传 --seal）。"""
    if seal:                                   # ① 用户显式 --seal（只取 4 字，不强制繁体——用户自担）
        cs = _norm_seal(list(str(seal)))
        if cs and len(cs) == 4:
            return cs
    for cand in (title, sub):                  # ② 自动从 title/sub 取（繁体 4 字才取）
        cs = _norm_seal(list(str(cand or '')))
        if cs and len(cs) == 4 and not _is_simplified(cs):
            return cs
    return default                             # ③ 回退默认（现状）

# 印章字号比例：只 4 字田字格 0.52（B13 取消 2 字印——删 2 字 0.60 项；只留 4 字）。
# B12：把 ratio 调大让字铺满印面；内距校验——字接近内框（留 <8% 内边）、不顶破边框。
# 只认 4 字（_norm_seal/_resolve_seal 已只认 4 字），其他字数回退 0.50（不应出现）。
_SEAL_RATIO = {4: 0.52}

def _seal_cells(chars, fam, size, ratio=None, ls=''):
    """印文 HTML 单元格：**只 4 字 → 2×2 田字格**（B13 取消 2 字竖排 / 单字印，只留 4 字）。
    字号比例按字数自动取（ratio=None 时用 _SEAL_RATIO，B12 铺满 + 内距校验 <8% 内边、不顶破框）；
    也可显式传 ratio 覆盖。只换文字来源/字号，不换印章版式（格/底/旋转/位置不变）。
    本函数不会收到非 4 字（_norm_seal/_resolve_seal 已只认 4 字）。"""
    if ratio is None:
        ratio = _SEAL_RATIO.get(len(chars), 0.50)

    def _c(pos, ch):
        st = (f"position:absolute;{pos};width:50%;height:50%;display:flex;align-items:center;justify-content:center;"
              f"font-family:\"{fam}\",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(size*ratio)}px;line-height:1")
        if ls:
            st += f';letter-spacing:{ls}'
        return f"<div style='{st}'>{ch}</div>"
    return _c('', chars[0]) + _c('left:50%', chars[1]) + _c('top:50%', chars[2]) + _c('left:50%;top:50%', chars[3])

def _bg_luma_for(photo):
    """落点背景亮度兜底：直接调 analyze_pixel.measure 顶/底分区亮度（dict {'top','bottom'}），
    失败返回 None（走 readability 双影兜底）。引擎 CLI 已在分发时传入更精确的 bg_luma。"""
    try:
        from analyze_pixel import measure
        b = measure(photo)['brightness']
        return {'top': float(b['top']), 'bottom': float(b['bottom'])}
    except Exception:
        return None


def render_html(photo, genre, topology_id, material_id, title, date, sub, location, lens='', seed=7, out_dir=None, font_safe=None, seal='', text_offset_x=0, text_offset_y=0, bg_luma=None, photo_focus_y=None):
    # 文字对比保障（引擎级）：用共享 readability 按"落点背景亮度"自动选亮/暗字 + 描边/阴影
    # bg_luma：dict {'top','bottom'}（analyze_pixel 亮度，0~255）；None=无像素数据 → 双影兜底
    def _CT(ink, bg_luma_=None):
        """已废弃，仅兼容保留（WP-B A1 收口）：委托 _rd_guard 取其 shadow 部分。
        新代码一律用 _rd_guard(ink, part)（返回 {color,shadow}，颜色随落点亮度翻转）；
        bg_luma_ 形参已废弃忽略（守卫按 part 自取落点亮度）；--font-safe off 语义不变（透明影）。"""
        return _rd_guard(ink, 'top')['shadow']
    def _bg(key):
        """取落点分区亮度（scalar 0~255）；无 bg_luma 或取不到返回 None。"""
        if isinstance(bg_luma, dict) and bg_luma.get(key) is not None:
            try:
                return float(bg_luma[key])
            except (TypeError, ValueError):
                return None
        return None
    def _rd_guard(ink, part='top'):
        """落点亮度可读守卫（返回 {color, shadow}）；--font-safe off 时禁用（保持原色+透明影）。
        part：'top'/'bottom' 落区分区亮度；也可直接传已知数值亮度 0~255（文字压已知实底时，如 specimen 拱形卡）。"""
        if isinstance(font_safe,str) and font_safe.lower() in ('off','false','0','none'):
            return {'color': ink, 'shadow': '0 0 0 rgba(0,0,0,0)'}
        bg = part if isinstance(part,(int,float)) and not isinstance(part,bool) else _bg(part)
        return readability(ink, bg)
    G = GENRE[genre]; TOPO = TOPOLOGY[topology_id]; MAT = MATERIAL[material_id]
    F = G['fonts']; SC = G['scale']; PA = G['palette']; L = G['layout']
    zone = detect_subject_zone(photo)
    # 画幅（竖版先默认 3:4；真实比例检测可从 photo 算，此处简化 3:4 测试）
    # 比例检测：从照片读宽高比，自动选画幅（3:4/4:3/16:9/9:16/1:1）
    try:
        from PIL import Image as _PI
        _pw,_ph = _PI.open(photo).size
        _r = _pw/_ph
        if _r>=1.6: _RATIO='16:9'
        elif _r>=1.25: _RATIO='4:3'
        elif _r>0.9: _RATIO='1:1'
        elif _r>0.6: _RATIO='3:4'
        else: _RATIO='9:16'
    except Exception:
        _RATIO='3:4'
    W,H = SIZES[_RATIO]
    if W>H: fx,fy = W/1350, H/1080
    else: fx,fy = W/1080, H/1350
    fs = min(fx,fy)
    # B14：文字落点随主体微调。偏移量按 fs（min(fx,fy)）缩放；只对"简单款"（绝对定位单行大字）
    # 的 title/sub 落点注入，复杂款（竖排/flex/多行）不动（防破坏布局，靠选对款）。
    _tox = int(text_offset_x * fs)   # 水平偏移（px）——只对"有真实 left 锚点"的款生效
    _toy = int(text_offset_y * fs)   # 垂直偏移（px）——主用：简单款 title/sub 的 top 上下移
    # 主标字号宽度预算（同旧引擎：字号×字数≥画布时收缩防超宽）
    title_units = len(title.replace(' ',''))
    max_w = int(W*0.90)
    if title_units>0:
        _per_unit = max_w/max(title_units,1)
        hero_fs = int(min(SC['hero_px']*fs, _per_unit*1.5))
    else:
        hero_fs = int(SC['hero_px']*fs)
    # 通用字段（新流派沿用旧 render_engine 写法）
    Z = G['z_layers']
    FEMO = F.get('emotion', F['hero'])          # 副标/正文字体（缺省回退 hero）
    FDATA = F.get('data', 'SpaceMono')          # 等宽数据字体
    T = esc(title); D = esc(date); S = esc(sub)
    LOC_E = esc(location) if location else (esc(_exif_location(photo)) or 'UNKNOWN')
    LENS_E = esc(lens) if lens else esc(_exif_lens(photo) or '28MM · F2.0 · ISO 200')
    # 缩放/复制照片
    outdir = out_dir or os.path.dirname(os.path.abspath(photo))
    os.makedirs(outdir, exist_ok=True)
    _ph = hashlib.md5(os.path.abspath(photo).encode()).hexdigest()[:8]
    IMG = f'v2_{_ph}.jpg'
    if os.path.abspath(photo) != os.path.join(outdir, IMG):
        import shutil as _s; _s.copy(photo, os.path.join(outdir, IMG))
    # WP-B · 照片取景焦点（核心款）：y≠50 时 img.ph 类规则追加 object-position（0=保顶裁脚）；
    # y=50/缺省 → 空串不输出（与历史字节一致；核心款 .ph 原本无 object-position，缺省即 center）。
    _fy = 50 if photo_focus_y is None else int(photo_focus_y)
    ph_focus = '' if _fy == 50 else ('object-position:center %d%%;' % _fy)
    HEAD = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
.stage{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
img.ph{{display:block;width:100%;height:100%;object-fit:cover{ph_focus}}}
</style></head><body><div class="stage"><img class="ph" src="{IMG}">"""
    body = ''
    # ===== zen（genre 主字避开主体，按 TOPO=right_wing 落右，但主体在右→改左）=====
    if genre=='zen':
        ink = PA['primary']; top_px = L['calligraphy_top_px']; margin_px = L['calligraphy_right_px']
        gap = L['col_gap_px']; lead_mt = L['lead_margin_top_px']; meta_mt = L['meta_margin_top_px']
        # 落点亮度感知（zen 深墨压照片 → 暗底自动翻亮字 + 发光；已知暗底/未知双影）
        _rd = _rd_guard(ink, 'top')
        _mast_side = 'left' if zone['h'] != 'left' else 'right'
        margin_px = int(margin_px * 0.90)   # 整组左移 10%
        _pos = f"{_mast_side}:{int(margin_px*fx)}px"
        body += f"""
<div style='position:absolute;top:{int(top_px*fy)}px;{_pos};z-index:20;display:flex;flex-direction:row-reverse;gap:{int(gap*fx)}px'>
  <div style='font-family:"{F['hero']}",{SERIF_CN};font-weight:900;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};writing-mode:vertical-rl;color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']}'>{title}</div>
  <div style='font-family:"{F['data']}",monospace;font-size:{int(SC['micro_px']*fs)}px;letter-spacing:.45em;writing-mode:vertical-rl;color:{ink};margin-top:{int(meta_mt*fy)}px;opacity:.55'>{date}·{location}</div>
</div>
<div style='position:absolute;top:{int(top_px*fy)}px;left:{int(6*fx)}px;z-index:20;writing-mode:vertical-rl'>
  <div style='font-family:"{F['emotion']}",{SERIF_CN};font-size:{int(SC['lead_px']*1.15*fs)}px;line-height:1;letter-spacing:.08em;color:{_rd['color']};opacity:.95;font-weight:700;text-shadow:{_rd['shadow']}'>{sub}</div>
</div>"""
        _sg = _resolve_seal(seal, title, sub, L['seal_chars']); _seal_size = int(46*fs)
        # 2026-09-25 用户修单：印章放**副标正下方**（副标=left:6 竖排，font lead×1.15 + .08em
        # 字距 + CJK 行高 → 每字纵向按 lead×1.15×1.25 估、+24 保险距〔1.08 版曾压尾字〕）。
        # 审查修复 F4：无副标分支竖排字高按 **字号×(1+hero_letter) 逐字**估——竖排 advance
        # 与行高无关（hero_lh 0.95 是列宽系数；按它估高低估 ~20%，≥2 字时印章压字尾）。
        _seal_pos = f"left:{int(6*fx)}px" if sub else f"{_mast_side}:{int(margin_px*fx+64*fx)}px"
        _seal_top = (int(top_px*fy + len(sub) * SC['lead_px'] * 1.15 * 1.25 * fs + 24 * fy) if sub
                     else int(top_px*fy + int(SC['hero_px']*fs*(1 + float(SC['hero_letter'].replace('em',''))))
                              * len(title.replace(' ','')) + 24*fy))
        _cell = _seal_cells(_sg, F['hero'], _seal_size)
        body += f"""
<div style='position:absolute;top:{_seal_top}px;{_seal_pos};z-index:20;width:{_seal_size}px;height:{_seal_size}px;background:{PA['point']};transform:rotate({L['seal_rotate']}deg);box-shadow:0 0 0 2px rgba(255,255,255,.5) inset,0 8px 22px rgba(0,0,0,.5)'><div style='position:absolute;inset:8%;border:1px solid rgba(255,255,255,.72)'>{_cell}</div></div>"""

    elif genre=='pulip':
        # 先锋街拍：主标按主体水平避让(主体右→靠左)，+ TOC + 条码
        shade_h = int(H*L['shade_height_ratio'])
        hdr_top = L['hdr_top_px']; title_top = int(H*L['title_top_ratio'])
        toc_bot = int(H*L['toc_bottom_ratio'])
        # B10 回归修复：sub 落点 = max(H*ratio, title_bottom+gap)。横版(4:3/16:9)标题大时防 sub 压 title；
        # 竖版保持 H*ratio 兜底，不松散。gap 用 18*fy 固定（横版 18-22px·fy 合适区间）。
        _pulip_title_fs = fit_title_fs(title, int(W-80*fx), int(SC['hero_px']*0.9*fs), '0.7em')
        _pulip_title_bottom = title_top + _pulip_title_fs * SC['hero_lh']
        sub_top = max(int(H*L['sub_gap_ratio']), int(_pulip_title_bottom + 18*fy))
        # 2026-09-14 用户微调：中英文标题整组垂直上移 10%（各按其当前 top 值的 10% 上提）
        title_top -= int(title_top * 0.10)
        sub_top -= int(sub_top * 0.10)
        if zone['h']=='right': _al='left'
        elif zone['h']=='left': _al='right'
        else: _al='center'
        _pulip_rd = _rd_guard(PA['primary'], 'top')
        body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{shade_h}px;z-index:2;background:linear-gradient(180deg, rgba(16,16,19,0.95), transparent)'></div>
<div style='position:absolute;top:{hdr_top}px;left:{int(52*fx)}px;right:{int(52*fx)}px;z-index:5;display:flex;justify-content:space-between'>
  <div style='font:12px "SpaceMono",monospace;color:{PA['accent']};letter-spacing:.4em;opacity:.9'>{L['issueno']}<br>{L['issue_meta']}</div>
  <div style='font:12px "SpaceMono",monospace;color:{PA['accent']};letter-spacing:.3em'>{L['badge']}</div>
</div>
<div style='position:absolute;top:{title_top+_toy}px;left:{int(40*fx)}px;right:{int(40*fx)}px;z-index:5;text-align:{_al}'>
  <div style='display:inline-block;font-family:SourceSerifHeavy,"{F['hero']}",{SERIF_CN};font-weight:700;font-size:{_pulip_title_fs}px;line-height:{SC['hero_lh']};letter-spacing:0.7em;color:{_pulip_rd['color']};text-shadow:{_pulip_rd['shadow']};white-space:nowrap'>{title}</div>
</div>
<div style='position:absolute;top:{sub_top+_toy}px;left:{int(56*fx)}px;right:{int(56*fx)}px;z-index:5;text-align:{_al}'>
  <div style='font-family:"{F['emotion']}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;color:{_pulip_rd['color']};letter-spacing:.5em;opacity:.95;text-shadow:{_pulip_rd['shadow']}'>{sub}</div>
</div>
<div style='position:absolute;bottom:{toc_bot}px;left:{int(48*fx)}px;z-index:5;font:11px "SpaceMono",monospace;color:{PA['accent']};line-height:1.9;letter-spacing:.3em;opacity:.85;background:rgba(16,16,19,.55);backdrop-filter:blur(6px);padding:14px 18px'>句摘 · VERSE<br>{'<br>'.join(f'{i:02d}  {t}' for i,t in enumerate(L['toc'],1))}</div>
"""
    elif genre=='bauhaus':
        # 包豪斯几何大刊：红色大刊头 + 几何边饰 + 网格构成（字S，红黑高饱和，拓06腰封）
        mast_top = L['masthead_top_px']; title_top = int(H*L['title_top_ratio'])
        sub_top = int(H*L['sub_top_ratio'])
        # 主体避让：主字放主体对侧（水平）
        if zone['h']=='right': _al='left'
        elif zone['h']=='left': _al='right'
        else: _al='center'
        red = PA['accent']; ink = PA['primary']
        # 2026-09-14 用户批：小字对比不足（质检 val=6~16）→ 字号提到 22px + 落点亮度守卫
        # （暗底自动翻亮字；亮底翻深。守卫语义同 imperial/monumental 的 WP-B A1 收口）
        _rd_red = _rd_guard(red, 'top')
        _rd_ink = _rd_guard(ink, 'top')
        # 顶部几何横梁（红）
        body += f"""
<div style='position:absolute;top:{int(mast_top*fy)}px;left:0;right:0;z-index:5;height:{L['rule_h']}px;background:{red}'></div>
<div style='position:absolute;top:{int((mast_top+14)*fy)}px;left:{int(44*fx)}px;right:{int(44*fx)}px;z-index:5;display:flex;justify-content:space-between'>
  <div style='font:{int(22*fs)}px "Oswald",sans-serif;letter-spacing:.32em;color:{_rd_red['color']};opacity:.95;text-shadow:{_rd_red['shadow']}'>{L['issue']}</div>
  <div style='font:{int(22*fs)}px "Oswald",sans-serif;letter-spacing:.28em;color:{_rd_ink['color']};opacity:.85;text-shadow:{_rd_ink['shadow']}'>ALPHA 04</div>
</div>
"""
        # 红色大刊头（主标）
        body += f"""
<div style='position:absolute;top:{title_top}px;left:{int(44*fx)}px;right:{int(44*fx)}px;z-index:5;text-align:{_al}'>
  <div style='display:inline-block;font-family:"{F['hero']}",sans-serif;font-weight:900;font-size:{fit_title_fs(title, int(W-88), int(SC['hero_px']*fs), SC['hero_letter'])}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};text-transform:uppercase;color:{_rd_red['color']};text-shadow:{SC['hero_shadow']},{_rd_red['shadow']};white-space:nowrap'>{title}</div>
</div>
"""
        # 副标（简体宋体）
        body += f"""
<div style='position:absolute;top:{sub_top}px;left:{int(44*fx)}px;right:{int(44*fx)}px;z-index:8;text-align:{_al}'>
  <div style='font-family:"{F['emotion']}",{SANS_CN};font-size:{int(SC['lead_px']*fs)}px;font-weight:700;color:{_rd_ink['color']};letter-spacing:.4em;opacity:.9;text-shadow:{_rd_ink['shadow']}'>{sub}</div>
</div>
"""
        # 几何边饰：左下红圆 + 网格竖线 + 底部注脚
        body += f"""
<div style='position:absolute;left:{int(44*fx)}px;bottom:{int(60*fy)}px;z-index:12;width:44px;height:44px;border-radius:50%;background:{red};opacity:.9'></div>
<div style='position:absolute;right:{int(60*fx)}px;bottom:{int(56*fy)}px;z-index:12;width:0;height:0;border-left:22px solid transparent;border-right:22px solid transparent;border-bottom:38px solid {ink};opacity:.85'></div>
<div style='position:absolute;left:0;right:0;bottom:{int(28*fy)}px;z-index:5;height:1px;background:rgba(213,43,30,.35)'></div>
<div style='position:absolute;left:{int(44*fx)}px;bottom:{int(10*fy)}px;z-index:12;font:{int(22*fs)}px "Oswald",sans-serif;letter-spacing:.3em;color:{_rd_ink['color']};opacity:.85;text-shadow:{_rd_ink['shadow']}'>{L['foot']}</div>
"""
    elif genre=='dual_portals':
        # 天地双极巨门：顶部巨字 + 底部巨字对峙（字T，拓04），中间照片被上下巨字夹成"门"
        top_top = int(H*L['top_max_top_ratio']); bot_top = int(H*L['bot_max_bottom_ratio'])
        ink = PA['primary']; accent = PA['accent']
        # 顶部巨字
        body += f"""
<div style='position:absolute;top:{top_top+_toy}px;left:0;right:0;z-index:{Z['top']};text-align:center'>
  <div style='font-family:"{F['hero']}",{SERIF_CN};font-weight:900;font-size:{fit_title_fs(title, int(W*0.92), int(L['top_title_fs']*fs), SC['hero_letter'])}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{accent};text-shadow:{SC['hero_shadow']};white-space:nowrap'>{title}</div>
</div>
"""
        # 顶部小字品牌
        body += f"""
<div style='position:absolute;top:{int((top_top+L['top_title_fs']*fs*1.18)*fy)+_toy}px;left:0;right:0;z-index:20;text-align:center'>
  <div style='font:{int(22*fs)}px "SpaceMono",monospace;letter-spacing:.4em;color:{accent};opacity:1;text-shadow:0 1px 8px rgba(0,0,0,.75)'>{L['brand']}</div>
</div>
"""
        # 底部巨字（副标）——复用公共 fit_title_fs 按宽度自适应（一行放下不换行）
        _bot_fs = fit_title_fs(sub, int(W*0.92), int(L['bot_title_fs']*fs), SC['hero_letter'])
        # clip_safe：底部巨字/注脚定位夹到画布安全边距（防触底被 overflow:hidden 裁）
        _bot_top = clip_safe(bot_top, H, 30)
        _foot_bot = clip_safe(int(H*L['foot_bottom_ratio']), H, 20)
        body += f"""
<div style='position:absolute;bottom:{_bot_top}px;left:0;right:0;z-index:{Z['bottom']};text-align:center'>
  <div style='font-family:"{F['emotion']}",{SERIF_CN};font-weight:900;font-size:{_bot_fs}px;line-height:1;letter-spacing:{SC['hero_letter']};white-space:nowrap;color:{accent};text-shadow:{SC['hero_shadow']}'>{sub}</div>
</div>
"""
        # 底部注脚
        body += f"""
<div style='position:absolute;left:0;right:0;bottom:{_foot_bot}px;z-index:30;text-align:center'>
  <div style='font:{int(10*fs)}px "SpaceMono",monospace;letter-spacing:.3em;color:{accent};opacity:.65'>{date} · {location}</div>
</div>
"""
    elif genre=='blue_note':
        # Blue Note 爵士黑胶封套：顶部几何横梁 + 主标 + 底部 33⅓ RPM 音轨目录（字M，拓01，纯色撞色）
        beam_top = L['beam_top_px']; beam_h = L['beam_h']; title_top = int(H*L['title_top_ratio'])
        track_bot = int(H*L['track_bottom_ratio'])
        blue = PA['primary']; orange = PA['accent']; cream = PA['point']
        # 落点亮度感知（WP-B A1 收口：主标/副标 'top'、音轨块 'bottom'，深蓝压暗底自动翻亮字）
        _rd_blue = _rd_guard(blue, 'top'); _rd_orange = _rd_guard(orange, 'top'); _rd_track = _rd_guard(blue, 'bottom')
        # 顶部几何横梁（Blue Note 标志）
        body += f"""
<div style='position:absolute;top:{beam_top}px;left:0;right:0;height:{beam_h}px;z-index:{Z['beam']};background:{orange}'></div>
<div style='position:absolute;top:{beam_top}px;left:{int(40*fx)}px;right:{int(40*fx)}px;height:{beam_h}px;z-index:11;display:flex;align-items:center;justify-content:space-between'>
  <div style='font:{int(12*fs)}px "SpaceMono",monospace;letter-spacing:.22em;color:{cream};font-weight:700'>BLUE NOTE</div>
  <div style='font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.2em;color:{cream};opacity:.92'>{L['cat']}</div>
</div>
"""
        # 主标（Unbounded，横梁下）
        body += f"""
<div style='position:absolute;top:{title_top+_toy}px;left:{int(40*fx)+_tox}px;right:{int(40*fx)}px;z-index:{Z['title']};text-align:left'>
  <div style='font-family:"{F['hero']}",sans-serif;font-weight:900;font-size:{fit_title_fs(title, int(W-80*fx), int(SC['hero_px']*fs), SC['hero_letter'])}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd_blue['color']};text-shadow:{SC['hero_shadow']},{_rd_blue['shadow']};white-space:nowrap'>{title}</div>
</div>
"""
        # 副标（中英，暖橙）
        body += f"""
<div style='position:absolute;top:{int((title_top+int(SC['hero_px']*fs)+18)*fy)+_toy}px;left:{int(40*fx)+_tox}px;z-index:20;text-align:left'>
  <div style='font-family:"{F['emotion']}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;color:{_rd_orange['color']};letter-spacing:.22em;opacity:.95;text-shadow:{_rd_orange['shadow']}'>{sub}</div>
</div>
"""
        # 底部 33⅓ RPM 音轨目录
        body += f"""
<div style='position:absolute;left:{int(40*fx)}px;right:{int(40*fx)}px;bottom:{track_bot}px;z-index:{Z['track']};display:flex;justify-content:space-between;align-items:flex-end'>
  <div style='font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.24em;color:{_rd_track['color']};opacity:.85;line-height:1.9;text-shadow:{_rd_track['shadow']}'>
    <div>{L['rpm']}</div>
    <div>{date} · {location}</div>
  </div>
  <div style='width:{int(120*fx)}px;height:{int(24*fy)}px;background:repeating-linear-gradient(90deg,{blue} 0 3px,transparent 3px 7px)'></div>
</div>
"""
    elif genre=='slender_zen':
        # 日系清秀手札：纤细明朝刊头(拓03右翼竖轴) + 霞鹜文楷副标 + Cormorant斜体诗，防毛玻璃清透
        mast_top = L['mast_top_px']; title_right = L['title_right_px']
        lead_mt = L['lead_margin_top_px']; poem_mt = L['poem_margin_top_px']
        ink = PA['primary']; grey = PA['point']
        # 落点亮度感知（清秀深墨压照片 → 暗底自动翻亮字 + 发光；已知暗底/未知双影）
        _rd = _rd_guard(ink, 'top')
        # 独立 left 定位（竖排下 margin 不可靠，用明确 x 坐标排开各列防重叠）
        # 竖排右翼：文字固定放左侧(避开右侧常见主体)，不依赖易误判的 zone['h'](亮背景会被误判成左侧)。
        _anchor = int(title_right * fx)
        _dir = 1
        # 纤细明朝主刊头（竖排）
        body += f"""
<div style='position:absolute;top:{int(mast_top*fy)}px;left:{_anchor}px;z-index:20;writing-mode:vertical-rl;font-family:"{F['hero']}",{SERIF_CN};font-weight:300;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']}'>{title}</div>
"""
        # 霞鹜文楷副标（竖排，清秀）
        body += f"""
<div style='position:absolute;top:{int((mast_top+30)*fy)}px;left:{_anchor+_dir*int(140*fx)}px;z-index:20;writing-mode:vertical-rl;font-family:"{F['emotion']}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;letter-spacing:.25em;color:{_rd['color']};opacity:.9;text-shadow:{_rd['shadow']}'>{sub}</div>
"""
        # Cormorant 斜体诗（点缀，英文/罗马）
        # 2026-09-14 用户批：原字体栈 "{F['data']}",serif —— Cormorant 无假名/汉字字形，
        # 全靠系统 serif 回退（本机成形，跨机可能变 □）。补 CJK 面（SERIF_CN 链，同款其他文字一致）。
        body += f"""
<div style='position:absolute;top:{int((mast_top+30)*fy + len(title)*int(SC['hero_px']*fs*1.32))}px;left:{_anchor}px;z-index:22;writing-mode:vertical-rl;font-family:"{F['data']}",{SERIF_CN};font-style:italic;font-size:{int(SC['micro_px']*1.6*fs)}px;color:{_rd['color']};text-shadow:{_rd['shadow']};letter-spacing:.18em'>{L['song_lines'][0]}<br>{L['song_lines'][1]}<br>{L['song_lines'][2]}</div>
"""

        # 2026-09-05 用户微调：四周细线内衬框（清秀手札装帧感）
        body += f"""
<div style='position:absolute;inset:{int(26*fs)}px;border:1px solid {_rd['color']};opacity:.32;z-index:18;pointer-events:none'></div>
"""

    elif genre=='monumental':
        # 君临天幕帝国：240-280px 纯金巨字充斥天穹（顶置全幅居中，半透明金字+深阴影"气场环抱"不遮主体）
        mast_top = L['masthead_top_px']
        foot_bot = L['footnote_bottom_px']
        # 落点亮度感知（WP-B A1 收口：金主标/白副标压天穹顶部 → 暗底保色发光、亮底翻深）
        _rd = _rd_guard(SC['hero_color'], 'top'); _rd_sub = _rd_guard('#ffffff', 'top')
        # B10 回归修复：sub 落点 = max(H*ratio, title_bottom+gap)。横版标题大时防 sub 压 title；
        # 竖版保持 H*ratio 兜底，不松散。gap 用 20*fy 固定。
        _mon_title_fs = fit_title_fs(title, int(W*0.92), hero_fs, SC['hero_letter'])
        _mon_title_bottom = int(mast_top*fy) + _mon_title_fs * SC['hero_lh']
        sub_top = max(int(H * L['subtitle_top_ratio']), int(_mon_title_bottom + 20*fy))
        body += f"""
<div style='position:absolute;top:{int(mast_top*fy)+_toy}px;left:0;right:0;z-index:{Z['masthead']};text-align:center'>
  <div style='display:inline-block;font-family:"{F['hero']}";font-weight:900;font-size:{_mon_title_fs}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']};text-transform:uppercase;white-space:nowrap'>{T}</div>
</div>
"""
        body += f"""
<div style='position:absolute;top:{sub_top+_toy}px;left:0;right:0;z-index:{Z['subtitle']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:{_rd_sub['color']};letter-spacing:.25em;text-shadow:0 6px 24px rgba(0,0,0,.95),{_rd_sub['shadow']}'>{S}</div>
</div>
"""
        body += f"""
<div style='position:absolute;left:0;right:0;bottom:{int(foot_bot*fy)}px;z-index:{Z['footnote']};text-align:center'>
  <div style='font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;color:#e6d29b;letter-spacing:.32em'>{D}{' · ' if date else ''}{LOC_E} · {LENS_E}</div>
</div>
"""
    elif genre=='nocturne':
        # 时尚夜曲封面：顶部墨韵渐变(防吞没) + 大刊头 + 中文副标 + 底部图说卡/ISSN
        shade_top = int(L['masthead_top_px'])
        shade_h = int(H * L['shade_height_ratio'])
        subtitle_top = int(H * (L['subtitle_top_ratio'] + 0.10))  # 下移，防与主标重叠
        # 落点亮度感知（WP-B A1 收口：主标/白副标压夜曲照片顶部 → 暗底自动翻亮字）
        _rd = _rd_guard(PA['accent'], 'top'); _rd_sub = _rd_guard('#ffffff', 'top')
        caption_bottom = int(H * L['caption_bottom_ratio'])
        body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{shade_h}px;z-index:{Z['shade']};background:{L['shade_grad']}'></div>
"""
        body += f"""
<div style='position:absolute;top:{shade_top+_toy}px;left:50px;right:50px;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{fit_title_fs(title, int(W-100), hero_fs, SC['hero_letter'])}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']};white-space:nowrap'>{T}</div>
</div>
"""
        body += f"""
<div style='position:absolute;top:{subtitle_top+_toy}px;left:50px;right:50px;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;color:{_rd_sub['color']};letter-spacing:.3em;text-shadow:{SC['hero_shadow']},{_rd_sub['shadow']}'>{S}</div>
</div>
"""
        cap = f'{D}' if date else ''
        if LOC_E: cap = cap + (' · ' if cap else '') + LOC_E
        if LENS_E: cap = cap + (' · ' if cap else '') + LENS_E
        barcode = L['issn']
        body += f"""
<div style='position:absolute;left:56px;right:56px;bottom:{caption_bottom}px;z-index:{Z['caption']};display:flex;justify-content:space-between;align-items:flex-end'>
  <div style='background:rgba(6,5,4,.55);backdrop-filter:blur(8px);padding:12px 16px;color:#e9dfd0;font:11px "SpaceMono",monospace;letter-spacing:.3em'>{cap}</div>
  <div style='background:rgba(6,5,4,.55);backdrop-filter:blur(8px);padding:10px 14px;color:#d49b6a;font:10px "SpaceMono",monospace;letter-spacing:.22em;text-align:right'>{barcode}<br><span style='opacity:.6'>POCKET EDITORIAL</span></div>
</div>
"""
    elif genre=='imperial':
        # 汉唐金石重器典藏：鎏金主标 + 特粗宋体中文副标 + 底部史实注脚 + 规范朱印(2×2白文田字格)
        gold = L['gold_hex']
        mast_top = L['masthead_top_px']
        sub_top = int(H * L['subtitle_top_ratio'])
        foot_bot = L['footnote_bottom_px']
        # 落点亮度感知（WP-B A1 收口：鎏金主标/白副标压照片顶部 → 暗底保色、亮底翻深）
        _rd = _rd_guard(SC['hero_color'], 'top'); _rd_sub = _rd_guard('#ffffff', 'top')
        body += f"""
<div style='position:absolute;top:{int(mast_top*fy)+_toy}px;left:0;right:0;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{F['hero']}";font-size:{fit_title_fs(title, int(W*0.92), hero_fs, SC['hero_letter'])}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']};text-transform:uppercase;white-space:nowrap'>{T}</div>
</div>
"""
        body += f"""
<div style='position:absolute;top:{int(sub_top*fy)+_toy}px;left:0;right:0;z-index:{Z['subtitle']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:{_rd_sub['color']};letter-spacing:.2em;text-shadow:0 4px 20px rgba(0,0,0,.9),{_rd_sub['shadow']}'>{S}</div>
</div>
"""
        body += f"""
<div style='position:absolute;left:0;right:0;bottom:{int(foot_bot*fy)}px;z-index:{Z['footnote']};text-align:center'>
  <div style='font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;color:{L.get('note_color','#ffd288')};letter-spacing:.3em'>{D}{' · ' if date else ''}{LOC_E} · {LENS_E}</div>
</div>
"""
        # 规范朱印：2×2 白文田字格，铺满、繁体、悬空落于左下空白负空间（不压主体）
        seal_red = L.get('seal_red', '#c43d2f')
        _seal = _resolve_seal(seal, title, sub, L.get('seal_grid', ['御','园','清','赏']))
        seal_size = int(min(hero_fs * 0.55, 130))
        _cell = _seal_cells(_seal, FEMO, seal_size, ls='.02em')
        body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(60*fy)}px;width:{seal_size}px;height:{seal_size}px;z-index:25;background:{seal_red};transform:rotate(-3deg);box-shadow:0 0 0 2px rgba(255,255,255,.55) inset, 0 6px 18px rgba(0,0,0,.45)'>
  <div style='position:absolute;inset:8%;border:1px solid rgba(255,255,255,.75)'></div>
  {_cell}
</div>
"""
    elif genre=='stone':
        # 宣纸金石碑拓：云雷纹回形金边 + 竖排书法主标(繁体全字库) + 霞鹜文楷款 + 朱砂朱文田字格印
        ink = L.get('ink_color', PA['primary'])
        # 落点亮度感知（stone 深墨压深夜空 → 暗底自动翻亮字 + 发光；已知暗底/未知双影）
        _rd = _rd_guard(ink, 'top')
        top_px = L['title_top_px']
        left_px = L['title_left_px']
        gap = L['col_gap_px']
        lead_mt = L['lead_margin_top_px']
        body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{int(H*0.22)}px;z-index:{Z['wash']};background:linear-gradient(180deg, rgba(23,19,13,0.16) 0%, transparent 100%)'></div>
<div style='position:absolute;left:0;right:0;bottom:0;height:{int(H*0.14)}px;z-index:{Z['wash']};background:linear-gradient(0deg, rgba(23,19,13,0.22) 0%, transparent 100%)'></div>
"""
        body += f"""
<div style='position:absolute;inset:{int(24*fx)}px;z-index:{Z['frame']};border:{int(1.5*fx)}px solid rgba(212,175,55,.55);pointer-events:none'>
  <div style='position:absolute;inset:8px;border:{int(6*fx)}px solid rgba(212,175,55,.18);margin:3px;background-image:{L['frame_border']};background-size:14px 14px;height:100%;opacity:.5'></div>
</div>
"""
        body += f"""
<div style='position:absolute;top:{int(top_px*fy)}px;left:{int(left_px*fx)}px;z-index:{Z['calligraphy']};display:flex;flex-direction:row;gap:{int(gap*fx)}px'>
  <div style='font-family:"{F['hero']}",{SERIF_CN};font-weight:900;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};writing-mode:vertical-rl;color:{_rd['color']};text-shadow:{SC['hero_shadow']},{_rd['shadow']}'>{T}</div>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;letter-spacing:.4em;writing-mode:vertical-rl;color:{_rd['color']};margin-top:{int(lead_mt*fy)}px;opacity:.9;text-shadow:{_rd['shadow']}'>{S}</div>
</div>
"""
        seal_red = L.get('seal_red', '#b83c23')
        _sg = _resolve_seal(seal, title, sub, L.get('seal_grid', ['石','上','花','开']))
        seal_size = int(min(SC['hero_px'] * L['seal_size_ratio'], 120))
        _cell = _seal_cells(_sg, FEMO, seal_size)
        body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(72*fy)}px;width:{seal_size}px;height:{seal_size}px;z-index:{Z['seal']};background:{seal_red};transform:rotate({L['seal_rotate']}deg);box-shadow:0 0 0 2px rgba(255,255,255,.5) inset, 0 8px 22px rgba(0,0,0,.5)'>
  <div style='position:absolute;inset:9%;border:1px solid rgba(255,255,255,.72)'></div>
  {_cell}
</div>
"""
    elif genre=='film':
        # 胶片齿孔档案卷：上下横带齿孔(竖图安全) + 暖褐调颗粒 + AGFA工业印字 + 片名系统宋体
        edge_w = L['edge_w']; hole_w = L['hole_w']; hole_h = L['hole_h']
        hole_r = L['hole_r']; gap = L['hole_gap']
        sepia = L.get('sepia', 0.55)
        # 落点亮度感知（WP-B A1 收口：主标压照片顶部 → 暗底自动翻亮字）
        _rd = _rd_guard(PA['accent'], 'top')
        body += f"""
<style>
.stage .ph{{filter:sepia({sepia}) saturate(1.05) contrast(1.05) brightness(0.98)}}
.grain{{position:absolute;inset:0;z-index:{Z['grain']};background:url('{GRAIN_URI}');opacity:.20;mix-blend-mode:overlay;pointer-events:none}}
.edge{{position:absolute;left:0;right:0;height:{edge_w}px;z-index:{Z['film']};background:linear-gradient(90deg,#2c1d10,#170d06)}}
.edge.t{{top:0;border-bottom:2px solid #000}}
.edge.b{{bottom:0;border-top:2px solid #000}}
.hole{{position:absolute;width:{hole_h}px;height:{hole_w}px;border-radius:{hole_r}px;background:#f4ead6;z-index:6;box-shadow:inset 2px 0 3px rgba(0,0,0,.45)}}
</style>
<div class='edge t'></div>
<div class='edge b'></div>
"""
        for i in range(int(W / gap) + 1):
            x = int(i * gap) + 20
            if x + hole_h <= W:
                body += f"<div class='hole' style='left:{x}px;top:{(edge_w-hole_w)//2}px'></div>"
                body += f"<div class='hole' style='left:{x}px;bottom:{(edge_w-hole_w)//2}px'></div>"
        body += f"""
<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' style='position:absolute;inset:0;z-index:{Z['film']+2};pointer-events:none'>
  <g stroke='rgba(255,255,255,.14)' stroke-width='1' fill='none'>
    <path d='M120 180 q 60 40 90 130' />
    <path d='M820 900 q 50 -30 80 40' />
  </g>
  <g fill='rgba(255,255,255,.10)'>
    <circle cx='300' cy='640' r='3'/><circle cx='720' cy='330' r='2'/><circle cx='540' cy='1010' r='4'/>
  </g>
</svg>
"""
        body += f"""
<div style='position:absolute;left:{int(8*fx)}px;top:{int(90*fy)}px;z-index:{Z['title']};writing-mode:vertical-rl;font:{int(13*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.45em;opacity:.85'>{L['brand']}</div>
<div style='position:absolute;right:{int(8*fx)}px;top:{int(90*fy)}px;z-index:{Z['title']};writing-mode:vertical-rl;font:{int(13*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.45em;opacity:.85'>{L['film_type']}</div>
<div style='position:absolute;right:{int(6*fx)}px;top:{int(24*fy)}px;z-index:{Z['title']};font:{int(12*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.2em'>{L['frame_no']}</div>
<div style='position:absolute;left:{int(70*fx)}px;bottom:{int(78*fy)}px;z-index:{Z['title']};font:{int(11*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.32em;opacity:.8'>{D} · {LOC_E} · {LENS_E}</div>
"""
        body += f"""
<div style='position:absolute;left:{int(L['title_left_px']*fx)}px;right:{int(L['title_left_px']*fx)}px;top:{int(L['title_top_px']*fy)}px;z-index:{Z['title']};text-align:left'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:700;font-size:{fit_title_fs(T, int(W - 2*L['title_left_px']), int(SC['hero_px']*fs), '0.12em')}px;line-height:{SC['hero_lh']};color:{_rd['color']};letter-spacing:.12em;text-shadow:{SC['hero_shadow']},{_rd['shadow']};white-space:nowrap'>{T}</div>
  <div style='margin-top:{int(20*fy)}px;font-family:"{FDATA}",monospace;font-size:{int(SC['lead_px']*fs)}px;color:{PA['point']};letter-spacing:.3em'>{S}</div>
</div>
"""
        body += f"<div class='grain'></div>"
    elif genre=='layered':
        # 压底穿插：Cinzel 巨字压入左侧(主体佛像在右负空间=影子区) + 几何标贴替代红印章 + 档案文案
        giant = L['giant_word']
        giant_top = int(H * L['giant_top_ratio'])
        giant_left = int(L['giant_left_px'] * fx)
        giant_angle = L['giant_angle']
        # 落点亮度感知（WP-B A1 收口：半透明巨字/副标 → 暗底保色发光、亮底翻深）
        _rd_giant = _rd_guard('rgba(242,239,232,0.66)', 'top'); _rd_sub = _rd_guard('#f2efe8', 'top')
        # 2026-09-14 微调批2 #12：巨字层加 opacity:0.2（"透明隐约"）。**必须落外层定位 div**——
        # 质检器对比度维度读"承载文字元素自身"的 computed opacity，落内层（含 BUDDHA 文本）会
        # 新出 contrast ✗（本款白名单不含 contrast）；CSS opacity 非继承属性 → 内层文本不受影响。
        body += f"""
<div style='position:absolute;top:{giant_top}px;left:{giant_left}px;z-index:{Z['giant']};transform:rotate({giant_angle}deg);opacity:0.2'>
  <div style='font-family:"{F['hero']}";font-weight:900;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{_rd_giant['color']};text-shadow:{SC['hero_shadow']},{_rd_giant['shadow']};white-space:nowrap'>{giant}</div>
</div>
"""
        body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(L['caption_bottom_px']*fy)}px;z-index:{Z['caption']};width:{int(220*fx)}px;height:{int(46*fy)}px;background:repeating-linear-gradient(90deg,#f2efe8 0 2px,transparent 2px 5px,#f2efe8 5px 8px,transparent 8px 10px,#f2efe8 10px 12px,transparent 12px 16px);box-shadow:0 0 0 8px rgba(13,13,15,.5)'></div>
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(118*fy)}px;z-index:{Z['caption']};background:#f2efe8;color:#0d0d0f;padding:8px 12px;font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.3em'>{L['badge_text']}</div>
"""
        cap2 = f'{D}' if date else ''
        if LOC_E: cap2 = cap2 + (' · ' if cap2 else '') + LOC_E
        if LENS_E: cap2 = cap2 + (' · ' if cap2 else '') + LENS_E
        body += f"""
<div style='position:absolute;right:{int(64*fx)}px;bottom:{int(L['caption_bottom_px']*fy)}px;z-index:{Z['caption']};text-align:right'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:{_rd_sub['color']};letter-spacing:.2em;text-shadow:0 2px 10px rgba(0,0,0,.8),{_rd_sub['shadow']}'>{S}</div>
  <div style='margin-top:8px;font:{int(10*fs)}px "SpaceMono",monospace;color:#cfc8bb;letter-spacing:.3em'>{cap2}</div>
</div>
"""
    elif genre=='specimen':
        # 科考标本参数卡：照片窗(上) + 十字瞄准线 + 四角L形 + 下部四栏档案卡 + 条形码
        photo_h = int(H * L['photo_height_ratio'])
        arch_top = int(H * L['arch_top_ratio'])
        arch_h = int(H * L['arch_height_ratio'])
        # 2026-09-05 微调通道修正：原为演示硬编码（石佛造像/南朝/南京博物院）与实际照片不符
        # → 从真实输入派生；无数据的字段显示 '—'
        _spec_no = 'SP-' + (date or '').replace('.', '')[2:8] if date else 'SP-______'
        cells = [
            ('主体', title or '—'), ('日期', date or '—'), ('采集地', LOC_E or '—'),
            ('编号', _spec_no), ('影像', LENS_E or '—'), ('记录', (sub or '—')[:14]),
            ('光影', '自然光'), ('状态', '已归档'),
        ]
        cell_html = ''.join(
            f"""<div style='padding:7px 12px;border-right:1px solid rgba(233,236,239,.14);border-bottom:1px solid rgba(233,236,239,.10)'>
              <div style='font:{int(9*fs)}px Helvetica,"Helvetica Neue",Arial,sans-serif;letter-spacing:.25em;color:{PA['point']};opacity:.85'>{k}</div>
              <div style='margin-top:3px;font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;color:{PA['accent']};letter-spacing:.05em'>{v}</div>
            </div>""" for k, v in cells)
        body += f"""
<style>
.stage .ph{{position:absolute;top:0;left:0;width:100%;height:{photo_h}px;object-fit:cover}}
.stage{{background:#000}}
.cross-x{{position:absolute;top:{int(photo_h*0.5)}px;left:{int(W*0.5)}px;width:1px;height:{int(photo_h*0.24)}px;background:rgba(233,236,239,.5);transform:translate(-50%,-50%);z-index:{Z['crosshair']}}}
.cross-y{{position:absolute;top:{int(photo_h*0.5)}px;left:{int(W*0.5)}px;height:1px;width:{int(W*0.24)}px;background:rgba(233,236,239,.5);transform:translate(-50%,-50%);z-index:{Z['crosshair']}}}
.corner{{position:absolute;width:26px;height:26px;border:2px solid rgba(233,236,239,.6);z-index:{Z['crosshair']}}}
.c-tl{{top:16px;left:16px;border-right:none;border-bottom:none}}
.c-tr{{top:16px;right:16px;border-left:none;border-bottom:none}}
.c-bl{{bottom:{int(H*0.28)}px;left:16px;border-right:none;border-top:none}}
.c-br{{bottom:{int(H*0.28)}px;right:16px;border-left:none;border-top:none}}
</style>
"""
        body += f"<div class='cross-x'></div><div class='cross-y'></div>"
        body += f"<div class='corner c-tl'></div><div class='corner c-tr'></div><div class='corner c-bl'></div><div class='corner c-br'></div>"
        # 落点亮度感知（WP-B A1 收口：主标压拱形卡实底 #0c1013 → 落点亮度已知）
        _rd_spec = _rd_guard(PA['accent'], luma('#0c1013'))
        body += f"""
<div style='position:absolute;top:{int(20*fy)}px;left:{int(28*fx)}px;z-index:{Z['crosshair']}'>
  <div style='font:{int(11*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.35em;opacity:.9'>{L['title_frame']}</div>
  <div style='margin-top:4px;font:{int(10*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.2em'>REC · NO.008</div>
</div>
"""
        body += f"""
<div style='position:absolute;left:0;right:0;top:{arch_top+_toy}px;height:{arch_h}px;z-index:{Z['arch']};background:#0c1013;border-top:1px solid rgba(233,236,239,.12)'>
  <div style='padding:8px 24px 0 24px;display:flex;justify-content:space-between;align-items:baseline'>
    <div style='font-family:"{F['hero']}",{SANS_CN};font-weight:900;font-size:{fit_title_fs(T, int(W-240), int(SC['hero_px']*fs), SC['hero_letter'])}px;color:{_rd_spec['color']};letter-spacing:{SC['hero_letter']};text-transform:uppercase;text-shadow:{SC['hero_shadow']},{_rd_spec['shadow']};white-space:nowrap'>{T}</div>
    <div style='font:{int(11*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.3em'>{D} · {LOC_E}</div>
  </div>
  <div style='margin:6px 24px 0 24px;display:grid;grid-template-columns:repeat({L['grid_cols']},1fr);border:1px solid rgba(233,236,239,.12)'>{cell_html}</div>
</div>
"""
        body += f"""
<div style='position:absolute;right:24px;bottom:{int(28*fy)}px;z-index:{Z['arch']};width:{int(190*fx)}px;height:{int(44*fy)}px;background:repeating-linear-gradient(90deg,#e9ecef 0 2px,transparent 2px 5px,#e9ecef 5px 8px,transparent 8px 10px,#e9ecef 10px 12px,transparent 12px 15px)'></div>
"""
    return HEAD + body + '</div></body></html>'


# --fg-texts 支持判定（2026-10-02 扩面：原固定 2 款白名单 → 能力判定）：凡 design 族 config 声明了
# layout.fixed（固定装饰文案位）的款都可注入；键名 = 该款 layout.fixed 键名（SKILL 键名表同源）。
# argparse help / 消费判空 / 忽略警告三处共用，防文案漂移；新款加 layout.fixed 即自动获得该能力。
def _fg_texts_supported(genre):
    return bool(((DESIGN_CONFIGS.get(genre) or {}).get('layout') or {}).get('fixed'))


def _embed_fonts(html):
    """方案 A（2026-09-25 用户拍板）· 字体数据内嵌：把 @font-face 的
    url("file:///…") 替换为**按本页用字子集化**的 woff2 base64 data URI
    （fontTools subset + brotli）——渲染机有字体即可子集；分发出的 html 在
    无字体机器的浏览器里打开不回退系统字。
    字符集 = 页面全文 ∪ 可打印 ASCII（超集：覆盖全部文案/装饰词/回退链）。
    照片仍为 file:// 引用（_photo_uri=as_uri，未拍板不动）。
    单款失败（文件缺失/子集异常）→ 保留原 file:// 引用 + 打印告警，不阻断渲染。
    默认关闭（零回归）；同参子集字节确定。"""
    import base64
    import io
    import re
    from fontTools import subset as _fsub

    pattern = re.compile(r'src:\s*url\("file:///([^"]+)"\)')
    paths = list(dict.fromkeys(pattern.findall(html)))
    if not paths:
        return html
    chars = ''.join(sorted(set(html) | {chr(c) for c in range(0x20, 0x7f)}))
    repl_map = {}
    for raw in paths:
        try:
            opts = _fsub.Options()
            font = _fsub.load_font(raw, opts)
            sub = _fsub.Subsetter(options=opts)
            sub.populate(text=chars)
            sub.subset(font)
            font.flavor = 'woff2'
            buf = io.BytesIO()
            font.save(buf)
            repl_map[raw] = 'data:font/woff2;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')
        except Exception as ex:  # 缺文件/坏字体 → 原引用保留 + 告警
            print(f'[embed-fonts] 子集失败，保留原引用: {raw} ({ex})')
            repl_map[raw] = None

    def _rep(m):
        rep = repl_map.get(m.group(1))
        return f'src: url("{rep}")' if rep else m.group(0)

    out = pattern.sub(_rep, html)
    print(f'[embed-fonts] {sum(1 for v in repl_map.values() if v)}/{len(paths)} 款字体已子集内嵌 (woff2)')
    return out


def _embed_photo(html):
    """方案 A 补充（2026-09-25 用户：边界能解决最好）· 照片内嵌：
    img 的 src="file:///…" → base64 data URI（mimetypes 按扩展名定 mime；
    as_uri() 的 percent 编码先 unquote 还原本地路径）——分发出的 html 照片
    不再依赖本机路径（与 --embed-fonts 合用 = html 自包含字体+照片）。
    失败（缺文件/无 mime）保留原引用 + 告警不阻断。默认关（零回归）。
    体积 +原图 ×1.37（如 1MB 照片 → html +1.37MB）。"""
    import base64
    import mimetypes
    import re
    import urllib.parse

    pat = re.compile(r'src="file:///([^"]+)"')
    raws = list(dict.fromkeys(pat.findall(html)))
    if not raws:
        return html
    stat = {'ok': 0, 'fail': 0}

    def _rep(m):
        real = urllib.parse.unquote(m.group(1))
        mt = mimetypes.guess_type(real)[0]
        if mt and os.path.exists(real):
            with open(real, 'rb') as fh:
                b64 = base64.b64encode(fh.read()).decode('ascii')
            stat['ok'] += 1
            return f'src="data:{mt};base64,{b64}"'
        stat['fail'] += 1
        print(f'[embed-photo] 内嵌失败，保留原引用: {real}')
        return m.group(0)

    out = pat.sub(_rep, html)
    print(f"[embed-photo] {stat['ok']}/{len(raws)} 张照片已内嵌 (data URI)")
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='版式引擎 v2 · 13 套精品流派（三层登记表）')
    p.add_argument('--photo', required=True, help='照片路径')
    p.add_argument('--genre', required=True, choices=list(GENRE.keys()) + MATTING_IDS + list(MATTING_ALIAS) + METAPHOR_IDS + BLUEPRINT_IDS + DESIGN_IDS, help='流派')
    p.add_argument('--title', default=''); p.add_argument('--date', default='')
    p.add_argument('--sub', default=''); p.add_argument('--location', default='')
    p.add_argument('--lens', default='')
    p.add_argument('--words', default='',
                   help='词墙用户词（仅 collage_man 消费；逗号分隔注入词墙③层，其余流派忽略）')
    p.add_argument('--fg-texts', default='',
                   help=f"固定装饰文案覆盖（key=词;key2=词2 分号分隔，键 = 该款 config layout.fixed 键名；"
                        f"凡声明了 layout.fixed 的款均可注入，其余流派忽略；未知键名告警丢弃）")
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--photo-ratio', type=float, default=None,
                   help='照片/谱线占比因子（仅 music_manuscript 载体隐喻款；默认 1.0；其它流派忽略）')
    p.add_argument('--topology', default=None, choices=list(TOPOLOGY.keys()))
    p.add_argument('--material', default=None, choices=list(MATERIAL.keys()))
    p.add_argument('--font-safe', default=None)
    p.add_argument('--seal', default='', help='印章文字（只支持 4 字名章田字格；带印流派可用，无印流派忽略）')
    p.add_argument('--text-offset-x', type=float, default=0,
                   help='文字水平偏移 px（按 fs 缩放；只对"有真实 left 锚点"的简单款生效，全宽居中款无效）')
    def _focus_y(s):
        v = int(s)
        if not (0 <= v <= 100): raise argparse.ArgumentTypeError('photo-focus-y 须 0-100，得 %d' % v)
        return v
    p.add_argument('--photo-focus-y', type=_focus_y, default=50,
                   help='照片取景纵向焦点 0-100（0=保顶裁脚；50=center 缺省不变；装裱/载体/蓝图/核心款 cover 路径通用）')
    p.add_argument('--text-offset-y', type=float, default=0,
                   help='文字垂直偏移 px（按 fs 缩放；只对简单款 title/sub 生效，复杂款竖排/flex/多行不生效）')
    p.add_argument('--embed-fonts', action='store_true',
                   help='方案A 字体内嵌：@font-face 按本页用字子集化为 woff2 base64'
                        '（分发 html 给无字体机器预览用；默认关=零回归；渲染机需有字体文件）')
    p.add_argument('--embed-photo', action='store_true',
                   help='方案A 照片内嵌：img 的 file:// 引用转 base64 data URI'
                        '（与 --embed-fonts 合用 = html 自包含；默认关；体积 +原图×1.37）')
    p.add_argument('--out', required=True, help='输出 HTML 路径')
    a = p.parse_args()
    # ---- 蓝图原 id 纯别名：解析为对应装裱款再走向下的 matting 分发（复用渲染，零重复模板）----
    # 别名只影响分发；资源/出图用解析后的装裱款 config（french→french_par_avion 等 2 条，
    # 2026-09-05 真删除后剩 2 条，chroma/polaroid/victorian/stamp 随目标款下线）。
    if a.genre in MATTING_ALIAS:
        a.genre = MATTING_ALIAS[a.genre]
    # --fg-texts 固定装饰文案覆盖（2026-09-24 死词参数化 b 方案）：格式 key=词;key2=词2
    # （分号分隔，键 = 该款 config layout.fixed 内键名——未知键名告警丢弃；值去首尾空白、
    # 保留内部空格与中文〔--words 先例口径〕，值内不允许分号；HTML 转义在渲染端统一做）。
    # 凡 config 声明了 layout.fixed 的款消费（render 内 cfg 合并，不进模板 kwargs）；
    # 其余款收到 → 显式打印提示忽略（同 --words 先例：不阻断渲染，参数语义透明）。
    fg_fixed = None
    if a.fg_texts:
        _d = {}
        for _seg in a.fg_texts.split(';'):
            if not _seg.strip():
                continue
            if '=' not in _seg:
                print(f'[engine_v2] --fg-texts 段缺 "="，忽略该段：{_seg.strip()}')
                continue
            _k, _v = _seg.split('=', 1)
            if not _k.strip():
                print(f'[engine_v2] --fg-texts 段缺键名，忽略该段：{_seg.strip()}')
                continue
            _d[_k.strip()] = _v.strip()
        if _d:
            if _fg_texts_supported(a.genre):
                # 键名校验：拼错键静默失效正是本功能要消灭的图文不符 → 显式告警丢弃；
                # 模板 .get 兜底键（如 exhibition 的 hero_sub/right_date）不在 fixed，
                # 一并按未知键拒绝——让「键 = fixed 键名」的 help/SKILL 声明严格成立。
                _known = set(DESIGN_CONFIGS[a.genre]['layout'].get('fixed') or {})
                _bad = sorted(k for k in _d if k not in _known)
                if _bad:
                    print(f'[engine_v2] --fg-texts 未知键名（非 {a.genre} layout.fixed 键），忽略：{"、".join(_bad)}')
                fg_fixed = {k: v for k, v in _d.items() if k in _known} or None
            else:
                print(f'[engine_v2] --fg-texts：{a.genre} 无固定装饰文案位（layout.fixed），忽略 {len(_d)} 键')
    # 落点背景亮度（分析像素所得，经 render 传入三族引擎与核心款；失败回退 None → 双影兜底）
    bg_luma = _bg_luma_for(a.photo)
    if a.genre in MATTING_CONFIGS:
        # 装裱/影格流派族：走 matting_engine，文字全参数化
        # EXIF 兜底（复用 _exif_location/_exif_lens）：GPS 定位只由 location 形参承担，meta_extra 只带 lens（不重复）
        loc = a.location or _exif_location(a.photo)
        meta_extra = a.lens or _exif_lens(a.photo)
        html = matting_engine.render(a.photo, MATTING_CONFIGS[a.genre], a.title, a.sub, a.date, loc,
                                     meta_extra=meta_extra, bg_luma=bg_luma,
                           photo_focus_y=a.photo_focus_y)
    elif a.genre in METAPHOR_CONFIGS:
        # 载体隐喻流派族：走 metaphor_engine，文字全参数化，mode='M' 仅为家族标记
        # photo_ratio 仅对 config 带该字段的款（music_manuscript）生效；其它款模板不读，行为不变
        # 隐喻族 playbill/lunar/viewfinder 把 L 当折目/诗词内容（非注脚），GPS 兜底会把坐标
        # 泄漏进折目/诗句槽（"定位变成折子名"）。按用户拍板 A2：隐喻族**整体**不用 GPS 兜底
        # （最简，避免逐款判断）——location 只用用户显式传的 a.location，不读 GPS；
        # 副作用：auction/dossier/score/arch 的注脚/来源位也不再自动带出 GPS（只有显式 --location）。
        # lens 兜底仍保留（meta_extra 只在有注脚位的款渲染）。见设计 §2.2。
        loc = a.location
        meta_extra = a.lens or _exif_lens(a.photo)
        html = metaphor_engine.render(a.photo, a.genre, a.title, a.sub, a.date, loc,
                                      photo_ratio=a.photo_ratio, meta_extra=meta_extra, bg_luma=bg_luma, photo_focus_y=a.photo_focus_y)
    elif a.genre in BLUEPRINT_CONFIGS:
        # 蓝图补齐流派族：走 blueprint_engine，文字全参数化，mode='B' 仅为家族标记
        loc = a.location or _exif_location(a.photo)
        meta_extra = a.lens or _exif_lens(a.photo)
        html = blueprint_engine.render(a.photo, BLUEPRINT_CONFIGS[a.genre], a.title, a.sub, a.date, loc,
                                       meta_extra=meta_extra, bg_luma=bg_luma, photo_focus_y=a.photo_focus_y)
    elif a.genre in DESIGN_CONFIGS:
        # 设计语言流派族（第 5 族）：走 design_engine，文字全参数化，mode='DESIGN' 仅为家族标记
        # GPS/lens 兜底策略对齐 blueprint 族：meta_extra 收 lens（super 目录 04 栏 / pop·tv 注脚位）
        loc = a.location or _exif_location(a.photo)
        meta_extra = a.lens or _exif_lens(a.photo)
        # --words 词墙用户词（2026-09-07 彩活四款）：仅 collage_man 消费（③层），
        # 其余款忽略——显式打印提示（不阻断渲染，参数语义透明）
        words = [w.strip() for w in a.words.split(',') if w.strip()] if a.words else None
        if words and a.genre != 'collage_man':
            print(f'[engine_v2] --words 仅 collage_man 消费，{a.genre} 忽略 {len(words)} 词')
        html = design_engine.render(a.photo, DESIGN_CONFIGS[a.genre], a.title, a.sub, a.date, loc,
                                    meta_extra=meta_extra, bg_luma=bg_luma,
                                    photo_focus_y=a.photo_focus_y, words=words, fg_fixed=fg_fixed)
    else:
        g = GENRE[a.genre]
        topo = a.topology or g['default_topology']
        mat = a.material or g['default_material']
        html = render_html(a.photo, a.genre, topo, mat, a.title, a.date, a.sub, a.location,
                           lens=a.lens, seed=a.seed, out_dir=os.path.dirname(os.path.abspath(a.out)),
                           font_safe=a.font_safe, seal=a.seal,
                           text_offset_x=a.text_offset_x, text_offset_y=a.text_offset_y, bg_luma=bg_luma,
                           photo_focus_y=a.photo_focus_y)
    # 输出目录兜底（2026-09-11）：--out 指向不存在的目录时先建。
    # 此前仅核心款 render_html 分支内部有 makedirs，blueprint/matting/metaphor/design
    # 四族分支在此 open 前无保护 → FileNotFoundError。统一在唯一出口兜底，对所有族幂等。
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if getattr(a, 'embed_fonts', False):
        html = _embed_fonts(html)
    if getattr(a, 'embed_photo', False):
        html = _embed_photo(html)
    with open(a.out, 'w', encoding='utf8') as f: f.write(html)
    print(a.out)

