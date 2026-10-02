#!/usr/bin/env python3
# 版式引擎（阶段一补齐）：读 flows.py 配方 → 生成 HTML/CSS/SVG 版式
# 独立文件，不 import render.py（那是 __main__ 脚本）；公共逻辑自成一体。
# 现有 #1 nocturne_vogue / #5 zen_landscape / #8 imperial_han 分支保持不动，
# 新增 #3 pulp_street / #7 stone_inscription / #9 film_rsx / #17 layered_underneath
# / #22 monumental_sky / #28 specimen_field，并按 P0-3 修正 #8 印章。
import argparse, os, shutil, random, hashlib, sys, base64, html as _html

# ---- 画布尺寸表（同 render.py）----
SIZES = {
    '3:4':  (1080, 1350),
    '4:3':  (1350, 1080),
    '16:9': (1350, 759),
    '9:16': (759, 1350),
    '1:1':  (1080, 1080),
}
FLOW_CHOICES = ['nocturne_vogue', 'zen_landscape', 'imperial_han',
                'pulp_street', 'stone_inscription', 'film_rsx',
                'layered_underneath', 'monumental_sky', 'specimen_field']

p = argparse.ArgumentParser()
p.add_argument('--photo', required=True, help='照片路径')
p.add_argument('--flow', required=True, choices=FLOW_CHOICES,
               help='流派（有限选择，9 套）')
p.add_argument('--title', default='夜色温存')
p.add_argument('--date', default='')
p.add_argument('--sub', default='')
p.add_argument('--location', default='')
p.add_argument('--lens', default='')
p.add_argument('--seed', type=int, default=7)
p.add_argument('--ratio', default='auto', choices=['auto'] + list(SIZES.keys()))
p.add_argument('--out', required=True)
a = p.parse_args()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flows import FLOWS, FONTS_CSS, SERIF_CN, SANS_CN

# ---- 比例检测（同 render.py）----
if a.ratio == 'auto':
    try:
        from PIL import Image as _PILImg
        _pw, _ph = _PILImg.open(a.photo).size
        _r = _pw / _ph
        if _r >= 1.6: RATIO = '16:9'
        elif _r >= 1.25: RATIO = '4:3'
        elif _r > 0.9: RATIO = '1:1'
        elif _r > 0.6: RATIO = '3:4'
        else: RATIO = '9:16'
    except Exception:
        RATIO = '3:4'
else:
    RATIO = a.ratio
W, H = SIZES[RATIO]

# ---- 地点：EXIF 或手动 ----
LOCATION = a.location
if not LOCATION:
    try:
        from PIL import Image as _PILImg
        from PIL.ExifTags import TAGS, GPSTAGS
        _exif = _PILImg.open(a.photo).getexif()
        _gps = {}
        for tag_id, val in _exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'GPSInfo':
                for k, v in val.items():
                    _gps[GPSTAGS.get(k, k)] = v
        def _to_deg(val):
            d, m, s = val
            return float(d) + float(m)/60 + float(s)/3600
        if 'GPSLatitude' in _gps and 'GPSLongitude' in _gps:
            lat = _to_deg(_gps['GPSLatitude']); lon = _to_deg(_gps['GPSLongitude'])
            if _gps.get('GPSLatitudeRef') == 'S': lat = -lat
            if _gps.get('GPSLongitudeRef') == 'W': lon = -lon
            LOCATION = f"{lat:.4f}°N {lon:.4f}°E"
    except Exception:
        pass
if not LOCATION:
    LOCATION = 'UNKNOWN'

# ---- 镜头：EXIF 或默认 ----
LENS = a.lens
if not LENS:
    try:
        from PIL import Image as _PILImgL
        _exif_l = _PILImgL.open(a.photo).getexif()
        _fl = _exif_l.get(37386); _fn = _exif_l.get(33437); _iso = _exif_l.get(34855)
        _lp = []
        if _fl: _lp.append(f'{int(_fl)}MM')
        if _fn: _lp.append(f'F{float(_fn):.1f}')
        if _iso: _lp.append(f'ISO {int(_iso)}')
        if _lp: LENS = ' · '.join(_lp)
    except Exception:
        pass
if not LENS:
    LENS = '28MM · F2.0 · ISO 200'

# ---- 照片复制：唯一文件名防覆盖 ----
outdir = os.path.dirname(os.path.abspath(a.out))
os.makedirs(outdir, exist_ok=True)
_ph_hash = hashlib.md5(os.path.abspath(a.photo).encode()).hexdigest()[:8]
_ph_ext = os.path.splitext(a.photo)[1].lower() or '.jpg'
if _ph_ext not in ('.jpg', '.jpeg', '.png', '.webp'):
    _ph_ext = '.jpg'
IMG = f'eng_{_ph_hash}{_ph_ext}'
_dst = os.path.join(outdir, IMG)
if os.path.abspath(a.photo) != _dst:
    shutil.copy(a.photo, _dst)

def esc(s):
    return _html.escape(s, quote=True)
title = esc(a.title); date = esc(a.date); sub = esc(a.sub)
LOCATION_E = esc(LOCATION); LENS_E = esc(LENS)

# ---- 缩放因子（同 render.py 风格9 写法）----
if W > H:
    fx, fy = W / 1350, H / 1080
else:
    fx, fy = W / 1080, H / 1350
fs = min(fx, fy)  # 字号缩放防窄幅溢出

# ---- 胶片颗粒（供 #9 使用）----
_GRAIN = ("<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
          "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.4' numOctaves='3'/>"
          "<feColorMatrix type='saturate' values='0'/></filter>"
          "<rect width='300' height='300' filter='url(#n)' opacity='0.7'/></svg>")
GRAIN_URI = 'data:image/svg+xml;base64,' + base64.b64encode(_GRAIN.encode()).decode()

flow = FLOWS[a.flow]
L = flow['layout']
F = flow['fonts']
SC = flow['scale']
PA = flow['palette']
Z = flow['z_layers']
FEMO = F.get('emotion', F['hero'])          # 副标/正文字体（缺省回退 hero）
FDATA = F.get('data', 'SpaceMono')          # 等宽数据字体

# ---- HEAD 骨架 ----
HEAD = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
.stage{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
img.ph{{display:block;width:100%;height:100%;object-fit:cover}}
</style></head><body><div class="stage"><img class="ph" src="{IMG}">"""

# ---- 主标字号宽度预算（蓝图 05：字号×字数 ≥ 画布，则按宽度收缩防超宽）----
title_units = len(title.replace(' ', ''))  # 去空格后的字数（Mega 建议 2-4 字）
max_w = int(W * 0.90)
if title_units > 0:
    _per_unit = max_w / max(title_units, 1)
    hero_fs = int(min(SC['hero_px'] * fs, _per_unit * 1.5))
else:
    hero_fs = int(SC['hero_px'] * fs)

# ---- 自适应主体检测（P0-8 实测驱动）：判断主体偏左/偏右，文字放对侧负空间 ----
def detect_subject_zone(photo_path):
    """A1 区域级主体感知：检测主体在画面的左右 + 上下分布。
    返回 dict: {'h': 'left'|'right'|'center', 'v': 'top'|'bottom'|'center'}。
    纯像素启发（边缘强度+亮度对齐），零多模态。"""
    try:
        from PIL import Image
        im = Image.open(photo_path).convert('L').resize((16, 16))
        px = list(im.getdata())
        # 四象限平均亮度 + 边缘强度；主体=细节多(边缘强)且与背景亮度反差大的区
        def cell(x0,x1,y0,y1):
            vals=[px[y*16+x] for y in range(y0,y1) for x in range(x0,x1)]
            mean=sum(vals)/len(vals)
            edge=sum(abs(a-b) for a,b in zip(vals,vals[1:]))/len(vals)
            return mean, edge
        TL=cell(0,8,0,8); TR=cell(8,16,0,8)
        BL=cell(0,8,8,16); BR=cell(8,16,8,16)
        def weight(c):
            m,e=c; return e*(1+abs(m-128)/128)  # 亮度偏离中间+边缘强 = 主体
        wl=weight(TL)+weight(BL); wr=weight(TR)+weight(BR)
        wt=weight(TL)+weight(TR); wb=weight(BL)+weight(BR)
        h='center'
        if wr>wl*1.12: h='right'
        elif wl>wr*1.12: h='left'
        v='center'
        if wb>wt*1.12: v='bottom'
        elif wt>wb*1.12: v='top'
        return {'h':h, 'v':v}
    except Exception:
        return {'h':'center', 'v':'center'}

SUBJECT_ZONE = detect_subject_zone(a.photo)
SUBJECT_SIDE = SUBJECT_ZONE['h']   # 向后兼容：h 即左右

body = ''

# ================= #1 时尚夜曲封面 (nocturne_vogue) =================
if a.flow == 'nocturne_vogue':
    shade_top = int(L['masthead_top_px'])
    shade_h = int(H * L['shade_height_ratio'])
    subtitle_top = int(H * (L['subtitle_top_ratio'] + 0.10))  # 下移，防与主标重叠
    caption_bottom = int(H * L['caption_bottom_ratio'])
    # 顶部墨韵渐变（防吞没）
    body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{shade_h}px;z-index:{Z['shade']};background:{L['shade_grad']}'></div>
"""
    # 大刊头（正文）
    body += f"""
<div style='position:absolute;top:{shade_top}px;left:50px;right:50px;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{hero_fs}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{PA['accent']};text-shadow:{SC['hero_shadow']}'>{title}</div>
</div>
"""
    # 中文副标（人文）
    body += f"""
<div style='position:absolute;top:{subtitle_top}px;left:50px;right:50px;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;color:#fff;letter-spacing:.3em;text-shadow:{SC['hero_shadow']}'>{sub}</div>
</div>
"""
    # 底部图说卡 + ISSN 条形码
    caption = f'{date}' if date else ''
    if LOCATION_E: caption = caption + (' · ' if caption else '') + LOCATION_E
    if LENS_E: caption = caption + (' · ' if caption else '') + LENS_E
    barcode = L['issn']
    body += f"""
<div style='position:absolute;left:56px;right:56px;bottom:{caption_bottom}px;z-index:{Z['caption']};display:flex;justify-content:space-between;align-items:flex-end'>
  <div style='background:rgba(6,5,4,.55);backdrop-filter:blur(8px);padding:12px 16px;color:#e9dfd0;font:11px "SpaceMono",monospace;letter-spacing:.3em'>{caption}</div>
  <div style='background:rgba(6,5,4,.55);backdrop-filter:blur(8px);padding:10px 14px;color:#d49b6a;font:10px "SpaceMono",monospace;letter-spacing:.22em;text-align:right'>{barcode}<br><span style='opacity:.6'>POCKET EDITORIAL</span></div>
</div>
"""

# ================= #5 东方泼墨长卷 (zen_landscape) =================
if a.flow == 'zen_landscape':
    # 玄墨深字（防吞没：借死白天空以实击虚）
    ink = L.get('ink_color', PA['primary'])
    top_px = L['calligraphy_top_px']
    margin_px = L['calligraphy_right_px']
    gap = L['col_gap_px']
    lead_mt = L['lead_margin_top_px']
    meta_mt = L['meta_margin_top_px']
    # 自适应主体：主体在右→主字放左；主体在左→主字放右；居中→默认放左(最安全,不压主体)
    _mast_side = 'left' if SUBJECT_SIDE != 'left' else 'right'   # 主体在左→字放右; 否则字放左
    _pos = f"{_mast_side}:{int(margin_px*fx)}px"
    # 竖排书法矩阵：主标 + 副标 + meta 三列，列间错落（vertical-rl），文字放主体对侧
    body += f"""
<div style='position:absolute;top:{int(top_px*fy)}px;{_pos};z-index:{Z['calligraphy']};display:flex;flex-direction:row-reverse;gap:{int(gap*fx)}px'>
  <div style='font-family:"{F['hero']}";font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};writing-mode:vertical-rl;color:{ink};text-shadow:{SC['hero_shadow']}'>{title}</div>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;letter-spacing:.35em;writing-mode:vertical-rl;color:{ink};margin-top:{int(lead_mt*fy)}px;opacity:.85'>{sub}</div>
  <div style='font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;letter-spacing:.45em;writing-mode:vertical-rl;color:{ink};margin-top:{int(meta_mt*fy)}px;opacity:.55'>{date}·{LOCATION_E}</div>
</div>
"""
    # 朱印（左下，rotate）
    seal_rot = L.get('seal_rotate', -2)
    seal_color = L.get('seal_color', PA['point'])
    # 朱印跟款走：放在竖排主标末端下方，与主字同侧（P0-3 印随款走）
    if _mast_side == 'left':
        _seal_h = f"left:{int(margin_px*fx + 10*fx)}px"
    else:
        _seal_h = f"right:{int(margin_px*fx + 10*fx)}px"
    # 主标竖排末端：top_px + 主标高度(字号×字数)；印章放其下方，同列
    _seal_size = int(46*fs)
    _seal_top = int(top_px*fy + hero_fs*len(title.replace(' ','')) + 30*fy)
    # 2×2 田字格白文印（与 stone 同款，符合 P0-3：四字回字序/铺满/白文/内框）
    _sgs = ['石', '佛', '無', '言']
    def _cellz(x, y, ch):
        return (f"<div style='position:absolute;left:{x}%;top:{y}%;width:50%;height:50%;"
                f"display:flex;align-items:center;justify-content:center;"
                f"font-family:\"{F['hero']}\",{SERIF_CN};font-weight:900;color:#fff;"
                f"font-size:{int(_seal_size*0.42)}px;line-height:1'>{ch}</div>")
    _cell = _cellz(0,0,_sgs[0]) + _cellz(50,0,_sgs[1]) + _cellz(0,50,_sgs[2]) + _cellz(50,50,_sgs[3])
    body += f"""
<div style='position:absolute;top:{_seal_top}px;{_seal_h};z-index:20;width:{_seal_size}px;height:{_seal_size}px;background:{seal_color};transform:rotate({seal_rot}deg);box-shadow:0 0 0 2px rgba(255,255,255,.5) inset, 0 8px 22px rgba(0,0,0,.5)'><div style='position:absolute;inset:8%;border:1px solid rgba(255,255,255,.72)'>{_cell}</div></div>
"""

# ================= #8 汉唐金石重器典藏 (imperial_han) =================
# ── P0-3 章法修正：原 `國寶` 红框悬空印章不合规范，改为规范朱印 ──
# 印随款走（竖排钤在副标/款末端）· 用繁体全字库 · 比例上限 ≤ 主标字高×0.55
# · 铺满田字格（2×2 白文）· 钤白不钤实（落在空白负空间，不压主体）
if a.flow == 'imperial_han':
    gold = L['gold_hex']
    mast_top = L['masthead_top_px']
    sub_top = int(H * L['subtitle_top_ratio'])
    foot_bot = L['footnote_bottom_px']
    body += f"""
<div style='position:absolute;top:{int(mast_top*fy)}px;left:0;right:0;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{F['hero']}";font-size:{hero_fs}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{SC['hero_color']};text-shadow:{SC['hero_shadow']};text-transform:uppercase'>{title}</div>
</div>
"""
    # 中文副标（特粗宋体）
    body += f"""
<div style='position:absolute;top:{int(sub_top*fy)}px;left:0;right:0;z-index:{Z['subtitle']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:#fff;letter-spacing:.2em;text-shadow:0 4px 20px rgba(0,0,0,.9)'>{sub}</div>
</div>
"""
    # 底部史实注脚
    body += f"""
<div style='position:absolute;left:0;right:0;bottom:{int(foot_bot*fy)}px;z-index:{Z['footnote']};text-align:center'>
  <div style='font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;color:{L.get('note_color','#ffd288')};letter-spacing:.3em'>{date}{' · ' if date else ''}{LOCATION_E} · {LENS_E}</div>
</div>
"""
    # ── 规范朱印：2×2 白文田字格，铺满、繁体、悬空落于左下空白负空间（不压主体）──
    seal_red = L.get('seal_red', '#c43d2f')
    _seal = L.get('seal_grid', ['南', '博', '珍', '藏'])   # 2×2 田字格（繁体）
    seal_size = int(min(hero_fs * 0.55, 130))     # 比例上限 ≤ 主标字高 × 0.55
    _cell = f'''<div style='position:absolute;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.42)}px;letter-spacing:.02em'>{ _seal[0] }</div><div style='position:absolute;left:50%;width:50%;height:50%;top:0;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.42)}px'>{ _seal[1] }</div><div style='position:absolute;top:50%;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.42)}px'>{ _seal[2] }</div><div style='position:absolute;left:50%;top:50%;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.42)}px'>{ _seal[3] }</div>'''
    body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(60*fy)}px;width:{seal_size}px;height:{seal_size}px;z-index:25;background:{seal_red};transform:rotate(-3deg);box-shadow:0 0 0 2px rgba(255,255,255,.55) inset, 0 6px 18px rgba(0,0,0,.45)'>
  <div style='position:absolute;inset:8%;border:1px solid rgba(255,255,255,.75)'></div>
  {_cell}
</div>
"""

# ================= #3 先锋大字街拍 (pulp_street) =================
if a.flow == 'pulp_street':
    shade_h = int(H * L['shade_height_ratio'])
    hdr_top = int(L['hdr_top_px'])
    title_top = int(H * L['title_top_ratio'])
    sub_top = int(H * L['sub_gap_ratio'])
    toc_bot = int(H * L['toc_bottom_ratio'])
    cap_bot = int(H * L['caption_bottom_ratio'])
    toc = L.get('toc', [])
    # 顶部墨韵渐变（防吞没）
    body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{shade_h}px;z-index:{Z['shade']};background:{L['shade_grad']}'></div>
"""
    # 顶部刊头（ISSUE / VOL 小字）
    body += f"""
<div style='position:absolute;top:{hdr_top}px;left:{int(52*fx)}px;right:{int(52*fx)}px;z-index:{Z['masthead']};display:flex;justify-content:space-between;align-items:flex-start'>
  <div style='font:{int(12*fs)}px "SpaceMono",monospace;color:{PA['accent']};letter-spacing:.4em;opacity:.9;line-height:1.8'>{L['issueno']}<br>{L['issue_meta']}</div>
  <div style='font:{int(12*fs)}px "SpaceMono",monospace;color:{PA['accent']};letter-spacing:.3em;opacity:.9;text-align:right'>{L['badge']}</div>
</div>
"""
    # 主标大字（优设标题黑，简体系）；A1 主体避让：主体在右→主标靠左，主体在左→主标靠右
    if SUBJECT_ZONE['h'] == 'right':
        _pulp_align = 'left'; _pulp_w = '52%'
    elif SUBJECT_ZONE['h'] == 'left':
        _pulp_align = 'right'; _pulp_w = '52%'
    else:
        _pulp_align = 'center'; _pulp_w = '90%'
    body += f"""
<div style='position:absolute;top:{title_top}px;left:{int(40*fx)}px;right:{int(40*fx)}px;z-index:{Z['masthead']};text-align:{_pulp_align}'>
  <div style='display:inline-block;font-family:"{F['hero']}";font-weight:900;font-size:{hero_fs}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{PA['accent']};text-shadow:{SC['hero_shadow']}'>{title}</div>
</div>
"""
    # 副标（人文）
    body += f"""
<div style='position:absolute;top:{sub_top}px;left:{int(56*fx)}px;right:{int(56*fx)}px;z-index:{Z['masthead']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;color:{PA['accent']};letter-spacing:.5em;opacity:.9;text-shadow:{SC['hero_shadow']}'>{sub}</div>
</div>
"""
    # 多栏 TOC 目录舱（左下角，等宽字）
    toc_html = ''.join(f'<div style="margin-top:8px;font-size:{int(11*fs)}px;letter-spacing:.4em;opacity:.75">{i:02d} · {t}</div>' for i, t in enumerate(toc, 1))
    body += f"""
<div style='position:absolute;left:{int(52*fx)}px;bottom:{toc_bot}px;z-index:{Z['caption']};background:rgba(16,16,19,.55);backdrop-filter:blur(10px);padding:16px 20px;color:{PA['accent']};border:1px solid rgba(245,243,236,.18);min-width:{int(280*fx)}px'>
  <div style='font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.5em;opacity:.7;border-bottom:1px solid rgba(245,243,236,.22);padding-bottom:8px'>CONTENTS / 目錄</div>
  {toc_html}
</div>
"""
    # 底部参数卡（backdrop-filter 防吞没）
    cap = f'{date}' if date else ''
    if LOCATION_E: cap = cap + (' · ' if cap else '') + LOCATION_E
    if LENS_E: cap = cap + (' · ' if cap else '') + LENS_E
    body += f"""
<div style='position:absolute;left:{int(52*fx)}px;right:{int(52*fx)}px;bottom:{cap_bot}px;z-index:{Z['caption']};display:flex;justify-content:space-between;align-items:flex-end'>
  <div style='background:rgba(16,16,19,.55);backdrop-filter:blur(10px);padding:12px 16px;color:{PA['accent']};font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.3em'>{cap}</div>
  <div style='background:rgba(16,16,19,.55);backdrop-filter:blur(10px);padding:10px 14px;color:{PA['point']};font:{int(10*fs)}px "SpaceMono",monospace;letter-spacing:.22em;text-align:right'>{L['masthead_brand']}<br><span style='opacity:.6'>PULP STREET</span></div>
</div>
"""

# ================= #7 宣纸金石碑拓 (stone_inscription) =================
# 繁体验证点：主标用繁体 + 全字库 SourceSerifHeavy；严禁用秋鸿楷/春风楷（简字库缺繁体）
if a.flow == 'stone_inscription':
    ink = L.get('ink_color', PA['primary'])
    top_px = L['title_top_px']
    left_px = L['title_left_px']
    gap = L['col_gap_px']
    lead_mt = L['lead_margin_top_px']
    # 墨韵防吞没：只保留极淡暗纹，取消过强的上下渐变（避免盖住主体）
    body += f"""
<div style='position:absolute;left:0;right:0;top:0;height:{int(H*0.22)}px;z-index:{Z['wash']};background:linear-gradient(180deg, rgba(23,19,13,0.16) 0%, transparent 100%)'></div>
<div style='position:absolute;left:0;right:0;bottom:0;height:{int(H*0.14)}px;z-index:{Z['wash']};background:linear-gradient(0deg, rgba(23,19,13,0.22) 0%, transparent 100%)'></div>
"""
    # 云雷纹回形金边（连续回纹）
    body += f"""
<div style='position:absolute;inset:{int(24*fx)}px;z-index:{Z['frame']};border:{int(1.5*fx)}px solid rgba(212,175,55,.55);pointer-events:none'>
  <div style='position:absolute;inset:8px;border:{int(6*fx)}px solid rgba(212,175,55,.18);margin:3px;background-image:{L['frame_border']};background-size:14px 14px;height:100%;opacity:.5'></div>
</div>
"""
    # 竖排书法：主标（繁体全字库）+ 款（霞鹜文楷）；主体在右，落左侧负空间
    body += f"""
<div style='position:absolute;top:{int(top_px*fy)}px;left:{int(left_px*fx)}px;z-index:{Z['calligraphy']};display:flex;flex-direction:row;gap:{int(gap*fx)}px'>
  <div style='font-family:"{F['hero']}",{SERIF_CN};font-weight:900;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};writing-mode:vertical-rl;color:{ink};text-shadow:{SC['hero_shadow']}'>{title}</div>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-size:{int(SC['lead_px']*fs)}px;letter-spacing:.4em;writing-mode:vertical-rl;color:{ink};margin-top:{int(lead_mt*fy)}px;opacity:.9'>{sub}</div>
</div>
"""
    # 朱砂朱文连珠印章（P0-3：印随款走 / 繁体 / 铺满 / 悬空 / 比例上限）
    seal_red = L.get('seal_red', '#b83c23')
    _sg = L.get('seal_grid', ['金', '石', '永', '固'])       # 2×2 田字格
    seal_size = int(min(SC['hero_px'] * L['seal_size_ratio'], 120))
    _cell = f'''<div style='position:absolute;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.40)}px'>{ _sg[0] }</div><div style='position:absolute;left:50%;top:0;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.40)}px'>{ _sg[1] }</div><div style='position:absolute;top:50%;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.40)}px'>{ _sg[2] }</div><div style='position:absolute;left:50%;top:50%;width:50%;height:50%;display:flex;align-items:center;justify-content:center;font-family:"{FEMO}",{SERIF_CN};font-weight:900;color:#fff;font-size:{int(seal_size*0.40)}px'>{ _sg[3] }</div>'''
    body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(72*fy)}px;width:{seal_size}px;height:{seal_size}px;z-index:{Z['seal']};background:{seal_red};transform:rotate({L['seal_rotate']}deg);box-shadow:0 0 0 2px rgba(255,255,255,.5) inset, 0 8px 22px rgba(0,0,0,.5)'>
  <div style='position:absolute;inset:9%;border:1px solid rgba(255,255,255,.72)'></div>
  {_cell}
</div>
"""

# ================= #9 胶片齿孔档案卷 (film_rsx) =================
if a.flow == 'film_rsx':
    edge_w = L['edge_w']; hole_w = L['hole_w']; hole_h = L['hole_h']
    hole_r = L['hole_r']; gap = L['hole_gap']
    sepia = L.get('sepia', 0.55)
    n = int(H / gap)
    hole_left = int(edge_w / 2 - hole_w / 2)
    hole_right = W - edge_w + int(edge_w / 2 - hole_w / 2)
    # 暖褐调 + 颗粒（防吞没）
    body += f"""
<style>
.stage .ph{{filter:sepia({sepia}) saturate(1.05) contrast(1.05) brightness(0.98)}}
.grain{{position:absolute;inset:0;z-index:{Z['grain']};background:url('{GRAIN_URI}');opacity:.20;mix-blend-mode:overlay;pointer-events:none}}
/* 竖图安全：齿孔带改上下横带（顶部单轨 + 底部片尾），横向留白给主体 */
.edge{{position:absolute;left:0;right:0;height:{edge_w}px;z-index:{Z['film']};background:linear-gradient(90deg,#2c1d10,#170d06)}}
.edge.t{{top:0;border-bottom:2px solid #000}}
.edge.b{{bottom:0;border-top:2px solid #000}}
.hole{{position:absolute;width:{hole_h}px;height:{hole_w}px;border-radius:{hole_r}px;background:#f4ead6;z-index:6;box-shadow:inset 2px 0 3px rgba(0,0,0,.45)}}
</style>
<div class='edge t'></div>
<div class='edge b'></div>
"""
    # 上下横带内横排齿孔
    for i in range(int(W / gap) + 1):
        x = int(i * gap) + 20
        if x + hole_h <= W:
            body += f"<div class='hole' style='left:{x}px;top:{(edge_w-hole_w)//2}px'></div>"
            body += f"<div class='hole' style='left:{x}px;bottom:{(edge_w-hole_w)//2}px'></div>"
    # 划痕/脏点 SVG 叠加
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
    # AGFA 工业印字竖排 + 帧号
    body += f"""
<div style='position:absolute;left:{int(8*fx)}px;top:{int(90*fy)}px;z-index:{Z['title']};writing-mode:vertical-rl;font:{int(13*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.45em;opacity:.85'>{L['brand']}</div>
<div style='position:absolute;right:{int(8*fx)}px;top:{int(90*fy)}px;z-index:{Z['title']};writing-mode:vertical-rl;font:{int(13*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.45em;opacity:.85'>{L['film_type']}</div>
<div style='position:absolute;right:{int(6*fx)}px;top:{int(24*fy)}px;z-index:{Z['title']};font:{int(12*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.2em'>{L['frame_no']}</div>
<div style='position:absolute;left:{int(70*fx)}px;bottom:{int(78*fy)}px;z-index:{Z['title']};font:{int(11*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.32em;opacity:.8'>{date} · {LOCATION_E} · {LENS_E}</div>
"""
    # 片名（系统宋体）
    body += f"""
<div style='position:absolute;left:{int(L['title_left_px']*fx)}px;right:{int(L['title_left_px']*fx)}px;top:{int(L['title_top_px']*fy)}px;z-index:{Z['title']};text-align:left'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:700;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};color:{PA['accent']};letter-spacing:.12em;text-shadow:{SC['hero_shadow']}'>{title}</div>
  <div style='margin-top:{int(20*fy)}px;font-family:"{FDATA}",monospace;font-size:{int(SC['lead_px']*fs)}px;color:{PA['point']};letter-spacing:.3em'>{sub}</div>
</div>
"""
    body += f"<div class='grain'></div>"

# ================= #17 压底穿插 (layered_underneath) =================
# 印章禁用点（P0-3）：现代流派禁用传统红印章 → 用几何标贴/条形码替代
if a.flow == 'layered_underneath':
    # Cinzel 巨字压入左侧（主体佛像在右侧负空间 = 影子区）；白字黑晕防吞没
    giant = L['giant_word']
    giant_top = int(H * L['giant_top_ratio'])
    giant_left = int(L['giant_left_px'] * fx)
    giant_angle = L['giant_angle']
    body += f"""
<div style='position:absolute;top:{giant_top}px;left:{giant_left}px;z-index:{Z['giant']};transform:rotate({giant_angle}deg)'>
  <div style='font-family:"{F['hero']}";font-weight:900;font-size:{int(SC['hero_px']*fs)}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:rgba(242,239,232,0.66);text-shadow:{SC['hero_shadow']};white-space:nowrap'>{giant}</div>
</div>
"""
    # 几何标贴（替代红印章）：条形码 + 几何块
    body += f"""
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(L['caption_bottom_px']*fy)}px;z-index:{Z['caption']};width:{int(220*fx)}px;height:{int(46*fy)}px;background:repeating-linear-gradient(90deg,#f2efe8 0 2px,transparent 2px 5px,#f2efe8 5px 8px,transparent 8px 10px,#f2efe8 10px 12px,transparent 12px 16px);box-shadow:0 0 0 8px rgba(13,13,15,.5)'></div>
<div style='position:absolute;left:{int(64*fx)}px;bottom:{int(118*fy)}px;z-index:{Z['caption']};background:#f2efe8;color:#0d0d0f;padding:8px 12px;font:{int(11*fs)}px "SpaceMono",monospace;letter-spacing:.3em'>{L['badge_text']}</div>
"""
    # 文案（data 档案）
    cap2 = f'{date}' if date else ''
    if LOCATION_E: cap2 = cap2 + (' · ' if cap2 else '') + LOCATION_E
    if LENS_E: cap2 = cap2 + (' · ' if cap2 else '') + LENS_E
    body += f"""
<div style='position:absolute;right:{int(64*fx)}px;bottom:{int(L['caption_bottom_px']*fy)}px;z-index:{Z['caption']};text-align:right'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:#f2efe8;letter-spacing:.2em;text-shadow:0 2px 10px rgba(0,0,0,.8)'>{sub}</div>
  <div style='margin-top:8px;font:{int(10*fs)}px "SpaceMono",monospace;color:#cfc8bb;letter-spacing:.3em'>{cap2}</div>
</div>
"""

# ================= #22 君临天幕帝国 (monumental_sky) =================
if a.flow == 'monumental_sky':
    gold = L['gold_hex']
    mast_top = L['masthead_top_px']
    # 天幕巨字（用户已拍板：接受"巨字叠合"是流派本性——巨字居中天幕，字透画面不遮脸）
    _mono_align = 'center'
    sub_top = int(H * L['subtitle_top_ratio'])
    foot_bot = L['footnote_bottom_px']
    # 240-280px 纯金巨字充斥天穹（顶置全幅居中，半透明金字 + 深阴影"气场环抱"不遮主体）
    body += f"""
<div style='position:absolute;top:{int(mast_top*fy)}px;left:0;right:0;z-index:{Z['masthead']};text-align:{_mono_align}'>
  <div style='display:inline-block;font-family:"{F['hero']}";font-weight:900;font-size:{hero_fs}px;line-height:{SC['hero_lh']};letter-spacing:{SC['hero_letter']};color:{SC['hero_color']};text-shadow:{SC['hero_shadow']};text-transform:uppercase'>{title}</div>
</div>
"""
    # 中文副标（白字黑晕）
    body += f"""
<div style='position:absolute;top:{sub_top}px;left:0;right:0;z-index:{Z['subtitle']};text-align:center'>
  <div style='font-family:"{FEMO}",{SERIF_CN};font-weight:900;font-size:{int(SC['lead_px']*fs)}px;color:#fff;letter-spacing:.25em;text-shadow:0 6px 24px rgba(0,0,0,.95)'>{sub}</div>
</div>
"""
    # 注脚
    body += f"""
<div style='position:absolute;left:0;right:0;bottom:{int(foot_bot*fy)}px;z-index:{Z['footnote']};text-align:center'>
  <div style='font-family:"{FDATA}",monospace;font-size:{int(SC['micro_px']*fs)}px;color:#e6d29b;letter-spacing:.32em'>{date}{' · ' if date else ''}{LOCATION_E} · {LENS_E}</div>
</div>
"""

# ================= #28 科考标本参数卡 (specimen_field) =================
if a.flow == 'specimen_field':
    photo_h = int(H * L['photo_height_ratio'])
    arch_top = int(H * L['arch_top_ratio'])
    arch_h = int(H * L['arch_height_ratio'])
    cells = [
        ('主体', '石佛造像'), ('时代', '南朝'), ('材质', '石灰岩'),
        ('编号', 'NM-BS-008'), ('尺寸', '通高 82cm'), ('收藏', '南京博物院'),
        ('光影', '自然光'), ('状态', '保存完好'),
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
    # 取景十字瞄准线（中心）+ 四角 L 形
    body += f"<div class='cross-x'></div><div class='cross-y'></div>"
    body += f"<div class='corner c-tl'></div><div class='corner c-tr'></div><div class='corner c-bl'></div><div class='corner c-br'></div>"
    # 上部照片窗标注
    body += f"""
<div style='position:absolute;top:{int(20*fy)}px;left:{int(28*fx)}px;z-index:{Z['crosshair']}'>
  <div style='font:{int(11*fs)}px "Courier New",monospace;color:{PA['accent']};letter-spacing:.35em;opacity:.9'>{L['title_frame']}</div>
  <div style='margin-top:4px;font:{int(10*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.2em'>REC · NO.008</div>
</div>
"""
    # 下部档案卡（4 栏等宽数据卡；背景比照片窗深 → 为照片留呼吸）
    body += f"""
<div style='position:absolute;left:0;right:0;top:{arch_top}px;height:{arch_h}px;z-index:{Z['arch']};background:#0c1013;border-top:1px solid rgba(233,236,239,.12)'>
  <div style='padding:8px 24px 0 24px;display:flex;justify-content:space-between;align-items:baseline'>
    <div style='font-family:"{F['hero']}",{SANS_CN};font-weight:900;font-size:{int(SC['hero_px']*fs)}px;color:{PA['accent']};letter-spacing:{SC['hero_letter']};text-transform:uppercase'>{title}</div>
    <div style='font:{int(11*fs)}px "Courier New",monospace;color:{PA['point']};letter-spacing:.3em'>{date} · {LOCATION_E}</div>
  </div>
  <div style='margin:6px 24px 0 24px;display:grid;grid-template-columns:repeat({L['grid_cols']},1fr);border:1px solid rgba(233,236,239,.12)'>{cell_html}</div>
</div>
"""
    # 底部条形码
    body += f"""
<div style='position:absolute;right:24px;bottom:{int(28*fy)}px;z-index:{Z['arch']};width:{int(190*fx)}px;height:{int(44*fy)}px;background:repeating-linear-gradient(90deg,#e9ecef 0 2px,transparent 2px 5px,#e9ecef 5px 8px,transparent 8px 10px,#e9ecef 10px 12px,transparent 12px 15px)'></div>
"""

html = HEAD + body + '</div></body></html>'

with open(a.out, 'w', encoding='utf-8') as f:
    f.write(html)
print(a.out)
print(f'flow={a.flow} ratio={RATIO} canvas={W}x{H}', file=sys.stderr)
