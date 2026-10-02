#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
载体隐喻流派族 · 参数化 configs（7 款）
===========================================
独立流派族（物格思维）：让照片"变身"成一件实物/媒介（拍卖图录/节目单/解密档案/
月相历/乐谱手稿/拱顶弧线/取景器），文字按"物的解剖"落位（LOT 号、印章、涂黑条、
月相序列、五线谱、弧线、取景读数）——不是"哪有空隙往哪放"。

每款 config 字段（供 metaphor_engine.render 使用）：
  template_id   : 构建函数名（_tpl_auction / _tpl_playbill / _tpl_dossier /
                  _tpl_lunar / _tpl_score / _tpl_arch / _tpl_viewfinder）
  mode          : 'M'（载体隐喻家族标记；**非分发键**——分发按 template_id）
  topology      : 绑定拓扑槽位（metadata；权威注册在 topology_registry.py）
  hero_zone     : 主标真实落区枚举（供 validate_layout_consistency 计算）
  text_on_photo : bool —— hero 文字是否落在照片上（护脸判别键）
  base_color    : 基调色（hex）—— 本款"物"的主色调
  tone_filter   : 照片 CSS filter（'' 无；如 sepia(0.15) saturate(1.2) 暖调）

title / sub / date / location 一律由 CLI 参数传入，**不硬编码文案**。
7 款均不作护脸款（用户拍板：通用风格），即使其中 3 款 text_on_photo==False，
也不强绑 face_portrait（见 topology_registry.face_safe_genres 的排除）。
"""

# ---- 共享默认（保证字段全集；每款按"物"的气质覆盖）----
_DEFAULT = {
    'mode': 'M',
    'template_id': '',
    'topology': '',
    'hero_zone': '',
    'text_on_photo': True,
    'base_color': '#f5f1e8',
    'tone_filter': '',
}


def _cfg(**kw):
    """基于默认填充一份完整 config，再按款覆盖。保证 7 字段全集、少冗余。"""
    c = dict(_DEFAULT)
    c.update(kw)
    return c


# ===================================================================
# 载体隐喻流派族 · 7 款（template_id / 拓扑 / hero_zone / text_on_photo / 基调）
# ===================================================================
METAPHOR_CONFIGS = {
    # ---------- 拍卖图录（米白 · 顶部 EVENING SALE + LOT 号 · 底部《title》+ sub）----------
    'auction_catalog': _cfg(
        template_id='_tpl_auction', topology='matted_gallery', hero_zone='bottom_card',
        text_on_photo=False, base_color='#f5f1e8', tone_filter='',
    ),
    # ---------- 剧场节目单（赭红 + 金 · 左侧金竖排 title · 折子戏场目 ACT/FINALE）----------
    'playbill': _cfg(
        template_id='_tpl_playbill', topology='right_wing', hero_zone='right_vertical',
        text_on_photo=False, base_color='#6b2318', tone_filter='sepia(0.08)',
    ),
    # ---------- 解密档案卷宗（牛皮纸 · 顶部档案头 + 红章「解密」· 涂黑红action条）----------
    'declassified_file': _cfg(
        template_id='_tpl_dossier', topology='zenith_center', hero_zone='top_center',
        text_on_photo=False, base_color='#e8dcc0', tone_filter='sepia(0.12) saturate(0.95)',
    ),
    # ---------- 月相历法盘（深空 · 顶部月相八相 + 底部月度诗词）----------
    'lunar_dial': _cfg(
        template_id='_tpl_lunar', topology='bedrock_base', hero_zone='bottom_center',
        text_on_photo=True, base_color='#0a0d12', tone_filter='',
    ),
    # ---------- 乐谱手稿（米白乐谱纸 · 上下五线谱 + 谱号 + 速度/调号）----------
    # photo_ratio（可选）：照片占比因子，默认 1.0 = v2 基准（上谱线 78px/下 56px/标题 32px，照片≈65%）。
    #   仅 music_manuscript 供 --photo-ratio 微调（谱线按 1/photo_ratio 缩放，见 metaphor_engine._tpl_score）；
    #   其它 6 款 config 不设该字段（缺省 1.0，模板不读它，行为不变）。
    'music_manuscript': _cfg(
        template_id='_tpl_score', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True, base_color='#f7f2e6', tone_filter='saturate(0.96)',
        photo_ratio=1.0,
    ),
    # ---------- 拱顶弧线（暖金 · SVG textPath 曲线标题 + 顶部渐变压暗）----------
    'arch_curved': _cfg(
        template_id='_tpl_arch', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True, base_color='#e5c98a', tone_filter='sepia(0.15) saturate(1.2)',
    ),
    # ---------- 相机取景器（黑白 UI · 四角括号 + 中央十字 + 顶部机身参数）----------
    'viewfinder_ui': _cfg(
        template_id='_tpl_viewfinder', topology='zenith_center', hero_zone='top_center',
        text_on_photo=True, base_color='#0a0a0a', tone_filter='',
    ),
}

# 供 engine_v2 的 --genre choices 并入
METAPHOR_IDS = list(METAPHOR_CONFIGS)


if __name__ == '__main__':
    # 自检：字段全集（必填 + 可选）+ 数量 + template_id 映射完整性
    _req = ('template_id', 'mode', 'topology', 'hero_zone', 'text_on_photo',
            'base_color', 'tone_filter')
    _opt = ('photo_ratio',)                  # 可选字段：仅 music_manuscript（照片占比因子，默认 1.0）
    _known = _req + _opt
    bad = {g: [f for f in _req if f not in c] for g, c in METAPHOR_CONFIGS.items()
           if not all(f in c for f in _req)}
    unknown = {g: [f for f in c if f not in _known] for g, c in METAPHOR_CONFIGS.items()
               if any(f not in _known for f in c)}
    bad_ratio = {g: c['photo_ratio'] for g, c in METAPHOR_CONFIGS.items()
                 if 'photo_ratio' in c
                 and not (isinstance(c['photo_ratio'], (int, float)) and c['photo_ratio'] > 0)}
    _tpl_ok = {
        'auction_catalog': '_tpl_auction', 'playbill': '_tpl_playbill',
        'declassified_file': '_tpl_dossier', 'lunar_dial': '_tpl_lunar',
        'music_manuscript': '_tpl_score', 'arch_curved': '_tpl_arch',
        'viewfinder_ui': '_tpl_viewfinder',
    }
    assert len(METAPHOR_CONFIGS) == 7, f"config 数量应为 7，实际 {len(METAPHOR_CONFIGS)}"
    assert not bad, f"字段缺失: {bad}"
    assert not unknown, f"未知字段: {unknown}"
    assert not bad_ratio, f"photo_ratio 必须为正数: {bad_ratio}"
    assert METAPHOR_CONFIGS['music_manuscript']['photo_ratio'] == 1.0, \
        "music_manuscript photo_ratio 默认应为 1.0"
    assert len(METAPHOR_IDS) == 7, "METAPHOR_IDS 应为 7"
    # 每款 mode 必须为 'M'；template_id 必须落在已知构建函数集内且与 id 一一对应
    for g, c in METAPHOR_CONFIGS.items():
        assert c['mode'] == 'M', f"{g} mode 应为 'M'，实际 {c['mode']!r}"
        assert c['template_id'] == _tpl_ok[g], f"{g} template_id 应为 {_tpl_ok[g]!r}"
    _has_ratio = [g for g in METAPHOR_CONFIGS if 'photo_ratio' in METAPHOR_CONFIGS[g]]
    print(f"metaphor_configs OK · {len(METAPHOR_CONFIGS)} 款 · 字段全集(必填{len(_req)}+可选{len(_opt)}) · mode=('M'×7) · photo_ratio 款: {', '.join(_has_ratio) or '无'}")
