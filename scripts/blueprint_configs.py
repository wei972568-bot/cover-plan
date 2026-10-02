#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝图 28 套补齐 · 文字压照片流派族（blueprint canonical）· 参数化 configs（6 款，2026-09-05 -piercing -horizon）
============================================================================
补 PROJECT_BLUEPRINT.md §4 蓝图 28 概念中引擎尚不能渲染的 8 套（原只有名字/拓扑、
GENRE_LAYOUT_SIGNATURE=None、engine_v2 无分支）——**2026-09-02 时点口径**，补齐后蓝图 28 概念全部落地；
2026-09-05 真删 piercing/horizon 两款（现役 6 款，见上）。

独立流派族（如同 matting / metaphor），不合并 engine_v2 旧 14 套命名，不改其逻辑。

每款 config 字段（供 blueprint_engine.render 使用；结构对齐 matting_engine 的"传 config"约定，
而内部形态沿用 engine_v2 GENRE 的 fonts/scale/palette/layout 结构——因为本族是"文字压照片"版式）：
  mode          : 'B'（蓝图文字压照片家族标记；**非分发键**——分发按 template_id）
  template_id   : 构建函数名（_tpl_light_leak / _tpl_deep_interlock / _tpl_draping /
                  _tpl_silhouette / _tpl_bedrock_stele / _tpl_midnight）
  topology      : 绑定拓扑槽位（metadata；权威注册在 topology_registry.py）
  hero_zone     : 主标真实落区枚举（供 validate_layout_consistency 计算）
  text_on_photo : bool —— hero 文字是否压在照片上。本 6 款均为 True（文字压照片，**非护脸**）。
  fonts         : {'hero': 主标字体, 'emotion': 副标/正文字体, 'data': 等宽数据字体}
  scale         : {'hero_px','lead_px','micro_px','hero_lh','hero_letter','hero_shadow'}
  palette       : {'primary': 基底/暗部色, 'accent': 主强调色, 'point': 点睛色}
  layout        : 每款专属结构参数（漏光方向/色带高度/阶梯块/底标偏移等）
  tone_filter   :（可选）照片 CSS filter（'' 无；如 saturate(1.1) contrast(1.05)）

title / sub / date / location 一律由 CLI 参数传入，**不硬编码文案**；仅"物/结构"标签
（如日期戳、LOT 号等）由参数派生（确定性 seed，见 blueprint_engine._derive）。

6 款均 text_on_photo==True（文字压照片），beh "护脸" 由 topology_registry.text_on_photo 排除，
故本族**不进入 face_safe_genres**（无需 _METAPHOR_NON_FACE_SAFE 式显式排除）。

简化声明（设计 §5 拆两档）：
  - 完整气质 4 款：light_leak / draping / bedrock_stele / midnight。（2026-09-05 -horizon）
  - 简化气质 2 款：deep_interlock / silhouette（2026-09-05 -piercing） —— 首版大字版式 + 简化咬合/环绕
    （叠字/色带/阶梯块顺边缘），**不含真正的发丝 3D 咬合/顺轮廓抠像**（那是另案，需轮廓识别）。
"""

# ---- 共享默认（保证字段全集；每款按气质覆盖）----
_DEFAULT = {
    'mode': 'B',
    'template_id': '',
    'topology': '',
    'hero_zone': '',
    'text_on_photo': True,
    'fonts': {'hero': 'SourceSerifHeavy', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
    'scale': {'hero_px': 110, 'lead_px': 34, 'micro_px': 10,
              'hero_lh': 0.95, 'hero_letter': '0.12em', 'hero_shadow': '0 4px 20px rgba(0,0,0,.5)'},
    'palette': {'primary': '#0d0d0e', 'accent': '#f5f1e8', 'point': '#c9a25a'},
    'layout': {},
    'tone_filter': '',
}


def _cfg(**kw):
    """基于默认填充一份完整 config，再按款覆盖。保证字段全集、少冗余。"""
    c = dict(_DEFAULT)
    c.update(kw)
    return c


# ===================================================================
# 蓝图补齐 · 6 款（template_id / 拓扑 / hero_zone / text_on_photo / 配方气质）
# ===================================================================
BLUEPRINT_CONFIGS = {
    # ---------- 35mm 光斑漏光日杂（红橙漏光 + 荧光橙数码日期戳）----------
    'light_leak': _cfg(
        template_id='_tpl_light_leak', topology='bottom_left', hero_zone='left_vertical',
        text_on_photo=True,
        fonts={'hero': 'BebasNeue', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 120, 'lead_px': 34, 'micro_px': 10,
               'hero_lh': 0.92, 'hero_letter': '0.18em', 'hero_shadow': '0 2px 12px rgba(0,0,0,.55)'},
        palette={'primary': '#1a0b06', 'accent': '#ff5c1a', 'point': '#ffb200'},
        layout={'leak_side': 'right',          # 漏光从哪一侧灌入（radial 光斑）
                'leak_strength': 0.36,        # 漏光强度（0~1）
                'stamp_pos': 'bottom_left'},  # 日期戳落区
        tone_filter='saturate(1.15) contrast(1.05)',
    ),
    # ---------- 深度咬合（Cormorant 大字母压主体留白 · 简化：CSS 叠字）----------
    'deep_interlock': _cfg(
        template_id='_tpl_deep_interlock', topology='right_wing', hero_zone='right_vertical',
        text_on_photo=True,
        fonts={'hero': 'CormorantItalic', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        scale={'hero_px': 132, 'lead_px': 36, 'micro_px': 10,
               'hero_lh': 0.95, 'hero_letter': '0.05em', 'hero_shadow': '0 4px 20px rgba(0,0,0,.5)'},
        palette={'primary': '#0d0d0e', 'accent': '#e6e0d4', 'point': '#b8933f'},
        layout={'giant':'right',              # 叠字前景大字母方向
                'giant_opacity': 0.16,        # 背景叠字透明度
                'giant_fs': 340},             # 背景叠字基准字号
        tone_filter='',
    ),
    # ---------- 悬垂流淌（书法从天顶垂落）----------
    'draping': _cfg(
        template_id='_tpl_draping', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True,
        fonts={'hero': 'LXGWWenKai', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        scale={'hero_px': 118, 'lead_px': 36, 'micro_px': 11,
               'hero_lh': 1.0, 'hero_letter': '0.1071em', 'hero_shadow': '0 3px 14px rgba(0,0,0,.4)'},
        palette={'primary': '#201a12', 'accent': '#e8dcc0', 'point': '#b83c23'},
        layout={'col_gap': 26,                # 天顶垂落竖列间距
                'fade_bottom': 0.62,          # 垂落渐隐终点（越高越短）
                'hanging_columns': True},     # 竖排从天顶垂落
        tone_filter='saturate(0.95)',
    ),
    # ---------- 横向穿过（极宽色带横贯 · 简化：人物限定版）----------
    'silhouette': _cfg(
        template_id='_tpl_silhouette', topology='right_wing', hero_zone='right_vertical',
        text_on_photo=True,
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 110, 'lead_px': 32, 'micro_px': 10,
               'hero_lh': 0.95, 'hero_letter': '0.15em', 'hero_shadow': '0 3px 12px rgba(0,0,0,.45)'},
        palette={'primary': '#101013', 'accent': '#c9a25a', 'point': '#f0e9dc'},
        layout={'step_count': 4,              # 阶梯块数量
                'step_h': 22,                 # 阶梯块高度
                'step_gap': 12,               # 阶梯块间距
                'step_side': 'right'},        # 阶梯块贴哪侧
        tone_filter='saturate(1.0)',
    ),
    # ---------- 泰山巨碑（底部 100-140px 特粗宋体如泰山托底）----------
    'bedrock_stele': _cfg(
        template_id='_tpl_bedrock_stele', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True,
        fonts={'hero': 'SourceSerifHeavy', 'emotion': 'LXGWWenKai', 'data': 'SpaceMono'},
        scale={'hero_px': 140, 'lead_px': 40, 'micro_px': 11,
               'hero_lh': 0.95, 'hero_letter': '0.08em', 'hero_shadow': '0 4px 20px rgba(0,0,0,.55)'},
        palette={'primary': '#0f0c08', 'accent': '#f3ead8', 'point': '#b83c23'},
        layout={'stele_bottom_px': 44,        # 托底主标距底
                'stele_h_px': 132},           # 托底主标行高（泰山托底）
        tone_filter='saturate(1.0)',
    ),
    # ---------- 无界延展（240px Bebas 切满左右两极）----------
    'midnight': _cfg(
        template_id='_tpl_midnight', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True,
        fonts={'hero': 'CinzelBold', 'emotion': 'SourceSerifHeavy', 'data': 'SpaceMono'},
        scale={'hero_px': 120, 'lead_px': 36, 'micro_px': 10,
               'hero_lh': 0.92, 'hero_letter': '0.1em', 'hero_shadow': '0 4px 20px rgba(0,0,0,.7)'},
        palette={'primary': '#0a1430', 'accent': '#d4af37', 'point': '#f0f0f0'},
        layout={'headline_top_px': 64,        # 刊头距顶
                'dark_overlay': 0.5},         # 暗蓝压暗强度
        tone_filter='saturate(1.1) contrast(1.05)',
    ),
}

# 供 engine_v2 的 --genre choices 并入
BLUEPRINT_IDS = list(BLUEPRINT_CONFIGS)


if __name__ == '__main__':
    # 自检：字段全集（必填 + 可选）+ 数量 + template_id 映射完整性 + text_on_photo
    _req = ('mode', 'template_id', 'topology', 'hero_zone', 'text_on_photo',
            'fonts', 'scale', 'palette', 'layout')
    _opt = ('tone_filter',)                  # 可选字段：照片调子（'' 无）
    _known = list(_req) + list(_opt)
    assert len(BLUEPRINT_CONFIGS) == 6, f"config 数量应为 6，实际 {len(BLUEPRINT_CONFIGS)}"

    bad = {g: [f for f in _req if f not in c] for g, c in BLUEPRINT_CONFIGS.items()
           if not all(f in c for f in _req)}
    unknown = {g: [f for f in c if f not in _known] for g, c in BLUEPRINT_CONFIGS.items()
               if any(f not in _known for f in c)}
    assert not bad, f"字段缺失: {bad}"
    assert not unknown, f"未知字段: {unknown}"

    # 每款 mode 必须为 'B'；text_on_photo 必须为 True；template_id 一一对应且端点明确
    _tpl_ok = {
        'light_leak': '_tpl_light_leak', 'deep_interlock': '_tpl_deep_interlock',
        'draping': '_tpl_draping', 'silhouette': '_tpl_silhouette',
        'bedrock_stele': '_tpl_bedrock_stele', 'midnight': '_tpl_midnight',
    }
    for g, c in BLUEPRINT_CONFIGS.items():
        assert c['mode'] == 'B', f"{g} mode 应为 'B'，实际 {c['mode']!r}"
        assert c['text_on_photo'] is True, f"{g} text_on_photo 应为 True（文字压照片）"
        assert c['template_id'] == _tpl_ok[g], f"{g} template_id 应为 {_tpl_ok[g]!r}"

    # 子字段全集
    _sub = {
        'fonts': ('hero', 'emotion', 'data'),
        'scale': ('hero_px', 'lead_px', 'micro_px', 'hero_lh', 'hero_letter', 'hero_shadow'),
        'palette': ('primary', 'accent', 'point'),
    }
    bad_sub = {g: {k: [f for f in v if f not in c[k]] for k, v in _sub.items()
                  if any(f not in c[k] for f in v)} for g, c in BLUEPRINT_CONFIGS.items()
               if any(any(f not in c[k] for f in v) for k, v in _sub.items())}
    assert not bad_sub, f"子字段缺失: {bad_sub}"

    # scale 数值须为正数
    bad_scale = {g: {k: v for k, v in c['scale'].items() if k in ('hero_px', 'lead_px', 'micro_px')
                     and not (isinstance(v, (int, float)) and v > 0)} for g, c in BLUEPRINT_CONFIGS.items()
                 if any(k in ('hero_px', 'lead_px', 'micro_px')
                        and not (isinstance(v, (int, float)) and v > 0)
                        for k, v in c['scale'].items())}
    assert not bad_scale, f"scale 数值须为正: {bad_scale}"

    assert len(BLUEPRINT_IDS) == 6, "BLUEPRINT_IDS 应为 6"
    print(f"blueprint_configs OK · {len(BLUEPRINT_CONFIGS)} 款 · 字段全集(必填{len(_req)}+可选{len(_opt)})"
          f" · mode=('B'×6) · text_on_photo=(True×6)")
