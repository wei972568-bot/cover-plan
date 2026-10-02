#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
font_guard · 缺字预检共享模块（2026-09-05，设计稿 docs/批量设计-真删除与字体驱动款-设计.md §2.2）
================================================================================================
立项动因：书法字体（演示秋鸿楷等）存在缺字，浏览器静默回退到系统宋体——视觉气质断裂且用户不知情。
本模块用 fontTools 读字体 cmap 做**渲染前**逐字覆盖检查，供两处接入：
  · 引擎内（matting_engine）：title/sub 落区字符对款字体逐字查，缺字字符包
    `<span style="font-family:'思源宋体'...">` 兜底（HTML 机制，matting 三模板落区皆 HTML div），
    替换记录写进 html 注释 `<!-- font-fallback: ... -->` 供质检器解析。
  · 质检器（validate_quality.py）：解析上述注释，输出 [font-coverage] 行（**只提示不计 ✗**）。

设计要点（§2.2 v2.1 评审修正 + v2.2 整段评估修正 2026-09-05）：
  · **整段评估优先**：主字体对整段覆盖率 <50%（全缺/大半缺）→ 整段直接用兜底字体渲（不逐字包
    span——逐字包会毁字距/连字，par_avion_marcellus 配中文标题时曾翻车）；≥50%（零星缺字）
    才逐字 span。整段切换同样记 [font-coverage]（质检器解析 segment-fallback 标记）。
  · **兜底字体自身也校验**：思源宋体同样过 cmap 检查；兜底仍缺字 → `coverage` 升格为
    `uncoverable`（渲染必缺字形，质检 ✗，绝不静默）。
  · **作用域**：引擎侧只对 title_font ∈ FONT_GUARD_WHITELIST 的款启用（保删除批
    1.6#4 字节零回归硬门槛；其余款不查不注）。
  · 缓存 per (字体路径, 文本)；fontTools lazy 打开，首次查询后整表缓存。

依赖：fonttools（pip install fonttools；2026-09-05 实装版本 **4.53.1**，纯 Python）。
"""
import os

# 兜底字体：思源宋体（覆盖最全的常用/生僻 CJK；气质同衬线系，与 _serif_cn 家族一致）。
# 渲染时由 matting_engine 确认 @font-face 已注册（FONTS_CSS 的 SourceSerifHeavy 同款文件族）。
FALLBACK_FONT_FAMILY = '思源宋体'
_FALLBACK_FONT_FILE = 'D:/dsh/fonts/SiYuanSongTiRegular/SourceHanSerifCN-Regular-1.otf'

# 引擎侧预检白名单（title_font family 名）：仅这些字体触发兜底逻辑（§2.2 v2.1 作用域修正）。
# 2026-09-06 +SourceHanSansHeavy：设计语言族思源黑 Heavy 主标款
# （pop_halftone/super_index/retro_tv，docs/批量设计-新设计语言六款-设计.md §2/§4-5）。
# 2026-09-07 +ZhuoKaiKai：彩活四款楷体选型（street_zine/doodle_summer 主标，
# docs/批量设计-彩活四款-设计.md §2）——选型依据：楷体候选 cmap 覆盖探针实测
# （font_covers 同口径，实测记录见 docs/交接摘要.md 2026-09-07 批交付段）：
# 清松手写体1 / 霞鹜文楷对繁体装饰字（本週注目★街頭速報/看這裡/綠野晚風逃跑計畫）
# 覆盖最全（仅缺罕见码位），拙楷/寒蝉/马善政缺 7 繁体字；**真字重文件**
# 优先于 KaiTi 系统字（引擎无楷体真字重链；§2 规范"黑体一律真字重文件"延伸到楷体，
# 防浏览器静默回退）。缺字（如鿑）走思源宋兜底 + 注释（接入点 A 先例）。
FONT_GUARD_WHITELIST = {'ZhuoKai', 'XingKai', 'Marcellus', 'YesevaOne', 'SourceHanSansHeavy',
                        'ZhuoKaiKai'}

# 字体文件路径表（family 名 → 盘上实名；2026-09-05 ls 实证）
FONT_FILES = {
    'Marcellus': 'D:/dsh/fonts/精选西文大刊与特色开源/Marcellus-Regular.ttf',
    'YesevaOne': 'D:/dsh/fonts/精选西文大刊与特色开源/YesevaOne-Regular.ttf',
    'ZhuoKai':   'D:/dsh/fonts/免费商用书法字体/江西拙楷2.0.ttf',
    'XingKai':   'D:/dsh/fonts/免费商用书法字体/三极行楷简体-粗.ttf',
    # 设计语言族（2026-09-06）：思源黑 Heavy（静态真字重文件，§2 字体规范）
    'SourceHanSansHeavy': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/思源系列/思源黑体/思源黑体-简体中文/SourceHanSansCN-Heavy.otf',
    # 彩活四款（2026-09-07）：楷体真字重文件（street_zine/doodle_summer 主标+固定繁体文案；
    # 选型探针实测——font_covers 同口径，记录见 docs/交接摘要.md 2026-09-07 批交付段）
    'ZhuoKaiKai': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/清松手写体1.ttf',
    # 构图三款（2026-09-08）：fg_texts 按文案自身 font 预检（docs/批量设计-构图三款-设计.md
    # §0.5 覆盖口径）所需的 family 名——霞鹜文楷（pop 二款对话/底部楷体句）、
    # 思源宋 Heavy（branch 楷格句/竖排小字/pop_press 底部款名）。预检查询只读 cmap
    # （font_covers_family），不建 @font-face（@font-face 由 design_engine 按需注入链负责）
    'LXGWWenKai': 'D:/dsh/fonts/十套高质量免费可商用字体整理/十套高质量免费可商用字体整理/手写体系列/霞鹜文楷/LXGWWenKai-Bold.ttf',
    'SourceSerifHeavy': 'D:/dsh/fonts/SiYuanSongTiRegular/SourceHanSerifCN-Heavy-4.otf',
    FALLBACK_FONT_FAMILY: _FALLBACK_FONT_FILE,
}

try:
    from fontTools.ttLib import TTFont
    _HAS_FONTTOOLS = True
except ImportError:  # fonttools 未安装时降级：返回"不覆盖"比静默放行更诚实
    _HAS_FONTTOOLS = False

# ---- cmap 缓存：字体路径 → set(码点)。lazy 打开，进程内复用 ----
_CODEPOINT_CACHE = {}


def _codepoints(font_path):
    """读取字体 cmap 的码点全集（进程内缓存；读失败返回 None）。"""
    if font_path in _CODEPOINT_CACHE:
        return _CODEPOINT_CACHE[font_path]
    if not _HAS_FONTTOOLS or not os.path.exists(font_path):
        _CODEPOINT_CACHE[font_path] = None
        return None
    try:
        f = TTFont(font_path, lazy=True, fontNumber=0)
        cps = set(f.getBestCmap().keys())
        f.close()
    except Exception:
        cps = None
    _CODEPOINT_CACHE[font_path] = cps
    return cps


def font_covers(font_path, text):
    """字体 cmap 是否覆盖 text 逐字。

    返回 (ok: bool, missing: list[str])：
      ok        —— text 全部字符都在 cmap 内
      missing   —— 缺字字符列表（按 text 出现顺序去重）
    font_path 不存在 / fontTools 缺失 / 解析失败 → (False, [全部字符])（宁可误报不静默放行）。
    """
    cps = _codepoints(font_path)
    if cps is None:
        return False, list(dict.fromkeys(text))
    missing = [c for c in dict.fromkeys(text) if ord(c) not in cps]
    return not missing, missing


def font_covers_family(font_family, text):
    """按引擎内部 family 名（FONT_FILES 键）查覆盖；未知 family → (True, []) 放行（非预检范围）。"""
    path = FONT_FILES.get(font_family)
    if path is None:
        return True, []
    return font_covers(path, text)


def check_and_wrap(text, font_family):
    """引擎接入点：对 text 按指定字体查覆盖，缺字字符包思源宋兜底 span。

    调用约定（与 matting_engine 一致）：text 为**未转义原文**（评审修正：esc 后文本再逐字
    esc 会双转义——title 含 '&' 时 esc 产物 "&amp;" 的实体字符再过 _html.escape，渲染成
    字面 "&amp;"）；本函数对每个字符单独 _html.escape 后拼接，非兜底字符与兜底字符转义
    口径一致，输出为安全 HTML。引擎侧 fit_title_fs 用 esc 后纯文本估宽（T_fit=esc(title)，
    纯文本与包裹产物可见宽度一致），兜底包裹只在 fit 之后进行（先 fit 后包，
    见 matting_engine.render）。

    返回 dict：
      html     : 兜底后的文本
      missing  : 缺字字符列表（款字体缺）
      fallback_used : bool（是否发生了兜底包裹）
      uncoverable   : list[str]（**思源宋也缺**的字符——升格 ✗ 项）
      comment : 质检器注释串（无兜底时为 ''）：`font-fallback: 欢,迎`
    """
    if not text:
        return {'html': '', 'missing': [], 'fallback_used': False,
                'uncoverable': [], 'comment': ''}

    import html as _html
    ok, missing = font_covers_family(font_family, text)
    if not missing:
        return {'html': _html.escape(text), 'missing': [], 'fallback_used': False,
                'uncoverable': [], 'comment': ''}

    # 兜底字体自身校验（§2.2 v2.1）：思源宋仍缺 → uncoverable 升格
    _fb_ok, _fb_missing = font_covers_family(FALLBACK_FONT_FAMILY, ''.join(missing))
    uncoverable = [] if _fb_ok else _fb_missing

    # v2.2 整段评估：覆盖率 <50% → 整段切兜底（逐字 span 毁字距；全缺/大半缺时排版优先）
    if len(missing) / max(len(dict.fromkeys(text)), 1) >= 0.5:
        fb_style = f"font-family:'{FALLBACK_FONT_FAMILY}','Songti SC',serif;"
        comment = 'font-fallback-segment: ' + ''.join(missing) + f' | coverage {len(dict.fromkeys(text))-len(missing)}/{len(dict.fromkeys(text))}'
        return {'html': f'<span style="{fb_style}">{_html.escape(text)}</span>',
                'missing': missing, 'fallback_used': True,
                'uncoverable': uncoverable, 'comment': comment, 'segment_fallback': True}

    fb_style = f"font-family:'{FALLBACK_FONT_FAMILY}','Songti SC',serif;"
    out, wrapped = [], False
    for c in text:
        if c in missing:
            out.append(f'<span style="{fb_style}">{_html.escape(c)}</span>')
            wrapped = True
        else:
            out.append(_html.escape(c))
    comment = ''
    if wrapped:
        # 注释里只列兜底字符（uncoverable 是兜底失败的子集，质检器按 ✗ 单独升格报告）
        comment = 'font-fallback: ' + ','.join(missing)
    return {'html': ''.join(out), 'missing': missing, 'fallback_used': wrapped,
            'uncoverable': uncoverable, 'comment': comment}


def coverage_report(text, font_family):
    """质检器用的覆盖报告（不包裹，只报告）：uncoverable 非空 → 升格 ✗。"""
    _ok, missing = font_covers_family(font_family, text)
    if not missing:
        return {'missing': [], 'uncoverable': [], 'ok': True}
    _fb_ok, _fb_missing = font_covers_family(FALLBACK_FONT_FAMILY, ''.join(missing))
    uncoverable = [] if _fb_ok else _fb_missing
    return {'missing': missing, 'uncoverable': uncoverable,
            'ok': not uncoverable and not missing}


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # 自检：秋鸿楷历史缺字场景 → 思源宋兜底；兜底字体自身覆盖"龘"实证
    r1 = check_and_wrap('秋鸿楷缺字龘测试', 'ZhuoKai')
    print('zhuokai missing:', r1['missing'], 'uncoverable:', r1['uncoverable'],
          'comment:', r1['comment'])
    print('html:', r1['html'])
    r2 = font_covers_family(FALLBACK_FONT_FAMILY, '龘')
    print('fallback covers 龘:', r2)
    r3 = coverage_report('龘', 'ZhuoKai')
    print('coverage_report 龘@zhuokai:', r3)
    assert not r2[1], '思源宋兜底字体必须覆盖 龘（回归用例前提）'
    assert r1['missing'] == ['龘'] and r1['uncoverable'] == [], '拙楷缺龘→思源宋兜住'
    assert r1['comment'] == 'font-fallback: 龘'
    print('font_guard OK')
