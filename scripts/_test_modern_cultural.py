#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新款入库批 · 开发期单测（docs/新款入库批-设计.md §7 用例表 T1–T19 + 审查守卫 T20–T21 / 验收 A1–A12 断言面）。
用法：python scripts/_test_modern_cultural.py
批次收口时按测试寿命纪律处置（默认退役；业务可观察 + 集成未覆盖才转 ②③，落批次档 §6）。"""
import io
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from design_configs import DESIGN_CONFIGS
from design_engine import render
import design_engine
import font_guard
from type_guard import fit_title_fs

PHOTO = 'D:/cover-plan/_t.jpg'          # 真实照片（仓根 _t.jpg；A7 样张另用 _w.jpg）
ARGS = ('古镇长巷', 'OLD TOWN ALLEY', '2026.09.15', 'SUZHOU')
ARGS_CJ = ('古镇漫步', '纪录片系列 · DOCUMENTARY SERIES', '2023.10.01', 'GUZHEN')
ARGS_EMPTY = ('', '', '', '')

_ok, _fail = [], []


def _check(name, cond, detail=''):
    (_ok if cond else _fail).append(name + (f' [{detail}]' if detail and not cond else ''))


def _re_escape(s):
    return re.escape(s)


def _html(g, *args, **kw):
    return render(PHOTO, DESIGN_CONFIGS[g], *args, **kw)


def _px(value):
    """px 断言容差：`_svf` 亚像素口径输出 `3.0px` / `64.0px` / `12.5px`（D-9），
    故 `3px` 与 `3.0px` 等价——勿按整数字面匹配（本轮 4 条假红即此因）。"""
    return re.escape(str(value)) + r'(?:\.0)?px'


def _cj_h1_fs(html):
    """cj 中文大标行的 font-size（§2.4 fit 注口径行：line-height:1.0 / 0.10em / accent #3E2F26）。"""
    m = re.search(r'font-size:(\d+)px;line-height:1\.0;letter-spacing:0\.10em;color:#3E2F26', html)
    return int(m.group(1)) if m else None


# ---- T1 · modern_spread 3:4 结构（A1）----
t1 = _html('modern_spread', *ARGS)
_check('T1 img count == 1（R1 无画中画）', t1.count('<img') == 1, t1.count('<img'))
_check('T1 粗横线 3px', bool(re.search(r'height:' + _px(3), t1)))
_check('T1 细横线/竖线/底线 1.5px', t1.count('1.5px') >= 4)
_check('T1 Prata 西文行（64px/0.02em）', 'font-family:&quot;Prata&quot;' in t1
       and bool(re.search(r'font-size:' + _px(64), t1)) and '0.02em' in t1)
_check('T1 思源黑 Heavy 中文行（48px/0.10em）', 'font-family:&quot;SourceHanSansHeavy&quot;' in t1 and 'font-size:48px' in t1)
_check('T1 三段元数据条 space-between', 'justify-content:space-between' in t1 and 'JOURNEYS INTO HERITAGE' in t1)
_check('T1 照片框 52/265/796×807（O-4 终值）', 'left:52px;top:265px;width:796px;height:807px' in t1)
_check('T1 照片 1px 细框 #191B1D', 'border:1px solid #191B1D' in t1)
_check('T1 页脚两行（feat_bold + ISSUED 2026）', 'THE SOUL OF WATER TOWNS' in t1 and 'ISSUED 2026' in t1)
_check('T1 底色 #D6CEBB（R7）', 'background:#D6CEBB' in t1)
_check('T1 照片无 filter（P0-1）', 'filter:' not in t1)

# ---- T2 · cultural_journal 3:4 结构（A2）----
t2 = _html('cultural_journal', *ARGS_CJ)
_check('T2 img count == 1（R2 单张）', t2.count('<img') == 1)
_check('T2 feTurbulence 纸纹', 'feTurbulence' in t2 and 'baseFrequency=\'0.82\'' in t2)
_check('T2 眉标 Cinzel 14px/0.34em/lh1.0', 'MEMORY OF THE OLD TOWN' in t2
       and bool(re.search(r'font-size:' + _px(14) + r';line-height:1.0;letter-spacing:0.34em', t2)))
_check('T2 中文大标 思源宋 Heavy 68px', 'font-family:&quot;SourceSerifHeavy&quot;' in t2 and 'font-size:68px' in t2)
_check('T2 闭式头部 162（h1_gap 32 + sub_gap 35，R6 构造）', 'margin-top:32px' in t2 and 'margin-top:35px' in t2 and 'height:162px' in t2)
_check('T2 卡纸 10px #FBF6EC + 照片 52/264/796×724（R3/R4）', 'border:10px solid #FBF6EC' in t2 and 'left:52px;top:264px;width:796px;height:724px' in t2)
_check('T2 双层投影', 'box-shadow:0 12px 30px rgba(62,47,38,.30)' in t2)
_check('T2 图注 1 行（R5，Cinzel 11px）', t2.count('Old Town Alley: Twilight Hour') == 1
       and bool(re.search(r'font-size:' + _px(11) + r';letter-spacing:0.15em', t2)))
_check('T2 手绘箭头恰 1 枚（R2）', t2.count('M4 30 C 12 27.5') == 1)
_check('T2 邮戳（cj-rough + 城市 + 国名）', 'cj-rough' in t2 and 'GUZHEN' in t2 and 'CHINA' in t2)
_check('T2 邮戳中行 ★ 2023（覆盖家族思源宋 Heavy）', '★ 2023 ★' in t2 and '&quot;SourceSerifHeavy&quot;,' in t2)
_check('T2 钢印（cj-emboss 双环）', 'cj-emboss' in t2 and 'EMBOSSED' in t2 and 'r="42"' in t2 and 'r="37"' in t2)
# 字体“真应用”而非“仅注入”（§2.6 血泪点：注入在位不等于模板引用了它）
_check('T2 手写注记 LXGWWenKaiReg 真应用于该文本段（§2.4 note_px）',
       bool(re.search(r'font-family:&quot;LXGWWenKaiReg&quot;[^>]*>The smell of aged wood', t2)))
_check('T2 手记中文小字 SourceHanSerifRegular 真应用（§2.4 note_cn_px）',
       bool(re.search(r'font-family:&quot;SourceHanSerifRegular&quot;[^>]*>古镇的雨意与木香', t2)))

# ---- T3 · 五桶结构面（A7 单测面；端到端五桶走 validate_quality 通道，§7.3-4）----
# 画幅→W/H 的判定在 render() 的 _canvas_for（依赖照片比例）；模板只吃 W/H/fs
# （§2.2 刚性块 s=min(W/900,H/1200)+ox/oy）⇒ 直接以各桶 W/H 调模板即为真五桶。
_BUCKETS = {'3:4': (900, 1200), '4:3': (1200, 900), '16:9': (1200, 675), '9:16': (675, 1200), '1:1': (1080, 1080)}
_t3_bad = []
for _g, _args in (('modern_spread', ARGS), ('cultural_journal', ARGS_CJ)):
    _tpl = design_engine._TPL[DESIGN_CONFIGS[_g]['template_id']]
    for _tag, (_w, _h) in _BUCKETS.items():
        _fs = min(_w / 900, _h / 1200)
        _b = _tpl('file:///D:/cover-plan/_t.jpg', DESIGN_CONFIGS[_g], *_args, _w, _h, _fs, _fs, _fs)
        _zero = re.findall(r'(?:left|top|right|bottom|width|height|margin-top|margin-left|font-size):'
                           r'(?:0(?:\.0)?|-\d+(?:\.\d+)?)px', _b)
        _p = re.search(r'left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px;box-sizing:border-box', _b)
        _y = re.search(r'class="cj-yearrow" style="position:absolute;top:(\d+)px;right:(\d+)px', _b)
        _oob = (not _p) or (int(_p.group(1)) + int(_p.group(3)) > _w) \
            or (int(_p.group(2)) + int(_p.group(4)) > _h) \
            or bool(_y and (int(_y.group(1)) >= _h or int(_y.group(2)) >= _w))
        if _zero or _oob:
            _t3_bad.append(f'{_g}@{_tag}' + (f' zero={_zero[:2]}' if _zero else '') + (' oob' if _oob else ''))
_check('T3 五桶 × 2 款：无 0/负尺寸 · 照片框与年份行右锚均在画布内', not _t3_bad, '; '.join(_t3_bad))
_m34 = re.search(r'html,body\{width:(\d+)px;height:(\d+)px', t1)
_check('T3 render() 3:4 画布 900×1200', bool(_m34) and _m34.group(1) == '900' and _m34.group(2) == '1200')

# ---- T4 · 计数链（A3/A4 自动化面）----
import topology_registry as tr
import engine_v2 as ev
_check('T4 _TPL 19 键', len(design_engine._TPL) == 19, len(design_engine._TPL))
_check('T4 DESIGN_IDS 19', len(DESIGN_IDS := list(DESIGN_CONFIGS)) == 19)
_check('T4 KNOWN_GENRES 60', len(tr.KNOWN_GENRES) == 60, len(tr.KNOWN_GENRES))
_check('T4 GENRE_LAYOUT_SIGNATURE 60', len(tr.GENRE_LAYOUT_SIGNATURE) == 60)
_check('T4 两键在 DESIGN_CONFIGS', 'modern_spread' in DESIGN_CONFIGS and 'cultural_journal' in DESIGN_CONFIGS)
_check('T4 zenith_center 含两款', all(g in tr.TOPOLOGY_REGISTRY['zenith_center']['primary_genres']
                                     for g in ('modern_spread', 'cultural_journal')))
_check('T4 两款护脸（A10）', not DESIGN_CONFIGS['modern_spread']['text_on_photo']
       and not DESIGN_CONFIGS['cultural_journal']['text_on_photo'])
_check('T4 不变项 MATTING 13 / METAPHOR 7 / BLUEPRINT 6 / 别名 2 / 拓扑 9',
       len(ev.MATTING_IDS) == 13 and len(ev.METAPHOR_IDS) == 7 and len(ev.BLUEPRINT_IDS) == 6
       and len(ev.MATTING_ALIAS) == 2 and len(tr.TOPOLOGY_REGISTRY) == 9,
       f'{len(ev.MATTING_IDS)}/{len(ev.METAPHOR_IDS)}/{len(ev.BLUEPRINT_IDS)}'
       f'/{len(ev.MATTING_ALIAS)}/{len(tr.TOPOLOGY_REGISTRY)}')
_check('T4 --genre choices = 60（13+13+2+7+6+19）',
       len(list(ev.GENRE) + list(ev.MATTING_IDS) + list(ev.MATTING_ALIAS)
           + list(ev.METAPHOR_IDS) + list(ev.BLUEPRINT_IDS) + list(ev.DESIGN_IDS)) == 60)

# ---- T5 · 字体生效 C-1/C-2/C-3（A5）----
import design_engine as de
_NEW_CONSTS = [('Prata', de._PRATA_CSS), ('SourceHanSansBold', de._SS_BOLD_CSS),
               ('SourceHanSansRegular', de._SS_REG_CSS), ('SourceHanSerifRegular', de._SS_SERIF_REG_CSS),
               ('LXGWWenKaiReg', de._LXGW_REG_CSS)]
for fam, css in _NEW_CONSTS:
    m = re.search(r'src:url\("file:///([^"]+)"\)', css)
    _check(f'T5/C-1 {fam} 路径存在', m and os.path.exists(m.group(1)), m.group(1) if m else 'no-src')
_MS_FAMS = ['SourceHanSansHeavy', 'Prata', 'SourceHanSansBold', 'SourceHanSansRegular']
_CJ_FAMS = ['SourceSerifHeavy', 'CinzelBold', 'SourceHanSerifMedium', 'SourceHanSerifRegular', 'LXGWWenKaiReg']
_check('T5/C-2 modern_spread 4 family @font-face 全在位',
       all(f'@font-face {{ font-family:"{fam}";' in t1 for fam in _MS_FAMS))
_check('T5/C-2 cultural_journal 5 family @font-face 全在位',
       all(f'@font-face {{ font-family:"{fam}";' in t2 for fam in _CJ_FAMS))
_check('T5/C-2 v2 钉死路径（SiYuanHeiTi-Regular/SourceHanSansSC-Regular-2.otf）',
       'SiYuanHeiTi-Regular/SourceHanSansSC-Regular-2.otf' in t1)
# C-3 槽位覆盖（§2.5 全部文本槽位；font_guard.font_covers 同 cmap 口径）
_FAM_FILE = dict(font_guard.FONT_FILES)
_FAM_FILE.update({
    'Prata': 'D:/dsh/fonts/精选西文大刊与特色开源/Prata-Regular.ttf',
    'SourceHanSansBold': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源黑体/思源黑体-简体中文/SourceHanSansCN-Bold.otf',
    'SourceHanSansRegular': 'D:/dsh/fonts/SiYuanHeiTi-Regular/SourceHanSansSC-Regular-2.otf',
    'SourceHanSerifMedium': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源宋体/思源宋体-简体中文/SourceHanSerifCN-Medium.otf',
    'SourceHanSerifRegular': 'D:/dsh/fonts/SiYuanSongTiRegular/SourceHanSerifCN-Regular-1.otf',
    'LXGWWenKaiReg': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Regular.ttf',
    'CinzelBold': 'D:/dsh/fonts/精选西文大刊与特色开源/Cinzel-Bold.ttf',
})
_SLOTS = [
    # modern_spread（§2.5 表）
    ('古镇长巷', _FAM_FILE['SourceHanSansHeavy']), ('OLD TOWN ALLEY', _FAM_FILE['Prata']),
    ('2026.09.15', _FAM_FILE['SourceHanSansBold']), ('SUZHOU', _FAM_FILE['SourceHanSansBold']),
    ('JOURNEYS INTO HERITAGE', _FAM_FILE['SourceHanSansBold']),
    ('ISSUED 2026', _FAM_FILE['SourceHanSansBold']),
    ('[FEATURE] THE SOUL OF WATER TOWNS', _FAM_FILE['SourceHanSansHeavy']),
    ("EXPLORING JIANGNAN'S HIDDEN ALLEYWAYS", _FAM_FILE['SourceHanSansRegular']),
    ('A JOURNEY THROUGH ANCIENT PAVEMENTS, RIVERS AND LANTERN-LIT NIGHTS', _FAM_FILE['SourceHanSansRegular']),
    # cultural_journal（§2.5 表；★ 改覆盖家族 SourceSerifHeavy）
    ('古镇漫步', _FAM_FILE['SourceSerifHeavy']), ('纪录片系列 · DOCUMENTARY SERIES', _FAM_FILE['SourceHanSerifMedium']),
    ('MEMORY OF THE OLD TOWN', _FAM_FILE['CinzelBold']), ('Old Town Alley: Twilight Hour', _FAM_FILE['CinzelBold']),
    ('The smell of aged wood & rain.', _FAM_FILE['LXGWWenKaiReg']),
    ('古镇的雨意与木香', _FAM_FILE['SourceHanSerifRegular']),
    ('OCT 2023', _FAM_FILE['CinzelBold']), ('GUZHEN', _FAM_FILE['CinzelBold']),
    ('★ 2023 ★', _FAM_FILE['SourceSerifHeavy']), ('CHINA', _FAM_FILE['CinzelBold']),
    ('EMBOSSED', _FAM_FILE['CinzelBold']), ('ARCHIVE', _FAM_FILE['CinzelBold']),
]
for txt, fpath in _SLOTS:
    _check(f'T5/C-3 零缺字 {txt[:14]}', font_guard.font_covers(fpath, txt))

# ---- T8 · 超长中文标题 fit（D-8/T8；§7.1 T8 的锚 = 标题块高 130 的 modern_spread）----
long_t = '古镇漫步' * 10
t8 = _html('modern_spread', long_t, *ARGS[1:])
m8 = re.search(r'font-size:(\d+(?:\.\d+)?)px;line-height:1.0;letter-spacing:0.10em;color:#191B1D', t8)
_check('T8 超长标题 fit 缩档（< 48px）且标题块高 130 在位',
       bool(m8) and float(m8.group(1)) < 48 and 'height:130px' in t8,
       m8.group(1) if m8 else 'no-match')
t8c = _html('cultural_journal', long_t, *ARGS_CJ[1:])
_check('T8c（②裁定后：cj 大标走 fit）超长标题缩档（< 68）且容器 overflow:hidden 兜底在位',
       _cj_h1_fs(t8c) is not None and _cj_h1_fs(t8c) < 68
       and 'height:162px;text-align:center;overflow:hidden' in t8c, _cj_h1_fs(t8c))

# ---- T9 · 全空参数（D-3/T9）----
t9 = _html('modern_spread', *ARGS_EMPTY)
_check('T9 无 None 字样', 'None' not in t9)
_check('T9 元数据条左右落 —', '>—<' in t9)
_check('T9 ISSUED 不渲（D 无年份）', 'ISSUED' not in t9)
t9c = _html('cultural_journal', *ARGS_EMPTY)
_check('T9c 年份行不渲（D 无月份/年份）', 'cj-yearrow' not in t9c)
_check('T9c 副标/城市落固定兜底', '纪录片系列' in t9c and 'GUZHEN' in t9c)

# ---- T10 · 非日期 D（D-3/T10）----
t10 = _html('modern_spread', '古镇长巷', 'OLD TOWN ALLEY', '今天', 'SUZHOU')
_check('T10 无年份 D → ISSUED 不渲', 'ISSUED' not in t10)
t10c = _html('cultural_journal', '古镇漫步', '纪录片系列', '今天', 'GUZHEN')
_check('T10c 邮戳中行不渲（无年份）', '★' not in t10c)
_check('T10c 年份行不渲', 'cj-yearrow' not in t10c)

# ---- T11 · 超长 L（D-13/T11）----
long_l = 'SUZHOU · JIANGSU · CHINA · 120.722°E · LONG LONG LOCATION NAME' * 3
t11 = _html('modern_spread', *ARGS[:3], long_l)
_check('T11 元数据条 ellipsis 兜底', 'text-overflow:ellipsis' in t11)
_check('T11 页脚第 2 行 nowrap', 'white-space:nowrap' in t11)

# ---- T12 · 缺字标题（兜底宋有该字，§1.6）----
t12 = _html('modern_spread', '古镇长巷鿑', 'OLD TOWN ALLEY', '2026.09.15', 'SUZHOU')
_check('T12 font-fallback 注释 + 兜底 @font-face', 'font-fallback: 鿑' in t12 and 'font-family:"思源宋体"' in t12)

# ---- T13 · 缺字标题（兜底宋也缺，预期 uncoverable）----
t13 = _html('modern_spread', '古镇长巷𠮷', 'OLD TOWN ALLEY', '2026.09.15', 'SUZHOU')
_check('T13 font-uncoverable 注释', 'font-uncoverable: 𠮷' in t13)

# ---- T14 · 照片缺失回退 3:4（回归）----
t14 = render('D:/cover-plan/_no_such_photo_xyz.jpg', DESIGN_CONFIGS['modern_spread'], *ARGS)
m14 = re.search(r'html,body\{width:(\d+)px;height:(\d+)px', t14)
_check('T14 缺照片回退 3:4 且不抛异常', bool(m14) and m14.group(1) == '900')

# ---- T15（A8）· 同参双渲确定性（torn_journal 代表款；全款 HEAD 基线由收口 A/B 通道核对）----
h1 = _html('torn_journal', *ARGS)
h2 = _html('torn_journal', *ARGS)
_check('T15 同参渲染确定性（sha 相等）', h1 == h2)

# ---- T17 · 年份标记结构面（A11）----
m17 = re.search(r'<svg class="cj-yearmark"[^>]*>', t2)
_check('T17 svg.cj-yearmark 在位', bool(m17))
if m17:
    tag = m17.group(0)
    _check('T17 viewBox 0 0 24 12', 'viewBox="0 0 24 12"' in tag)
    _check('T17 preserveAspectRatio none', 'preserveAspectRatio="none"' in tag)
    _check('T17 width/height = _sv(24)/_sv(12) = 24/12', 'width="24"' in tag and 'height="12"' in tag)
_segs = re.findall(r'<polygon points="([^"]+)" fill="([^"]+)"/>', t2)
_check('T17 polygon 恰 2 枚', len(_segs) == 2, len(_segs))
_check('T17 points 取 §2.4.1 值', _segs and _segs[0][0] == '0,0 11,6 0,12' and _segs[1][0] == '13,0 24,6 13,12')
_check('T17 fill = palette.point', _segs and _segs[0][1] == '#A85A3C' and _segs[1][1] == '#A85A3C')
_m17 = re.search(r'<svg class="cj-yearmark".*?</svg>', t2, re.S)
_inner17 = re.sub(r'<[^>]*>', '', _m17.group(0)) if _m17 else None
_check('T17 标记节点无文本（textContent==\'\'）',
       _inner17 is not None and _inner17.strip() == '', repr(_inner17))
_check('T17 产物 U+25B8 计数 0（全产物）', chr(0x25B8) not in t2)
_check('T17 产物 U+00BB 计数 0', chr(0xBB) not in t2)

# ---- T18/T19 · cj 中文大标 fit 缩档（§2.4 表后 fit 注 / v3 裁定 ② = 自动缩字号不丢字；A12）----
# 取值断言面：4 字不缩（= 基准 68）/ 12 字缩档（= fit_title_fs 复算值，且 < 68）。
_H1_W, _H1_BASE, _H1_LS = 796, 68, '0.10em'      # h1_fit_w / hero_px / hero_letter
_cj_lay = DESIGN_CONFIGS['cultural_journal']
_check('T18/A12 配置契约：cj layout.h1_fit_w = 796（版心宽 900−2×52）、scale.hero_px = 68',
       _cj_lay['layout']['h1_fit_w'] == _H1_W and _cj_lay['scale']['hero_px'] == _H1_BASE,
       f'{_cj_lay["layout"].get("h1_fit_w")}/{_cj_lay["scale"].get("hero_px")}')
_fit4 = fit_title_fs('古镇漫步', _H1_W, _H1_BASE, _H1_LS)
_fit12 = fit_title_fs('古镇漫步' * 3, _H1_W, _H1_BASE, _H1_LS)
t18 = _html('cultural_journal', '古镇漫步', *ARGS_CJ[1:])
t19 = _html('cultural_journal', '古镇漫步' * 3, *ARGS_CJ[1:])
_check('T18 4 字不缩档：font-size = 基准 68 = fit 复算值',
       _cj_h1_fs(t18) == 68 == _fit4, f'{_cj_h1_fs(t18)}/{_fit4}')
_check('T19 12 字缩档：font-size = fit 复算值 = 60 且 < 68',
       _cj_h1_fs(t19) == _fit12 == 60, f'{_cj_h1_fs(t19)}/{_fit12}')
_check('T19 头部容器无裁切（构造面）：容器高 162 ≥ 闭式内容高 14+32+fs+35+13',
       bool(re.search(r'height:162px;text-align:center;overflow:hidden', t19))
       and (_cj_h1_fs(t19) or 0) + 94 <= 162)

# T19 的 DOM 量测面（Range 墨迹宽 / 头部容器 sh·ch）走设计 §7.3 前置① chrome 通道；
# 产物落 %TEMP%（仓内零写入）；chrome 缺失 → 打印 SKIP 行（环境面，不判红）。
_CHROME = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
_CJ_MEASURE_JS = '''<script>
(function(){
  function mark(o){var d=document.createElement('div');d.id='CJFIT';
    d.textContent='CJFIT::'+JSON.stringify(o);document.body.appendChild(d);}
  document.fonts.ready.then(function(){ setTimeout(function(){
    var c=null, ds=document.querySelectorAll('div');
    for(var i=0;i<ds.length;i++){
      if((ds[i].getAttribute('style')||'').indexOf('height:162px;text-align:center')>=0){c=ds[i];break;}
    }
    if(!c){ mark({err:'no-head'}); return; }
    var h1=null;
    for(var k=0;k<c.children.length;k++){
      if((c.children[k].textContent||'').trim()==='__T__'){h1=c.children[k];break;}
    }
    if(!h1){ mark({err:'no-h1'}); return; }
    var r=document.createRange(); r.selectNodeContents(h1);
    var rr=r.getBoundingClientRect();
    mark({fs:getComputedStyle(h1).fontSize, inkW:Math.round(rr.width*100)/100,
          sh:c.scrollHeight, ch:c.clientHeight});
  },400); });
})();
</script>'''


def _chrome_dom_fit(html, title, tag):
    """chrome dump-dom 量测：h1 计算字号 / Range 墨迹宽 / 头部容器 scrollHeight·clientHeight。

    降级边界（advisor 🔵#5 落地）：**仅"chrome 二进制缺失"返回 None**（环境面 → 调用方 SKIP）；
    chrome 在但运行失败 / 未产出标记 → 返回带 `err` 的 dict ⇒ 调用方断言取不到 `fs` 即 **FAIL**
    （不再把"跑挂了"静默降级成 SKIP）。"""
    import json as _json
    import subprocess as _sp
    import tempfile as _tf
    if not os.path.exists(_CHROME):
        return None
    path = os.path.join(_tf.gettempdir(), f'cp_cjfit_{tag}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html.replace('</body>', _CJ_MEASURE_JS.replace('__T__', title) + '</body>')
                if '</body>' in html else html + _CJ_MEASURE_JS.replace('__T__', title))
    dom, err = '', ''
    try:
        r = _sp.run([_CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                     '--allow-file-access-from-files', '--window-size=900,1200',
                     '--virtual-time-budget=6000', '--dump-dom',
                     'file:///' + path.replace('\\', '/')], capture_output=True, timeout=60)
        dom = r.stdout.decode('utf-8', 'replace')
        if r.returncode != 0:
            err = f'chrome rc={r.returncode} {r.stderr.decode("utf-8", "replace")[-160:]}'
    except Exception as e:                       # noqa: BLE001 —— 通道异常一律显式上报
        err = f'chrome ex={e}'
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    m = re.search(r'CJFIT::(\{[^<]*\})', dom, re.S)
    if err or not m:
        return {'err': err or 'chrome/dump 未产出 CJFIT 标记（量测脚本未跑完？）'}
    try:
        return _json.loads(m.group(1))
    except ValueError as e:
        return {'err': f'CJFIT JSON 解析失败: {e}'}


_d18 = _chrome_dom_fit(t18, '古镇漫步', 't18')
_d19 = _chrome_dom_fit(t19, '古镇漫步' * 3, 't19')
if _d18 is None or _d19 is None:
    print(f'SKIP T18/T19-DOM: chrome 二进制缺失（{_CHROME}）——取值/构造断言面已覆盖')
else:
    _check('T18-DOM 4 字实测 font-size=68px 且墨迹宽 ≤ 796',
           _d18.get('fs') == '68px' and _d18.get('inkW', 1e9) <= 796, _d18)
    _check('T19-DOM 12 字实测 font-size=60px、墨迹宽 ≤ 796（Range）',
           _d19.get('fs') == '60px' and _d19.get('inkW', 1e9) <= 796, _d19)
    _check('T19-DOM 头部容器无裁切（scrollHeight ≤ clientHeight + 3）',
           _d19.get('sh', 1e9) <= _d19.get('ch', 0) + 3, _d19)

# ---- T20 · --fg-texts 固定装饰文案覆盖（死词参数化 b 方案；①注入 ②缺省两态）----
# ① CLI 端到端（subprocess 真跑 engine_v2 --fg-texts：解析 + 消费款判空 + cfg 合并全覆盖）：
#   产物落 %TEMP%（仓内零写入），两款各渲一次——rc=0 且新词在、旧词不在；
# ② 进程内先注入再渲缺省——若覆盖污染共享 DESIGN_CONFIGS（浅拷贝坑）默认词即丢，此处抓到。
_T20_ENG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine_v2.py')
_t20_out = {'ep': os.path.join(tempfile.gettempdir(), 'cp_fgt_exhibition.html'),
            'td': os.path.join(tempfile.gettempdir(), 'cp_fgt_deckle.html')}
_t20_rc = []
for _tag, _g, _fg in (('ep', 'exhibition_poster', 'right_name=见山;f_title=冬之衣·混凝土展'),
                      ('td', 'torn_deckle', 'note=新词 · 冬夜的站台。')):
    try:
        _r = subprocess.run([sys.executable, _T20_ENG, '--photo', PHOTO, '--genre', _g,
                        '--title', '冬之衣', '--sub', 'test', '--date', '2026.01.18',
                        '--location', '街角展厅', '--fg-texts', _fg, '--out', _t20_out[_tag]],
                       capture_output=True, timeout=120)
        _t20_rc.append(_r.returncode)
    except Exception as e:                       # noqa: BLE001 —— 通道异常显式判红（不静默 SKIP）
        _t20_rc.append(f'ex={e}')


def _t20_read(tag):
    try:
        with open(_t20_out[tag], encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ''


_t20i_ep, _t20i_td = _t20_read('ep'), _t20_read('td')
for _p in _t20_out.values():
    try:
        os.remove(_p)
    except OSError:
        pass
_check('T20① CLI --fg-texts 端到端两款各渲一次：rc=0 且新词在、旧词不在',
       _t20_rc == [0, 0]
       and '见山' in _t20i_ep and '冬之衣·混凝土展' in _t20i_ep
       and '鉄男' not in _t20i_ep and '安藤忠雄建築展' not in _t20i_ep
       and '新词 · 冬夜的站台。' in _t20i_td and '月台的燈，亮到很晚。' not in _t20i_td,
       f'rc={_t20_rc} ep_len={len(_t20i_ep)} td_len={len(_t20i_td)}')
# ② 进程内注入渲染后再渲缺省：共享 config 若被污染，下面断言立即判红
_html('exhibition_poster', *ARGS, fg_fixed={'right_name': '见山'})
_html('torn_deckle', *ARGS, fg_fixed={'note': '新词 · 冬夜的站台。'})
t20d_ep = _html('exhibition_poster', *ARGS)
t20d_td = _html('torn_deckle', *ARGS)
_check('T20② 不注入时 fixed 默认词保留（鉄男/安藤忠雄建築展 · 月台的燈；兼防共享污染）',
       '鉄男' in t20d_ep and '安藤忠雄建築展' in t20d_ep
       and '月台的燈，亮到很晚。' in t20d_td)

# ---- T21 · 审查修复守卫（2026-09-25 bc4282c 复审轮）----
# ① zen 无副标印章几何：竖排 title 物理下界 = 容器 top + 字数×字号（CJK 1em/字 + 字距）；
#    旧公式按 hero_lh 0.95 估高 → ≥2 字时印章 top 低于字栏真实底 → 压字尾（F4）。
_t21_out = os.path.join(tempfile.gettempdir(), 'cp_zenseal.html')
if os.path.exists(_t21_out):
    os.remove(_t21_out)
try:
    _r21 = subprocess.run([sys.executable, _T20_ENG, '--photo', PHOTO, '--genre', 'zen',
                           '--title', '云上练习曲', '--sub', '', '--date', '2026.11.03',
                           '--location', '林间', '--out', _t21_out],
                          capture_output=True, text=True, encoding='utf-8', errors='replace',
                          timeout=120)
    _t21h = open(_t21_out, encoding='utf-8').read() if os.path.exists(_t21_out) else ''
except Exception as _ex21:
    _r21, _t21h = None, f'ex={_ex21}'
_check('T21①a zen 无副标 CLI 渲染 rc=0 且产物在',
       _r21 is not None and _r21.returncode == 0 and bool(_t21h))
_mtop21 = re.search(r'position:absolute;top:(\d+)px;(?:left|right):\d+px;z-index:20;display:flex', _t21h)
_mfs21 = re.search(r'font-size:(\d+)px;line-height:0\.95;letter-spacing:0\.18em;writing-mode:vertical-rl', _t21h)
_msl21 = re.search(r'top:(\d+)px;(?:left|right):\d+px;z-index:20;width:\d+px;height:\d+px;'
                   r'background:[^;]+;transform:rotate\(-2deg\)', _t21h)
if _mtop21 and _mfs21 and _msl21:
    _floor21 = int(_mtop21.group(1)) + 5 * int(_mfs21.group(1))   # 5 字物理下界（1em/字）
    _check('T21①b 无副标印章 top ≥ 字栏物理下界（容器top + 5字×字号）',
           int(_msl21.group(1)) >= _floor21, f"seal={_msl21.group(1)} floor={_floor21}")
else:
    _check('T21①b zen 结构三要素可解析（容器/字栏/印章）', False,
           f"top={bool(_mtop21)} fs={bool(_mfs21)} seal={bool(_msl21)}")
if os.path.exists(_t21_out):
    os.remove(_t21_out)
# ② super_index 目录行：四栏编号全角冒号 + 字号整行统一（F5/F6）
_t21si = _html('super_index', *ARGS)
_check('T21②a 目录四栏编号带全角冒号（01：…04：）',
       all(f'{i:02d}：' in _t21si for i in range(1, 5)))
_check('T21②b 目录四栏字号整行统一（nowrap 槽位单值）',
       len(set(re.findall(r'font-size:(\d+)px;white-space:nowrap', _t21si))) == 1)
# ③ 裁定位锁（装饰 1/3 裁定 + 胶带贴角；配置字面量回归锁）
_check('T21③a torn_deckle 胶带贴角 tape1=(818,44,-6)',
       DESIGN_CONFIGS['torn_deckle']['layout']['tape1'] == (818, 44, -6))
_bub21 = DESIGN_CONFIGS['torn_journal']['layout']['doodles']['bubble']
_check('T21③b torn_journal 云朵左下跨角 (top=973, left=0)',
       _bub21['top'] == 973 and _bub21['left'] == 0)
_check('T21③c torn_journal photo_phrase 右缘 stage (right=10)',
       DESIGN_CONFIGS['torn_journal']['layout']['photo_phrase_right'] == 10)

# ---- T22 · 方案A 字体内嵌（2026-09-25 用户拍板 --embed-fonts）----
_t22_out = os.path.join(tempfile.gettempdir(), 'cp_embed.html')
if os.path.exists(_t22_out):
    os.remove(_t22_out)
try:
    _r22 = subprocess.run([sys.executable, _T20_ENG, '--photo', PHOTO, '--genre', 'torn_journal',
                           '--title', '云上练习曲', '--sub', '左手和弦', '--date', '2026.11.03',
                           '--location', '林间', '--out', _t22_out,
                           '--embed-fonts', '--embed-photo'],
                          capture_output=True, text=True, encoding='utf-8', errors='replace',
                          timeout=300)
    _t22h = open(_t22_out, encoding='utf-8').read() if os.path.exists(_t22_out) else ''
except Exception as _ex22:
    _r22, _t22h = None, f'ex={_ex22}'
_check('T22① --embed-fonts 渲染 rc=0 且产物在',
       _r22 is not None and _r22.returncode == 0 and bool(_t22h))
_t22_faces = re.findall(r'@font-face\s*\{[^}]*\}', _t22h)
_t22_ff = [x for x in _t22_faces if 'file:///' in x]
_check('T22② @font-face 全转 data:font/woff2（字体段 file:// 清零）',
       'data:font/woff2;base64,' in _t22h and not _t22_ff,
       f"data={_t22h.count('data:font/woff2')} ff_with_file={len(_t22_ff)}")
_check('T22③ --embed-photo img file:// 清零（data:image/ 就位）',
       'src="data:image/' in _t22h and not re.search(r'src="file:///', _t22h),
       f"data_img={_t22h.count('src=\x22data:image/')}")
if os.path.exists(_t22_out):
    os.remove(_t22_out)

# ---- 汇总 ----
print(f'PASS {len(_ok)}  FAIL {len(_fail)}')
for f in _fail:
    print('  FAIL:', f)
sys.exit(1 if _fail else 0)
