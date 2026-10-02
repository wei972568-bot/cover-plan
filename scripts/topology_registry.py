#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面计划 · 拓扑结构库（Topology Registry）
===========================================

本文件承载"读图→挑拓扑→定制"链路的前两步：**拓扑分类学（taxonomy）** + **挑拓扑匹配**。
- **拓扑定义**：把 9 拓扑的字段（id/名称/文字落区/避开区/适合结构/主次流派/默认材质）
  落成数据结构（TOPOLOGY_REGISTRY），供匹配与对外解释。基础 8 槽位为蓝图 §3；拓09 face_portrait
  （大头人像）为 2026-09-01 首次实测"脸满幅特写"后新增的独立骨架。
  ⚠️ 原「06 水平居腰封/横带 equator_belt」已于 **2026-09-14 按用户拍板整体移除**（根因否决：
  正视图中横贯照片不可行）——注册表 / TOPOLOGY_RULES / `_topo_family` / `_compat['middle']` 全删。
- **挑拓扑匹配**：`topology_supports()`（本节 3）按 image_features 给 9 拓扑打分选优——
  image_features 由 `analyze_pixel.py`（像素辅）产出、智能体 `read_image`（模型主）合并。
- **流派 hero 落区**：`GENRE_LAYOUT_SIGNATURE`（本节 1.5）记录每流派**实际**渲染的主标落区与
  是否压照片（text_on_photo）。注册表"拓扑↔流派"错位（stone 等）由此暴露、供复核。
本模块**不实现读图**（那是 analyze_pixel.py + 智能体 read_image 的职责），也**不修改** engine_v2.py。

====================================================================
0. 数据来源与权威取向
====================================================================
- 9 拓扑：基础 8 槽位 id 沿用 engine_v2.py 的 TOPOLOGY 注册名（zenith_center / right_wing / ...）；
  拓09 face_portrait 为本库新增（engine_v2.py 无此槽位，属"必要+普适"新骨架）。
- 2026-09-05 真删除 24 款装裱款 + 4 蓝原名别名（chroma/polaroid/victorian/stamp，目标款已删）：
  KNOWN_GENRES/GENRE_LAYOUT_SIGNATURE/TOPOLOGY_REGISTRY 三处同步剔除（保留池 14 款见
  docs/批量设计-真删除与字体驱动款-设计.md §1.1）。
- 基础 8 拓扑的"文字落区 / 避开区"以 PROJECT_BLUEPRINT.md §3 为唯一权威表
  （⚠️ 该表为设计原稿 9 拓扑；现役基础 8 已按 2026-09-14 用户拍板移除 06 equator_belt，
  蓝图原稿行保留为设计史记录、不回改——**现役以本注册表为准**）；
  拓09 face_portrait 的 text_zone/avoid_zone 依据 P0-7 护脸铁律（新表）。
- 基础 8 拓扑的"适合结构 / 主次流派"以 拓扑结构库设计.md §2 为唯一权威表（用户拍板采纳）。
- 流派 genre id 一律采用 engine_v2.py 的**准确命名**（zen / pulip / stone / ...），
  未来 28 套蓝图流派沿用其配方 id（bedrock_stele / dual_portals / ...）。
- family-4 装饰明信片 french / gatsby：**2026-09-02 已注册为使引擎可达的原 id，走装裱族纯别名映射**（french→french_par_avion / gatsby→art_deco_gatsby，engine_v2 `--genre` 可直达，输出与装裱款一致）。victorian / stamp / chroma / polaroid 四条别名随 2026-09-05 目标款删除而下线。

【取向取舍（诚实标注）】
- 主/次流派以 设计.md §2 为准。其中：
  * "主" = 默认/本性绑定该拓扑的流派：
      - engine 已实现的 14 套 → 按 engine_v2.py 的 default_topology；
      - 未来 14 套蓝图流派 → 按 PROJECT_BLUEPRINT.md §4 的"建议拓扑"（primary 槽位）。
    两者对已实现的 14 套完全一致（核对过：蓝图建议拓扑-primary == engine default_topology）。
  * "次" = 可选（可换到该拓扑）的流派（其默认绑定在别处）。
- 注意一处对 设计.md 的偏离：设计.md 把 draping / deep_interlock / piercing 三套归为
  "次流派"（专业变体）。为满足本文件验收标准"每个流派都能至少在一个拓扑的『主流派』找到"，
  本库把这三套按其默认/建议拓扑（01 / 03 / 06）**提升为『主流派』**，不再单列为『次』。
  （piercing 已于 2026-09-05 下线 → 现役两套：draping / deep_interlock。）
  若你坚持 设计.md 的"变体归次"口径，需回退此提升并放宽验收（记录为取舍）。

====================================================================
1. 新增拓扑的机制（必要性 + 普适性）
====================================================================
**何时新增**：读图发现某结构（如死白天幕、左右对称、对角线构图、脸满幅特写）9 拓扑都**套不住**时——才新增。
**新增一个拓扑 = 3 件事**（不是只加一张图）：
  1. 定义槽位：文字落区 / 避开区 / 适合什么结构（像 9 槽位那样明确）。
  2. 默认打底材质：配什么纹饰（需先注册到材质库）。
  3. 配套流派：这个拓扑能微调出哪几套（字体/配色/避坑）。
**避免**（真三层爆炸教训）：新拓扑是**新增一个骨架**，配套自己的**默认精品样式**，
不是"每个流派 × 拓扑"自由组合。候选新拓扑（天顶墨岚压印/白卡纸大开门/接触印相黑卡）
需**先证明 9 拓扑套不住**才预置（必要性），且要能撑多种图（普适性）——本步**不预置**。
☆ 拓09 face_portrait（大头人像）已于 2026-09-01 实测证明必要性：8 基础拓扑都会把字压到
  "脸满幅"的面部五官上（P0-7 违例），且像素把头发误判成留白——故新增独立骨架。

====================================================================
2. 验收标准（本模块满足即通过）
====================================================================
  ① registry 加载后校验 9 拓扑都有完整字段：
     id / name / text_zone / avoid_zone / suitable_structure /
     primary_genres / secondary_genres / default_material。
  ② 每个流派（28 套全集）都能至少在一个拓扑的 primary_genres（主流派）找到。
  ②' face_portrait（拓09）的主流派必须全部为护脸流派（text_on_photo==False）。
  ③ 非法 id / 无匹配结构有明确行为：
     - get_topology(unknown_id) 抛 KeyError（带清晰 message）；
     - topology_supports(无匹配特征) 返回 {'needs_new_topology': True, ...} 提示"必要性+普适性"。

====================================================================
3. 与现有体系的关系（边界）
====================================================================
- 本模块做"拓扑分类学 + 挑拓扑匹配"，**不实现读图**（读图 = analyze_pixel.py + 智能体 read_image），
  **不破坏** engine_v2.py 现有 14 套。
- 本模块不 import engine_v2（避免耦合）；流派 id 是我核对 engine_v2.py GENRE 键后硬编码的。
"""

# ===================================================================
# 0. 常量：流派全集 & 字段清单
# ===================================================================
# 28 套蓝图流派全集（核对 PROJECT_BLUEPRINT.md §4 与 engine_v2.py GENRE 键）。
# engine_v2.py 已实现其中的 14 套；其余 14 套蓝图概念已全部落地（8 蓝图补齐 + 2 蓝原名别名，
# 2026-09-02 注册 6 条；2026-09-05 真删除下线 chroma/polaroid/victorian/stamp 4 条）。
KNOWN_GENRES = {
    # family-1 重磅大刊
    'nocturne', 'pulip', 'bauhaus',
    # family-2 东方水墨金石
    'zen', 'slender_zen', 'stone', 'imperial',
    # family-3 胶片与宝丽来
    'film', 'light_leak',
    # family-4 装饰明信片（命名依据见模块 docstring『0. 数据来源与权威取向』）
    # B11：nordic 已删；2026-09-05 真删除下线 victorian/stamp（目标装裱款已删）。
    'french', 'gatsby',
    # family-5 空间多维交互
    'layered', 'deep_interlock', 'draping', 'silhouette',
    # family-6 天幕巨构
    'monumental', 'dual_portals', 'bedrock_stele',
    # family-7 黑胶唱片
    'blue_note', 'midnight',
    # family-8 科考档案
    'specimen',

    # =================================================================
    # 装裱/影格流派族（13 款，2026-09-05 真删除 24 款后 · 2026-09-14 微调批2 −5 款 · 独立流派族；保留池见设计 §1.1）
    # F 窗式 + E 纹饰式 = text_on_photo==False（护脸）；
    # D 顶栏式 = text_on_photo==True（不护脸，仅避五官需人工核）。
    # =================================================================
    # 任务2-A 画廊/卡纸窗（3）
    'dark_contact_print', 'gallery_ice_crack', 'gallery_centered_axis',
    # 任务2-D 现代/素笺（1，text_on_photo==True，不护脸）；
    #   ~~fashion_vogue~~ 2026-09-14 用户拍板彻底删除
    'oriental_plain_paper',
    # WP-C · 底部落字款（2026-09-05 §5 +script_bottom/cinzel_bottom，T-mode layout='bottom'，
    #        text_on_photo==True，不护脸；原款 vogue_bottom 于 2026-09-14 微调批2 彻底删除）
    'script_bottom', 'cinzel_bottom',
    'french_elegance',
    # 任务2-E 装饰/齿孔（4，text_on_photo==False 护脸）
    'french_par_avion', 'art_deco_gatsby', 'nordic_meander', 'film_rsx_sprocket',
    # 任务3 画廊框×色差（1，text_on_photo==False 护脸）
    'gallery_frame_warm',
    # 字体驱动段（原 5 款，2026-09-05 §2.1 配对表，骨架×字体；无新模板）
    # F/O 落区款：text_on_photo==False（护脸）；T 落区款：True（不护脸，随骨架）
    # 2026-09-14 微调批2：删 elegance_yeseva/oriental_zhuokai/film_xingkai/warm_zhuokai_card → 余 1 款
    'par_avion_marcellus',

    # =================================================================
    # 载体隐喻流派族（7 款，2026-09-02 新增 · 物格思维 · 独立流派族）
    # 独立命名，不与蓝图 28 / engine_v2 现有 13 套合并。均不作护脸款（用户拍板：
    # 通用风格），即使其中 3 款 text_on_photo==False 也不强绑 face_portrait
    # （face_safe_genres 显式排除，见下）。
    # =================================================================
    'auction_catalog', 'playbill', 'declassified_file', 'lunar_dial',
    'music_manuscript', 'arch_curved', 'viewfinder_ui',

    # =================================================================
    # 设计语言流派族（6+4 款，2026-09-06 六款 + 2026-09-07 彩活四款 · design canonical · 第 5 族）
    # 探针定稿（docs/批量设计-新设计语言六款-设计.md §1 + docs/批量设计-彩活四款-设计.md §1）。
    # 护脸语义按款（v3 修正：pop_halftone 改黑底贴纸款，标题全落黑底区 → False 护脸）：
    #   护脸（text_on_photo==False）：pop_halftone / kinfolk_air / museum_frame /
    #   super_index / retro_tv / collage_man（蛋窗+bottom 文字，v3 融合版）；
    #   非护脸（True，需人工核）：swiss_red_grid（满幅）/ street_zine（标题压照片下部）/
    #   duo_pop（红块 300px+圆点覆盖照片下部，方案 b）/ doodle_summer（标题落洗白渐隐带）。
    # =================================================================
    'pop_halftone', 'kinfolk_air', 'museum_frame',
    'swiss_red_grid', 'super_index', 'retro_tv',
    'street_zine', 'duo_pop', 'doodle_summer', 'collage_man',

    # =================================================================
    # 设计语言族 · 构图三款（2026-09-08，docs/批量设计-构图三款-设计.md §1）
    # 护脸语义：branch_magazine=False（照片在独立斜切窗内，文字/花枝全落留白区）；
    # pop_lichtenstein / pop_press = True（爆炸星/星群破界压照片底缘=原稿有意构图，
    # 满幅装饰型——保守策略注册 T 槽需人工核；照片本体止于 76%/87% 高度，
    # 黑条/底部文字不压照片）
    # =================================================================
    'branch_magazine', 'pop_lichtenstein', 'pop_press',

    # =================================================================
    # 设计语言族 · 撕纸手帐（2026-09-09，docs/批量设计-torn_journal-设计.md §1.5 · 第 14 款，
    # +1 款（2026-09-09 撕纸手帐））
    # 护脸语义：torn_journal = True（气泡/喇叭/T恤/go!徽章/白竖排短语轻搭照片边缘
    # =拼贴语义，不护脸需人工核；主标/副标/竖排轨道全落纸面；无印章）
    # =================================================================
    'torn_journal',
    # =================================================================
    # 设计语言族 · 展览海报（2026-09-10，docs/批量设计-展览海报-设计.md §1.6 · 第 15 款，
    # +1 款（2026-09-10 展览海报））
    # 护脸语义：exhibition_poster = False（文字全落纸面白边，不压照片任何像素，护脸安全；
    # 主标/副标参数化 + 左右竖排霞鹜文楷大字/朱砂红展签/底栏三栏=装饰位固定文案；无印章
    # =现代画廊语义→几何标贴）
    # =================================================================
    'exhibition_poster',
    # =================================================================
    # 设计语言族 · 撕纸破洞窥视（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 16 款，
    # +1 款（2026-09-10 撕纸两款））
    # 护脸语义：torn_peephole = False（主标/副标/揭语全落牛皮纸封面文字区，照片在破洞内
    # 零裁剪完整可见，不压照片任何像素，护脸安全；无印章）
    # =================================================================
    'torn_peephole',
    # =================================================================
    # 设计语言族 · 撕纸双层撕纸（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 17 款，
    # +1 款（2026-09-10 撕纸两款））
    # 护脸语义：torn_deckle = False（标题纸片固定右下角、骑线仅轻压照片底部约 6.5%，
    # 拼贴语义同 torn_journal——用户 2026-09-10 拍板不作人工核脸款）
    # =================================================================
    'torn_deckle',

    # =================================================================
    # 设计语言族 · 新款两款（2026-09-16，docs/新款入库批-设计.md §2.1 · 第 18/19 款，
    # +2 款（2026-09-16 新款入库批））
    # 护脸语义：两款均 text_on_photo=False（文字全落照片区外：modern_spread 标题/
    # 元数据在照片上方、页脚在下方；cultural_journal 标题群在上方、图注/注记在下方）
    # =================================================================
    'modern_spread', 'cultural_journal',
}

# 每个拓扑条目必须含有的字段（验收①）。
REQUIRED_FIELDS = (
    'id', 'name', 'text_zone', 'avoid_zone', 'suitable_structure',
    'primary_genres', 'secondary_genres', 'default_material',
)

# 合法的默认材质取值（与 engine_v2.py MATERIAL 中实际用于拓扑的 3 类一致）。
ALLOWED_MATERIALS = ('oriental_cloud', 'film_rsx', 'none')


# ===================================================================
# 1. TOPOLOGY_REGISTRY（9 槽位：基础 8 + 拓09 face_portrait 大头人像）
# ===================================================================
# 每条约目字段含义（== 蓝图 §3 / 设计.md §2 的列 ==）：
#   id                  ENGINE-v2 注册 id（= 蓝图槽位 01~09）
#   name                中文名（用 拓扑结构库设计.md / 蓝图 命名）
#   text_zone           文字落区（蓝图 §3 "主视觉重心落点"）
#   avoid_zone          避开区（蓝图 §3 "绝对禁止主文字区"）
#   suitable_structure  适合结构（设计.md §2 新列："什么图大体上该落这个拓扑"）
#   primary_genres      主流派（= 默认/本性绑定该拓扑的流派）
#   secondary_genres    次流派（= 可选，可换到该拓扑；默认绑定在别处）
#   default_material    默认打底材质（hint；流派级 default_material 优先）

TOPOLOGY_REGISTRY = {
    # ---------- 01 正中天穹压顶 ----------
    'zenith_center': {
        'id': 'zenith_center',
        'name': '正中天穹压顶',
        'text_zone': '正上方 X50% 居中，Y5-25%，240px 巨字',
        'avoid_zone': '左上 / 右上 / 边缘角',
        'suitable_structure': '主体居中偏下、大片上方留白',
        'primary_genres': ['pulip', 'monumental', 'nocturne', 'imperial', 'blue_note', 'midnight', 'draping',
                           # 引擎套 hero 实际偏上（几何大字/竖排刊头近上）→ 归正中天穹（审计修正：原误绑 equator_belt/right_wing）
                           'bauhaus', 'slender_zen',
                           # 装裱/影格 D 顶栏式（text_on_photo==True，不护脸，仅避五官）
                           # ~~fashion_vogue~~ 2026-09-14 用户拍板彻底删除
                           # 载体隐喻（M · 物格）：顶部/中轴落位（解密档案头 / 乐谱手稿 / 拱顶弧线 / 取景器）
                           'declassified_file', 'music_manuscript', 'arch_curved', 'viewfinder_ui',
                           # 设计语言族（2026-09-06 +super_index：文字全落顶部刊头带，护脸）
                           # 2026-09-09 撕纸手帐 +1：主标顶部正中落纸面（T 需人工核，见 KNOWN_GENRES 注）
                           'super_index', 'torn_journal',
                           # 2026-09-10 展览海报 +1：主标顶部正中落纸面（text_on_photo=False 护脸安全）
                           # 2026-09-10 撕纸两款 +2：主标顶部正中落纸面（均 text_on_photo=False 护脸安全；
                           #   torn_deckle 纸片骑线轻压照片底部约 6.5%，拼贴语义同 torn_journal）
                           'exhibition_poster', 'torn_peephole', 'torn_deckle',
                           # 2026-09-16 新款入库批 +2：主标顶部正中落版面（均 text_on_photo=False
                           # 护脸安全；modern_spread 标题在照片上方/cultural_journal 标题群在上方）
                           'modern_spread', 'cultural_journal'],
        'secondary_genres': [],
        'default_material': 'none',
    },
    # ---------- 02 底部泰山地基 ----------
    'bedrock_base': {
        'id': 'bedrock_base',
        'name': '底部泰山地基',
        'text_zone': '正下方 X50% 沉底，Y70-95%，100-140px',
        'avoid_zone': '上半部 60%',
        'suitable_structure': '主体在上、下方空',
        'primary_genres': ['bedrock_stele', 'lunar_dial',
                           # WP-C · 底部落字款（2026-09-05 §5 +2 款，字落照片底部渐变区）
                           'script_bottom', 'cinzel_bottom',
                           # 设计语言族（2026-09-06 +3 款：主标沉底——孟菲斯波点〔v3 黑底贴纸
                           # 款，字落黑底区·护脸〕/红格瑞士压照片〔不护脸〕/复古电视落深底〔护脸〕；
                           # 2026-09-07 彩活 +2 款：duo_pop 底部红块 300px 白字大标〔方案 b 原色，
                           # 压照片不护脸〕/doodle_summer 底部固定文案+渐隐带〔压照片不护脸〕）
                           'pop_halftone', 'swiss_red_grid', 'retro_tv',
                           'duo_pop', 'doodle_summer',
                           # 2026-09-08 构图三款 +2：pop_lichtenstein 星群破界+pop_press
                           # 满幅网点（bottom_center hero；T 需人工核，见 KNOWN_GENRES 注）
                           'pop_lichtenstein', 'pop_press'],
        'secondary_genres': [],
        'default_material': 'none',
    },
    # ---------- 03 右翼悬挂 / 右侧竖轴 ----------
    'right_wing': {
        'id': 'right_wing',
        'name': '右翼悬挂',
        'text_zone': '右上 / 右中 X60-95%，修长竖轴或右大刊头',
        'avoid_zone': '左侧全域 X0-50%',
        'suitable_structure': '主体偏左、右侧空',
        'primary_genres': ['zen', 'film', 'layered', 'silhouette', 'deep_interlock', 'stone',
                           # 装裱/影格 D 右翼竖轴（text_on_photo==True，不护脸）
                           'oriental_plain_paper',
                           # 载体隐喻（M · 物格）：剧场节目单 · 左竖轴占位
                           # （真实骨架为"左竖轴"，与 01 书脊精装同属待定新骨架；先按 right_wing 镜像占位，随 01 一并定）
                           'playbill'],
        'secondary_genres': [],
        'default_material': 'oriental_cloud',  # 旗手 zen 用东方云雷纹；film 流派级用 film_rsx 覆盖
    },
    # ---------- 04 天地对峙双极 ----------
    'dual_poles': {
        'id': 'dual_poles',
        'name': '天地对峙双极',
        'text_zone': '正顶 Y5% 与 正底 Y85% 垂直锁死',
        'avoid_zone': '左右两侧边际',
        'suitable_structure': '高度突出、上下呼应',
        # french_elegance B23 改"顶部英文+底部中文条带"（上+下），归本槽
        'primary_genres': ['dual_portals', 'french_elegance'],
        'secondary_genres': ['imperial'],  # 可选：imperial 蓝图建议拓扑 01·04，可换到本槽
        'default_material': 'none',
    },
    # ---------- 05 左下沉降锚点 ----------
    'bottom_left': {
        'id': 'bottom_left',
        'name': '左下沉降锚点',
        'text_zone': '左下 X5-45%、Y65-88%',
        'avoid_zone': '左上 / 右上 / 正顶',
        'suitable_structure': '主体右上、左下空',
        'primary_genres': ['light_leak'],
        'secondary_genres': [],
        'default_material': 'none',
    },
    # ---------- 06 四周边框环绕 ----------
    'perimeter_orbit': {
        'id': 'perimeter_orbit',
        'name': '四周边框环绕',
        'text_zone': '贴沿四周 10px，中央 80% 留空',
        'avoid_zone': '画面中央及四角',
        'suitable_structure': '主体居中、需要框住',
        'primary_genres': ['french', 'gatsby',
                           # 装裱/影格 E 装饰/齿孔（text_on_photo==False，护脸）
                           'french_par_avion', 'art_deco_gatsby',
                           'nordic_meander', 'film_rsx_sprocket',
                           # 字体驱动（O 落区款，落区继承骨架）
                           'par_avion_marcellus'],
        'secondary_genres': [],
        'default_material': 'none',
    },
    # ---------- 07 右下角印章与手札 ----------
    'bottom_right': {
        'id': 'bottom_right',
        'name': '右下角印章与手札',
        'text_zone': '右下 X55-90%、Y70-90%',
        'avoid_zone': '左上 / 左下 / 正顶',
        'suitable_structure': '主体左上、右下空',
        # 审计修正：stone 竖排 hero 实际落在左侧（left_vertical），非右下 → 迁至 right_wing（左↔右镜像互换，同 film/layered）；
        # 其朱红印（印章）仍落右下，但主标 hero 以 left_vertical 为准。本槽保留次流派。
        # 2026-09-07 +street_zine（填空槽）：底部右对齐大字+VOL/日期行落右下（探针 P1 终图
        # 与 hero 落区相符；docs/批量设计-彩活四款-设计.md §1.1 v2 修——原拟 bedrock_base
        # 与 hero 落区不符，美术规范 §2 本槽"暂空主"语义自洽）
        # 2026-09-08 +branch_magazine：左上文字块+右上竖排小字+花枝全落留白区，
        # 照片在独立斜切窗（护脸）；hero 签名 bottom_center 粗粒度映射 bottom_right 槽
        # （_compat['bottom'] 已含——street_zine 同槽先例）
        'primary_genres': ['street_zine', 'branch_magazine'],
        'secondary_genres': ['nocturne', 'film'],  # 可选：蓝图建议拓扑 01·08 / 03·08
        'default_material': 'oriental_cloud',  # stone 用东方云雷纹
    },
    # ---------- 08 大画廊卡纸装裱 ----------
    'matted_gallery': {
        'id': 'matted_gallery',
        'name': '大画廊卡纸装裱',
        'text_zone': '照片居中 100%，文字仅在下方独立白卡纸',
        'avoid_zone': '画面内部',
        'suitable_structure': '高调白片、需装裱',
        'primary_genres': ['specimen',
                           # 装裱/影格窗式 F/B/C/A（text_on_photo==False，护脸 + 卡纸装裱）
                           'dark_contact_print', 'gallery_ice_crack',
                           'gallery_centered_axis',
                           'french_par_avion', 'art_deco_gatsby',
                           'nordic_meander', 'film_rsx_sprocket',
                           'gallery_frame_warm',
                           # 载体隐喻（M · 物格）：字落在下方/装裱区（拍卖图录）
                           'auction_catalog',
                           # 设计语言族（2026-09-06 +2 款：字落照片窗外展签/文字带〔护脸〕；
                           # 装裱 F 款两槽先例——matted_gallery+face_portrait 同绑，拓扑库 §2）
                           'kinfolk_air', 'museum_frame'],
        'secondary_genres': [],
        'default_material': 'none',
    },
    # ---------- 09 大头人像 ----------
    # 2026-09-01 新增：首次测到"脸部特写满幅"这一结构，基础 8 拓扑都会把字压到面部五官上
    # （P0-7 主体不可遮挡），此前的 pixel 又把头发过度判成"留白"→ 需独立骨架。
    'face_portrait': {
        'id': 'face_portrait',
        'name': '大头人像',
        'text_zone': '仅额顶发际线上 / 两侧发缘 / 下颌以下（颈部），极少量，绝不落面部五官',
        'avoid_zone': '面部五官区（眉眼鼻嘴）+ 画面中央大部分',
        'suitable_structure': '人物脸部特写/大头像，脸满幅或头部占大，直视/微侧，几乎无留白',
        # 主流派必须全部 text_on_photo==False（护脸）。含 specimen + 装裱/影格护脸款
        'primary_genres': [
            'specimen',
            # F/B/C/A + E 全部 text_on_photo==False（字落卡/边框带，不落照片）
            'dark_contact_print', 'gallery_ice_crack',
            'gallery_centered_axis',
            'french_par_avion', 'art_deco_gatsby',
            'nordic_meander', 'film_rsx_sprocket',
            'gallery_frame_warm',
            # 字体驱动（F/O 落区款，text_on_photo==False 护脸）
            'par_avion_marcellus',
            # 设计语言族（2026-09-06 +2 款，text_on_photo==False 护脸：kinfolk 字落底部带、
            # museum 字落展签区；与 matted_gallery 两槽同绑——装裱 F 款先例，拓扑库 §2；
            # 2026-09-07 彩活 +collage_man：蛋窗 605×691 蛋窗内照片+文字全落窗外墙/底部，
            # 蛋窗构图只适合单人照（款约束写死，多人照质检提示换款））
            'kinfolk_air', 'museum_frame', 'collage_man',
        ],
        'secondary_genres': [],
        'default_material': 'none',
    },
}


# ===================================================================
# 1.5 GENRE_LAYOUT_SIGNATURE —— 流派「实际 hero 落区」签名
# ===================================================================
# 2026-09-01 新增（边界测试实锤问题 B）：
# 注册表"拓扑↔流派"绑定错位——stone 绑定拓08，但竖排 hero 实际落在左侧。
# （B11 已删 nordic：其绑定拓07"沿边"但 hero 实际居中落脸，正是删除主因。）
# **流派的真实布局 ≠ 拓扑元数据声明的 text_zone**。
# 因此新增本签名表：flow 每个流派**实际渲染**时主标（hero）落在哪、是否压在照片上（text_on_photo）。
# 字段（从 engine_v2.py 各流派 scale/layout 参数 + 实测渲染推导，非臆造）：
#   hero_zone      : 主标真实落区枚举（top_center / top_or_center / right_vertical / left_vertical /
#                    left_giant / upper_left / center_mid / vertical_masthead / top_and_bottom / bottom_card）
#   text_on_photo  : bool —— hero 文字是否落在照片上。False = 字落在独立卡纸/画面上（护脸判别键）。
#   note           : caveat；标 ⚠️ 表示与注册表绑定的 default_topology 的 text_zone 矛盾（需复核）。
GENRE_LAYOUT_SIGNATURE = {
    'zen':          {'hero_zone': 'right_vertical', 'text_on_photo': True,  'note': ''},
    'pulip':        {'hero_zone': 'top_center',     'text_on_photo': True,  'note': ''},
    'bauhaus':      {'hero_zone': 'top_or_center',  'text_on_photo': True,  'note': '几何大刊，hero 居中偏上；✅ 审计修正：绑拓01 正中天穹（原误绑拓06 腰封）'},
    'dual_portals': {'hero_zone': 'top_and_bottom', 'text_on_photo': True,  'note': ''},
    'blue_note':    {'hero_zone': 'top_center',     'text_on_photo': True,  'note': ''},
    'slender_zen':  {'hero_zone': 'vertical_masthead', 'text_on_photo': True, 'note': '竖排大字近上，左上/右上随构图浮动；✅ 审计修正：绑拓01 正中天穹（原误绑拓03 右翼）'},
    'monumental':   {'hero_zone': 'top_center',     'text_on_photo': True,  'note': ''},
    'nocturne':     {'hero_zone': 'top_center',     'text_on_photo': True,  'note': ''},
    'imperial':     {'hero_zone': 'top_center',     'text_on_photo': True,  'note': ''},
    'stone':        {'hero_zone': 'left_vertical',  'text_on_photo': True,  'note': '✅ 审计修正：绑拓03 右翼竖轴（左↔右镜像互换，同 film/layered；原误绑拓08 右下）'},
    'film':         {'hero_zone': 'upper_left',     'text_on_photo': True,  'note': 'hero 偏上左（避开齿孔带）'},
    'layered':      {'hero_zone': 'left_giant',     'text_on_photo': True,  'note': '巨字压入画外左侧；⚠️ 绑定拓03(右翼)但 hero 居左'},
    'specimen':     {'hero_zone': 'bottom_card',    'text_on_photo': False, 'note': '✅ 文字在下方独立卡纸/档案卡上，不落照片（护脸唯一选择）'},

    # =================================================================
    # 装裱/影格流派族（13 款，2026-09-05 真删除 24 款后 · 2026-09-14 微调批2 −5 款 · 保留池见设计 §1.1）
    # F 窗式 + E 纹饰式：text_on_photo==False → 护脸（字落卡/边框带）
    # D：text_on_photo==True → 不护脸（仅避五官，需人工核）
    # =================================================================
    # ---- 任务2-A 画廊/卡纸窗（F / face_portrait / bottom_card / 护脸）----
    'dark_contact_print':   {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 暗房接触印相，字落下方卡带'},
    'gallery_ice_crack':    {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 冰裂纹装裱，字落下方卡带'},
    'gallery_centered_axis':{'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 居中轴线装裱，字落下方卡带'},
    # ---- 任务2-D 现代/素笺（T，text_on_photo==True，不护脸，仅避五官）----
    # ~~fashion_vogue~~ 2026-09-14 用户拍板彻底删除（原：顶栏大字，文字落照片上方，避五官需人工核）
    # ~~vogue_bottom~~ 2026-09-14 微调批2 #17 用户拍板彻底删除（原：WP-C 底部落字款，主标/副标/meta 全落底部堆叠）
    'script_bottom':        {'hero_zone': 'bottom_center', 'text_on_photo': True, 'note': '底部落字家族（§5.2 手账甜美）：沐瑶软笔手写体主标 + ✦✦✦ 点缀 + 斜体副标，全落底部堆叠（不护脸，需人工核）'},
    'cinzel_bottom':        {'hero_zone': 'bottom_center', 'text_on_photo': True, 'note': '底部落字家族（§5.2 罗马碑刻）：CinzelBold 主标 + 两侧渐隐金线+金菱形点缀 + #efe6cf 副标，全落底部堆叠（不护脸，需人工核）'},
    'french_elegance':      {'hero_zone': 'top_and_bottom', 'text_on_photo': True, 'note': '法式·规避头部（B23）：顶部英文大字偏上/左上 + 右上 ISSUE_04 红标 + 底部中文条带，头部区留空'},
    'oriental_plain_paper': {'hero_zone': 'right_vertical', 'text_on_photo': True, 'note': '右翼竖排素笺，文字落照片右侧（避五官需人工核，不护脸）'},
    # ---- 任务2-E 装饰/齿孔（O / perimeter_orbit + face_portrait / bottom_card / 护脸）----
    'french_par_avion':     {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 航空明信片纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字（政策接受）'},
    'art_deco_gatsby':      {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 装饰艺术盖茨比纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字（政策接受）'},
    'nordic_meander':       {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 北欧回纹纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字（政策接受）'},
    'film_rsx_sprocket':    {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 35mm 齿孔影格纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字（政策接受）'},
    # ---- 任务3 画廊框×色差（F / face_portrait / bottom_card / 护脸）----
    'gallery_frame_warm':   {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 暖米大框，字落下方更暖色差文字带'},
    # ---- 字体驱动段（原 5 款，2026-09-05 §2.1：骨架×字体，落区继承骨架；2026-09-14 微调批2 −4）----
    'par_avion_marcellus':  {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ Marcellus×航空信笺（骨架 french_par_avion），字落边框底部卡带；绑拓07(沿边)视为装裱边框内正当落字（政策接受）'},
    # ~~elegance_yeseva / oriental_zhuokai / film_xingkai / warm_zhuokai_card~~ 2026-09-14
    # 微调批2 用户拍板彻底删除 4 款 → 字体驱动段现役仅 par_avion_marcellus。

    # =================================================================
    # 载体隐喻流派族（7 款，2026-09-02 新增 · 物格思维 · 独立流派族）
    # 均不作护脸款（用户拍板：通用风格）——text_on_photo 如实标，但 face_safe_genres
    # 显式排除本家族（含 3 款 text_on_photo==False 者），不强绑 face_portrait。
    # =================================================================
    # 拍卖图录（字落下方装裱区，不落照片）
    'auction_catalog':      {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '拍卖图录 · 顶部 EVENING SALE + LOT 号，字落下方装裱区（文案已参数化）'},
    # 剧场节目单（左竖轴占位，字落左侧金竖排，不落照片）
    'playbill':             {'hero_zone': 'right_vertical', 'text_on_photo': False, 'note': '剧场节目单 · 左竖轴占位；真实骨架"左竖轴"待定，随 01 一并定'},
    # 解密档案卷宗（字落顶部档案头/底部注记区，不落照片）
    'declassified_file':    {'hero_zone': 'top_center', 'text_on_photo': False, 'note': '解密档案 · 顶部档案头 + 红章，字落档案头/注记区（文案已参数化）'},
    # 月相历法盘（字压深空画面，避五官需人工核，不护脸）
    'lunar_dial':           {'hero_zone': 'bottom_center', 'text_on_photo': True, 'note': '月相历法盘 · 顶部月相八相 + 底部月度诗词，字压照片直接落底（非卡纸），故 hero 归 bottom_center（审计修正：原标 bottom_card 与绑定的拓02 底部不符）'},
    # 乐谱手稿（题名/速度块落谱纸头，不压照片核心；避五官需核，不护脸）
    'music_manuscript':     {'hero_zone': 'top_center', 'text_on_photo': True, 'note': '乐谱手稿 · 题名 + 速度/调号落谱纸头（避五官需人工核，不护脸）'},
    # 拱顶弧线（曲线标题压照片顶部，避五官需核，不护脸）
    'arch_curved':          {'hero_zone': 'top_center', 'text_on_photo': True, 'note': '拱顶弧线 · SVG textPath 曲线标题压照片顶部（避五官需人工核，不护脸）'},
    # 相机取景器（底部标题压照片，十字压脸当心，避五官需核，不护脸）
    'viewfinder_ui':        {'hero_zone': 'top_center', 'text_on_photo': True, 'note': '相机取景器 · 四角括号 + 中央十字 + 底部标题压照片（十字压脸需人工核，不护脸）'},

    # =================================================================
    # 蓝图补齐流派族（6 款现役，2026-09-02 新增 8 款 · blueprint canonical · 文字压照片）
    # 均 text_on_photo==True（**非护脸**）→ 由 text_on_photo 自然排除出 face_safe_genres，
    # 无需 _METAPHOR_NON_FACE_SAFE 式显式排除。
    # deep_interlock / silhouette 为「简化气质」（大字版式 + 简化咬合/环绕），不含真正发丝
    # 3D 咬合/顺轮廓抠像（另案，需轮廓识别）；light_leak / draping / bedrock_stele /
    # midnight 为「完整气质」（设计 §5 拆两档）。~~piercing/horizon~~ 2026-09-05 下线。
    # =================================================================
    # 35mm 光斑漏光日杂（红橙漏光 + 荧光橙数码日期戳；主标落左侧竖排）
    'light_leak':       {'hero_zone': 'left_vertical', 'text_on_photo': True, 'note': '红橙漏光日杂 · 主标落左侧竖排（字压照片，避五官需人工核，不护脸）'},
    # 深度咬合（简化：CSS 叠字，Cormorant 巨字压主体留白）
    'deep_interlock':   {'hero_zone': 'right_vertical', 'text_on_photo': True, 'note': '简化咬合 · 叠字大字压主体留白（字压照片，不护脸）'},
    # 悬垂流淌（书法从天顶垂落）
    'draping':          {'hero_zone': 'top_center', 'text_on_photo': True, 'note': '书法垂落 · 主标落天顶竖排（字压照片，不护脸）'},
    # 横向穿过（简化：人物限定版 · 极宽色带横贯）
    # 身形环绕（简化：阶梯标块顺边缘环抱）
    'silhouette':       {'hero_zone': 'right_vertical', 'text_on_photo': True, 'note': '简化环绕 · 阶梯块顺右缘 + 右竖轴主标（字压照片，不护脸）'},
    # 泰山巨碑（底置特粗宋体托底；经 bottom_center→bottom 映射落 bottom 家族）
    'bedrock_stele':    {'hero_zone': 'bottom_center', 'text_on_photo': True, 'note': '泰山托底 · 底部 100-140px 特粗宋体（字压照片，不护脸）'},
    # 无界延展（240px Bebas 切满左右两极）
    # 暗夜黑胶（暗蓝/暗金大字刊头）
    'midnight':         {'hero_zone': 'top_center', 'text_on_photo': True, 'note': '暗夜黑胶 · 暗蓝/暗金大字刊头（字压照片，不护脸）'},

    # =================================================================
    # 蓝图原 id（2 款，2026-09-02 注册 · 2026-09-05 真删除后剩 2 款 · 纯别名 → 装裱款）
    # =================================================================
    # 蓝图 28 套中的原概念 id 未单独实现，通过 --genre 直达时**纯别名**映射到
    # 对应装裱款（engine_v2 分发前解析 MATTING_ALIAS）。签名**取对应装裱款**的
    # hero_zone + text_on_photo：french_par_avion / art_deco_gatsby 为 O 类
    # text_on_photo=False（绑 perimeter_orbit）。故原 id 同样为护脸款（继承装裱款语义）。
    # chroma / polaroid / victorian / stamp 四条已随 2026-09-05 目标款删除而下线。
    'french':           {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 蓝原名 id french，别名→french_par_avion（航空明信片纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字）'},
    'gatsby':           {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 蓝原名 id gatsby，别名→art_deco_gatsby（装饰艺术盖茨比纹饰，字落边框底部卡带；绑定拓07(沿边)视为装裱边框内正当落字）'},

    # =================================================================
    # 设计语言流派族（6 款，2026-09-06 新增 · design canonical · 第 5 族）
    # 探针定稿（docs/批量设计-新设计语言六款-设计.md §1 终值）。
    # =================================================================
    # 孟菲斯波点（v3 黑底贴纸款：黑底+黄波点+粉青双框+斜贴纸标题块+底部黄字大标，
    # 标题全落黑底区 → text_on_photo=False 护脸；槽归属 bedrock_base 不变——hero 仍
    # bottom_center，与拓02"底部泰山"落区语义相符）
    'pop_halftone':     {'hero_zone': 'bottom_center', 'text_on_photo': False, 'note': '✅ 孟菲斯波点 · 黑底+黄波点纹+粉青双色边框照片+顶部斜贴纸标题块；主标黄字落底部黑底区（护脸）'},
    # 素白金线（米白极简大留白；照片窗居中；金色渐隐分界线；底部文字带思源宋 Medium）
    'kinfolk_air':      {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 素白金线 · 字落底部文字带（照片窗外卡纸区，护脸）'},
    # 馆签双框（双线展签框随图自动框色〔确定性〕；顶部信息条；底部文字块下移加深）
    'museum_frame':     {'hero_zone': 'bottom_card', 'text_on_photo': False, 'note': '✅ 馆签双框 · 字落底部展签区（照片窗外，护脸）'},
    # 红格瑞士（去色满幅+红网格径向蒙版〔中心 40% 无网格〕；左下白衬线主标压照片）
    'swiss_red_grid':   {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '红格瑞士 · 左下主标压去色满幅照片（不护脸，需人工核）'},
    # 刊头索引（奶白刊头带 330px+满幅照片；文字全落刊头带〔思源黑 Heavy 刊名+四栏目录〕）
    'super_index':      {'hero_zone': 'top_center', 'text_on_photo': False, 'note': '✅ 刊头索引 · 文字全落顶部刊头带（照片上方卡纸区，护脸）'},
    # 复古电视（深炭底+大圆角照片窗；主标落右下深底非照片区；左上手写英文）
    'retro_tv':         {'hero_zone': 'bottom_center', 'text_on_photo': False, 'note': '✅ 复古电视 · 主标落右下深底（非照片区，护脸）；RGB 故障错位 text-shadow（单元素多层）'},

    # =================================================================
    # 设计语言族 · 彩活四款（2026-09-07，docs/批量设计-彩活四款-设计.md §1 v2 口径）
    # =================================================================
    # 街头小志（照片满幅原色+顶部渐变黑带刊名红块；底部右对齐楷体大字压照片下部）
    'street_zine':      {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '街头小志 · 底部右对齐楷体白字压照片下部（不护脸，需人工核）；拓扑注册填拓08 bottom_right 槽〔v2 修：原拟 bedrock_base 与 hero 落区不符〕'},
    # 双色波普（方案 b 照片原色禁 duotone；底部红块 300px 白字大标+12 波普圆点覆盖照片下部）
    'duo_pop':          {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '双色波普 · 底部红块 300px+右下圆点实际覆盖满幅照片下部（探针闺蜜图即如此且经用户目测定稿；不护脸，需人工核）'},
    # 涂鸦夏日（照片洗白+白色上下渐隐；标题/固定文案/EN 贴纸落洗白渐隐带=压照片）
    'doodle_summer':    {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '涂鸦夏日 · 标题/固定文案/EN 贴纸实际落洗白照片的渐隐带上（底部渐隐带 .88 白保证可读性；不护脸，需人工核）'},
    # 杂拼人物（v3 融合版：蛋窗 605×691 护脸+文字墙落窗外；单人照限定）
    'collage_man':      {'hero_zone': 'bottom_center', 'text_on_photo': False, 'note': '✅ 杂拼人物 · 蛋窗+bottom 文字=护脸（照片居蛋窗内，词墙/大标全落窗外）；单人照限定——多人照质检提示换款'},

    # =================================================================
    # 设计语言族 · 构图三款（2026-09-08，docs/批量设计-构图三款-设计.md §1）
    # =================================================================
    # 折枝杂志（米白纸底+左上文字块+右上竖排小字+花枝+双层斜切照片窗；照片在窗内=
    # 文字/花枝全落留白区，护脸）
    'branch_magazine':  {'hero_zone': 'bottom_center', 'text_on_photo': False, 'note': '✅ 折枝杂志 · 照片在独立斜切窗内（双层嵌套，right:30=探针 A4 源码勘误值，见设计稿 §1.1 勘误注），文字块/竖排小字/花枝全落留白区（护脸）；hero 粗粒度 bottom_center→拓08 bottom_right 槽（street_zine 同槽先例）'},
    # 波普宣言（黄底 Ben-Day 圆点+原色照片窗 76% 高+大红爆炸星破界压照片底缘+黑条星群 12 颗）
    'pop_lichtenstein': {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '波普宣言 · 照片止于 76% 高、黑条不压照片，但大红爆炸星/星群破界压照片底缘=原稿有意构图（不护脸，需人工核；保守策略 T 槽）'},
    # 报纸印刷波普（三段律 13/74/13+半调网点渐隐+原色照片+白网点 overlay）
    'pop_press':        {'hero_zone': 'bottom_center', 'text_on_photo': True,  'note': '报纸印刷波普 · 三段律照片区 74%、底部文字不压照片；白网点 overlay 满铺照片=制版感（不护脸，需人工核；保守策略 T 槽）'},
    # 撕纸手帐（2026-09-09，docs/批量设计-torn_journal-设计.md §1.5）
    'torn_journal':     {'hero_zone': 'top_center',     'text_on_photo': True,  'note': '撕纸手帐 · 主标/副标/竖排轨道全落纸面；气泡/喇叭/T恤/白竖排短语轻搭照片边缘=拼贴语义（避五官需人工核）；无印章'},
    # 展览海报（2026-09-10，docs/批量设计-展览海报-设计.md §1.6）
    'exhibition_poster': {'hero_zone': 'top_center',    'text_on_photo': False, 'note': '展览海报 · 主标/副标参数化 + 左右竖排霞鹜文楷大字/朱砂红展签/底栏三栏=装饰位固定文案，文字全落纸面（text_on_photo=False 护脸安全）；现代画廊语义无印章→几何标贴'},
    # 撕纸破洞窥视（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 16 款）
    'torn_peephole':    {'hero_zone': 'top_center',     'text_on_photo': False, 'note': '撕纸破洞窥视 · 主标/副标/揭语全落牛皮纸封面文字区，照片在破洞内零裁剪完整可见（洞 = 原图等比 contain；撕边恒朝外咬牛皮纸）；不压照片任何像素（text_on_photo=False 护脸安全）；无印章→NO.04 圆戳'},
    # 撕纸双层撕纸（2026-09-10，docs/批量设计-撕纸两款-设计.md §1 · 第 17 款）
    'torn_deckle':      {'hero_zone': 'top_center',     'text_on_photo': False, 'note': '撕纸双层撕纸 · 标题纸片固定右下角（骑线仅轻压照片底部约 6.5%，拼贴语义同 torn_journal）；主标/副标/meta 全落纸片，手记小纸片/牛皮纸条/NO.08 圆戳落灰底（text_on_photo=False 护脸安全）'},
    # 现代网格杂志风（2026-09-16，docs/新款入库批-设计.md §2.1/§2.3 · 第 18 款）
    'modern_spread':    {'hero_zone': 'top_center',     'text_on_photo': False, 'note': '✅ 现代网格杂志风 · 居中主标题（西文 Prata/中文思源黑 Heavy）+ 三段式元数据条全落照片上方，页脚两行落照片下方；内嵌大图无画中画（R1）；文字全落照片区外（text_on_photo=False 护脸安全）'},
    # 东方手记风（2026-09-16，docs/新款入库批-设计.md §2.1/§2.4 · 第 19 款）
    'cultural_journal': {'hero_zone': 'top_center',     'text_on_photo': False, 'note': '✅ 东方手记风 · 居中主标题群（眉标/中文大标/副标）全落照片上方，图注/手记行/年份行全落照片下方；单张卡纸装裱照片（R2 只用一张）；文字全落照片区外（text_on_photo=False 护脸安全）'},
}


def hero_zone_for_genre(genre):
    """返回某流派 hero 真实落区签名 dict；未知 genre 返回 None。"""
    return GENRE_LAYOUT_SIGNATURE.get(genre)


# 载体隐喻流派族（7 款）——用户拍板均不作护脸款（通用风格）；即使其中 3 款
# text_on_photo==False，也不在 face_safe_genres() 里出现（不强绑 face_portrait）。显式排除。
_METAPHOR_NON_FACE_SAFE = {
    'auction_catalog', 'playbill', 'declassified_file', 'lunar_dial',
    'music_manuscript', 'arch_curved', 'viewfinder_ui',
}


def face_safe_genres():
    """返回 text_on_photo==False 的流派集合（满幅脸/满幅主体可用的护脸流派）。

    载体隐喻流派族（7 款）被显式排除——它们是通用风格，不作护脸款（用户拍板）。
    """
    return set(g for g, s in GENRE_LAYOUT_SIGNATURE.items()
               if not s['text_on_photo'] and g not in _METAPHOR_NON_FACE_SAFE)


def validate_layout_consistency(registry=None, signatures=None):
    """校验「流派实际 hero 落区」与「注册表绑定拓扑的 text_zone」是否一致（问题 B 的体检）。

    该检查是**启发式**：把每个流派注册为 primary 的拓扑的 text_zone 与 hero_zone 归为粗粒度
    家族后对比。**它把已知错位当成可检测项暴露，供复核——绝不静默通过。**
    【本库数据的实际暴露结果】：审计修正后 hero 落区一致性**无错位**（bauhaus / slender_zen / stone / lunar_dial 已迁至正确绑定，2026-09-04；B11 已删 nordic——非现存款，仅作 legacy/基线标注）。
    【政策可接受、不报】：本库把 `left` 家族 hero（left_vertical/left_giant/upper_left）与
    `right`/`bottom_left` 拓扑视为可互换（film 的 upper_left、layered 的 left_giant 挂 right_wing
    即属此类），故 film / layered 不会报错——即便 layered 的 ⚠️ 注记提示其 hero 与绑定方向相反。
    返回 dict：
      {
        'ok': bool,                     # 无任何错位
        'mismatches': [{'genre':..., 'hero_zone':..., 'primary_topologies':[...], 'why':...}, ...],
      }
    """
    registry = registry if registry is not None else TOPOLOGY_REGISTRY
    signatures = signatures if signatures is not None else GENRE_LAYOUT_SIGNATURE

    # 粗家族：拓扑 text_zone / hero_zone 各归一类，用于可比对
    _topo_family = {
        'zenith_center': 'top', 'bedrock_base': 'bottom', 'right_wing': 'right',
        'dual_poles': 'top_bottom', 'bottom_left': 'bottom_left',
        'perimeter_orbit': 'edge', 'bottom_right': 'bottom_right', 'matted_gallery': 'card',
        'face_portrait': 'face_edge',
    }
    _hero_family = {
        'top_center': 'top', 'top_or_center': 'top', 'right_vertical': 'right',
        'left_vertical': 'left', 'left_giant': 'left', 'upper_left': 'left',
        'vertical_masthead': 'top',
        'top_and_bottom': 'top_bottom', 'bottom_card': 'card', 'bottom_center': 'bottom',
    }
    # hero 家族兼容哪些拓扑家族（严格：方向一致才兼容，避免"居中 hero 混进边缘拓扑"）
    _compat = {
        'top': {'top', 'top_bottom'},
        'right': {'right'},
        'left': {'right', 'bottom_left'},
        'top_bottom': {'top_bottom'},
        # card（字落下方卡纸）兼容 face_edge（护脸：字只在额顶/发缘/下颌）——specimen 正是拓09 的搭子
        # ☆ 2026-09-01 新增 'edge'：装裱/影格 E（纹饰框流派）绑拓07(沿边)，字落在"装裱边框"的底部卡带
        #   ——这是 framed/装裱构图下 `perimeter_orbit(edge)` 的正当落字方式（非错位），
        #   与既有 film/layered 的 left↔right 互换同属"政策接受"级兼容放松。
        'card': {'card', 'face_edge', 'edge'},
        # bottom（字落底部）兼容三家族——
        #   · bedrock_base（基础）：bedrock_stele（泰山托底）正属此家族；
        #   · ☆ 2026-09-07 彩活四款（docs/批量设计-彩活四款-设计.md §3）：
        #     bottom_right / face_edge 两家族——
        #     - street_zine/branch_magazine（拓08 bottom_right）：hero 签名枚举只有
        #       bottom_center 粒度，实际落点右对齐贴右下角（探针 P1 终图），与拓08
        #       "右下 X55-90%、Y70-90%" text_zone 相符——粗粒度政策接受；
        #     - collage_man（拓09 face_edge）：蛋窗 605×691 居中+文字墙/大标全落窗外
        #       （bottom_center 粒度无法表达"窗内脸+窗外字"的护脸结构），与 specimen
        #       （bottom_card→face_edge）同理，属拓09 正当落字（护脸）。
        'bottom': {'bottom', 'bottom_right', 'face_edge'},
    }

    # 反查：genre -> 注册为 primary 的拓扑列表
    genre_primary = {}
    for tid, e in registry.items():
        for g in e.get('primary_genres', []):
            genre_primary.setdefault(g, []).append(tid)
    genre_primary.setdefault(None, [])

    mismatches = []
    for genre, sig in signatures.items():
        hero = sig.get('hero_zone')
        hfam = _hero_family.get(hero)
        if hfam is None:
            mismatches.append({'genre': genre, 'hero_zone': hero,
                               'primary_topologies': genre_primary.get(genre, []),
                               'why': '未知 hero_zone 家族'})
            continue
        allowed = _compat.get(hfam, set())
        primaries = genre_primary.get(genre, [])
        # 每一注册为 primary 的拓扑，其 text_zone 家族都必须兼容 hero 家族
        for tid in primaries:
            tfam = _topo_family.get(tid, '?')
            if tfam not in allowed:
                mismatches.append({
                    'genre': genre, 'hero_zone': hero,
                    'primary_topologies': [tid],
                    'why': f"hero='{hfam}' 与 topo '{tid}'({tfam}) 的 text_zone 不符",
                })

    # 去重（同一 genre 多拓扑各报一条即可，按 genre 合并首条为 ok 判定）
    ok = not mismatches
    return {'ok': ok, 'mismatches': mismatches}




# ===================================================================
# 2. 查询与校验
# ===================================================================
def get_topology(topology_id):
    """按 id 取拓扑条目；非法 id 抛 KeyError（明确行为，验收③）。"""
    if topology_id not in TOPOLOGY_REGISTRY:
        raise KeyError(
            f"未知拓扑 id: {topology_id!r}。可用 id: {sorted(TOPOLOGY_REGISTRY)} "
            f"（新增请走『必要性 + 普适性』机制，见模块 docstring §1）。"
        )
    return TOPOLOGY_REGISTRY[topology_id]


def validate_registry(registry=None, known_genres=None):
    """校验 registry 完整性（验收①②③的一部分）。

    检查：
      ① 恰好 9 个拓扑，且每条含 REQUIRED_FIELDS 全部字段；
      ② 每个 known_genres 流派都能在 >=1 个拓扑的 primary_genres 找到；
      ③ face_portrait（拓09）primary_genres 必须全部为护脸流派（text_on_photo==False）；
      ④ （④ 的行为由 get_topology / topology_supports 负责，此处不重复校验。）

    返回 dict：
      {
        'ok': bool,
        'topology_count': int,
        'missing_fields': {topo_id: [缺的字段...]},
        'genres_not_primary': [未在任一主流派出现的流派...],
        'unknown_genres': [流现在主/次列表里但不在 known_genres 的 id...],
        'face_portrait_unsafe': [face_portrait 主流派里 text_on_photo==True 的流派...],
      }
    """
    registry = registry if registry is not None else TOPOLOGY_REGISTRY
    known_genres = set(known_genres) if known_genres is not None else set(KNOWN_GENRES)

    missing = {}
    for tid, entry in registry.items():
        miss = [f for f in REQUIRED_FIELDS if f not in entry]
        if miss:
            missing[tid] = miss

    # 收集所有出现在 primary/secondary 的流派
    primary_sets = {tid: set(e['primary_genres']) for tid, e in registry.items()}
    all_primary = set().union(*primary_sets.values()) if registry else set()
    genres_not_primary = sorted(gen for gen in known_genres if gen not in all_primary)

    # 主/次列表里出现的未知流派名（防拼写错误）
    referenced = set()
    for e in registry.values():
        referenced |= set(e.get('primary_genres', []))
        referenced |= set(e.get('secondary_genres', []))
    unknown_genres = sorted(referenced - known_genres)

    # ③ face_portrait（拓09）主流派必须全部护脸（text_on_photo==False）
    face_entry = registry.get('face_portrait')
    face_safe = set(face_safe_genres()) if face_entry else set()
    face_portrait_unsafe = []
    if face_entry:
        face_portrait_unsafe = sorted(
            g for g in face_entry.get('primary_genres', [])
            if g not in face_safe
        )

    ok = (
        len(registry) == 9  # 2026-09-14 拓06 equator_belt 根因否决移除（10→9）
        and not missing
        and not genres_not_primary
        and not unknown_genres
        and not face_portrait_unsafe
    )
    return {
        'ok': ok,
        'topology_count': len(registry),
        'missing_fields': missing,
        'genres_not_primary': genres_not_primary,
        'unknown_genres': unknown_genres,
        'face_portrait_unsafe': face_portrait_unsafe,
    }


# ===================================================================
# 3. topology_supports —— 读图分析器的匹配接口（已实现）
# ===================================================================
# 匹配规则：每个拓扑一组【条件权重表】(predicate, weight, reason)，
# predicate 从 image_features 的客观键取布尔值；命中则该拓扑得分累加 weight。
# 得分 = 加权命中数（每拓扑满分随其规则多少而不同，非校准 0-1 概率；满分上限差异即区分度）。
# 得分最高者即推荐；最高分 < SUPPORT_THRESHOLD → needs_new_topology。
# 规则来源：PROJECT_BLUEPRINT.md §3 的 text_zone/avoid_zone + 拓扑结构库设计.md §2 的
# "适合结构"。**只依赖客观键**（subject_zone/whitespace/brightness/composition/highkey/
# exposure/height_ratio），与 analyze_pixel.py 契约逐键对齐。

# 安全取值器：image_features 可能缺键（智能体合并/手写），一律 .get 兜底，不抛异常。
def _sz(f, key, default='center'):
    return (f.get('subject_zone') or {}).get(key, default)

def _ws(f, key, default=0.0):
    return (f.get('whitespace') or {}).get(key, default)

def _br(f, key, default=128.0):
    return (f.get('brightness') or {}).get(key, default)

def _comp(f, default='centered'):
    return f.get('composition', default)

def _hk(f):
    return bool(f.get('highkey', False))

def _hr(f, default=0.5):
    return f.get('height_ratio', default)


def _f2exp(f):
    return f.get('exposure', 'normal')


TOPOLOGY_RULES = {
    # ---------- 01 正中天穹压顶 ----------
    'zenith_center': [
        (lambda f: _sz(f, 'v') == 'bottom', 0.35, '主体坐低（天顶留白）'),
        (lambda f: _ws(f, 'top') >= 0.40, 0.25, '上方大片留白'),
        (lambda f: _hk(f) or _br(f, 'top') >= 160, 0.25, '顶部亮（死白/天空，墨岚压得动）'),
        (lambda f: _sz(f, 'v') != 'top', 0.15, '主体不在顶（不抢天顶文字）'),
    ],
    # ---------- 02 底部泰山地基 ----------
    'bedrock_base': [
        (lambda f: _sz(f, 'v') == 'top', 0.45, '主体在上'),
        (lambda f: _sz(f, 'h') == 'center', 0.15, '主体居上中（非左/右上）'),
        (lambda f: _ws(f, 'bottom') >= 0.30, 0.25, '下方空（沉底）'),
        (lambda f: _hr(f) < 0.75, 0.15, '主体未撑满全高'),
    ],
    # ---------- 03 右翼悬挂 ----------
    'right_wing': [
        (lambda f: _sz(f, 'h') == 'left', 0.45, '主体偏左'),
        (lambda f: _ws(f, 'right') >= 0.30, 0.35, '右侧空（竖轴落右）'),
        (lambda f: _comp(f) != 'diagonal', 0.10, '非对角线构图'),
    ],
    # ---------- 04 天地对峙双极 ----------
    'dual_poles': [
        (lambda f: _ws(f, 'top') >= 0.25 and _ws(f, 'bottom') >= 0.25, 0.45, '上下皆有留白'),
        (lambda f: _sz(f, 'v') == 'center', 0.25, '主体居中共振'),
        (lambda f: _hr(f) >= 0.55, 0.20, '主体有高度（撑起天地）'),
        (lambda f: _comp(f) == 'vertical', 0.10, '纵向构图'),
    ],
    # ---------- 05 左下沉降锚点 ----------
    'bottom_left': [
        (lambda f: _sz(f, 'h') == 'right' and _sz(f, 'v') == 'top', 0.50, '主体右上'),
        (lambda f: _ws(f, 'bottom') >= 0.30 and _ws(f, 'left') >= 0.20, 0.30, '左下空'),
        (lambda f: _hr(f) < 0.80, 0.20, '主体未撑满全高'),
    ],
    # ---------- 06 四周边框环绕 ----------
    'perimeter_orbit': [
        (lambda f: _sz(f, 'h') == 'center' and _sz(f, 'v') == 'center', 0.40, '主体居中'),
        (lambda f: _hk(f) or _comp(f) in ('centered', 'symmetry'), 0.25, '高调白/居中对称，需框住'),
        (lambda f: _ws(f, 'top') >= 0.20 and _ws(f, 'bottom') >= 0.20, 0.20, '上下留白'),
    ],
    # ---------- 07 右下角印章与手札 ----------
    'bottom_right': [
        (lambda f: _sz(f, 'h') == 'left' and _sz(f, 'v') == 'top', 0.50, '主体左上'),
        (lambda f: _ws(f, 'bottom') >= 0.30 and _ws(f, 'right') >= 0.20, 0.30, '右下空'),
        (lambda f: _hr(f) < 0.80, 0.20, '主体未撑满全高'),
    ],
    # ---------- 08 大画廊卡纸装裱 ----------
    'matted_gallery': [
        (lambda f: _hk(f), 0.40, '高调白（死白/白墙）'),
        (lambda f: _f2exp(f) == 'highkey', 0.15, '曝光高调'),
        (lambda f: _ws(f, 'top') >= 0.30 and _ws(f, 'bottom') >= 0.30, 0.20, '大片留白可装裱'),
        (lambda f: _sz(f, 'v') == 'center', 0.15, '照片居中窗口'),
        (lambda f: _hr(f) >= 0.70, 0.10, '主体撑满（需框住）'),
    ],
}


# 命中阈值：最高分 >= 此值才认定 9 拓扑套得住；否则 needs_new_topology。
SUPPORT_THRESHOLD = 0.50


def topology_supports(image_features):
    """判断 image_features 适合哪个拓扑（第 2 步读图分析器已接入真实匹配）。

    参数 image_features：dict，由 analyze_pixel.py（像素辅）产出、智能体（模型主）
    合并后的客观特征。契约键（详见模块 docstring §1 与 analyze_pixel.py）：
        'subject_zone'  : {'h':'left|center|right','v':'top|center|bottom'}
        'whitespace'    : {'top','bottom','left','right'}  # 留白占比 0~1
        'brightness'    : {'top','bottom'}                 # 0~255
        'composition'   : 'centered|vertical|horizontal|diagonal|symmetry'
        'highkey'       : bool
        'exposure'      : 'highkey|lowkey|normal'
        'height_ratio'  : float
        'semantic'      : {'subject_type':'face_closeup|portrait_double|couple|family|...',  # 可选；模型读图语义提示（主路）
                           'multi_face_dominant': bool}   # 可选；显式"多脸且脸占画面主体"标记
        缺键时安全兜底（.get 默认值），不会抛异常。
        ★ 图"脸占画面主体"时（单脸特写 face_closeup 或 多脸/双人满幅 portrait_double/couple/family/
          group_portrait/friends/multi_face/portrait_multi，或 multi_face_dominant=True），模型应填对应
          semantic → 本函数直接推荐拓09 face_portrait。
          （正因为像素把头发误判成留白、判 center，脸图必须由模型语义显式触发，否则会落错。）

    返回值（dict）：
        {
          'topology_id': <str> | None,          # 命中的拓扑 id（无匹配为 None）
          'confidence' : <float 0~1>,           # 最高拓扑的加权命中数（非校准概率；满分随拓扑规则数而异）
          'reasons'    : [<str>, ...],          # 命中的理由（可解释）
          'needs_new_topology': bool,           # True = 9 拓扑套不住，建议新增
          'candidates' : [{'topology_id','confidence','reasons'}, ...],  # 前 3 名备选
          'face_safe_genres'?: [<str>,...],     # 命中拓09 时附加：text_on_photo==False 的护脸流派
        }

    【无匹配结构的明确行为】——最高分 < SUPPORT_THRESHOLD 时返回
        {'topology_id': None, 'needs_new_topology': True, 'reasons': [...]}，
        并在 reasons 标明该结构 9 拓扑套不住 → 需按『必要性 + 普适性』新增拓扑
        （见模块 docstring §1），**绝不**静默硬塞一个错误拓扑。

    【非法输入】image_features 非 dict → 抛 TypeError 并说明期望的 dict 契约。
    """
    if not isinstance(image_features, dict):
        raise TypeError(
            f"topology_supports 期望 image_features 为 dict（契约见 docstring），"
            f"收到 {type(image_features).__name__}"
        )

    # ---- 语义「脸占满画面主体」直达（单脸特写 / 多脸·双人满幅；问题 A/B 的模型主路显式化）----
    # 像素无法识别"这是脸"（头发平滑被当留白、判 center，正是脸图误判的根源），
    # 故由智能体 read_image 判 subject_type，经可选 'semantic' 键传入。
    # 命中"脸占画面主体"（单脸特写 / 多脸·双人满幅） → 直接推荐拓09 face_portrait。
    # 判定：语义 subject_type 落在面的常见集合（face_closeup/portrait_double/couple/family/...
    # ）或显式 multi_face_dominant is True 即命中前面板，无需像素权重。
    # P0-7：不可遮挡任一五官；只配 text_on_photo==False 的护脸流派。
    semantic = image_features.get('semantic') or {}
    subject_type = semantic.get('subject_type')
    _face_subject_types = (
        'face_closeup', 'portrait_double', 'couple', 'family',
        'group_portrait', 'friends', 'multi_face', 'portrait_multi',
    )
    _is_face_dominant = subject_type in _face_subject_types or semantic.get('multi_face_dominant') is True
    if _is_face_dominant:
        face_safe = sorted(face_safe_genres())
        _single = subject_type == 'face_closeup' and semantic.get('multi_face_dominant') is not True
        scene_desc = '脸部特写/满幅脸' if _single else '多脸同框/双人满幅'
        p0_note = 'P0-7 不可遮挡五官' if _single else 'P0-7 不可遮挡任一五官'
        reason = (
            f'模型判为「{scene_desc}」（{p0_note}）；'
            '基础 8 拓扑会把字压到面部 → 用拓09 大头人像，文字仅落额顶/发缘/下颌，'
            '只配 text_on_photo==False 的护脸流派'
        )
        return {
            'topology_id': 'face_portrait',
            'confidence': 1.0,
            'reasons': [reason],
            'needs_new_topology': False,
            'candidates': [{'topology_id': 'face_portrait', 'confidence': 1.0, 'reasons': [reason]}],
            'face_safe_genres': face_safe,
        }


    scored = []
    for tid, rules in TOPOLOGY_RULES.items():
        score = 0.0
        reasons = []
        for pred, weight, why in rules:
            if pred(image_features):
                score += weight
                reasons.append(why)
        # 得分 = 加权命中数（每拓扑满分随其规则多少而不同，非校准 0-1 概率）。
        # 不做归一化：满分上限差异本身是有用的"区分度"，归一化反而制造跨拓扑同分并列。
        scored.append({'topology_id': tid, 'confidence': round(score, 3), 'reasons': reasons})

    scored.sort(key=lambda x: -x['confidence'])
    best = scored[0]
    candidates = scored[:3]

    if best['confidence'] >= SUPPORT_THRESHOLD:
        return {
            'topology_id': best['topology_id'],
            'confidence': best['confidence'],
            'reasons': best['reasons'],
            'needs_new_topology': False,
            'candidates': candidates,
        }

    return {
        'topology_id': None,
        'confidence': best['confidence'],
        'reasons': [
            f"最高分拓扑 {best['topology_id']} 仅 {best['confidence']}，"
            f"低于阈值 {SUPPORT_THRESHOLD}。该结构 9 拓扑套不住 → "
            f"需按『必要性 + 普适性』新增拓扑（见模块 docstring §1）。"
        ],
        'needs_new_topology': True,
        'candidates': candidates,
    }


# ===================================================================
# 4. 自检（python topology_registry.py 直接跑）
# ===================================================================
if __name__ == '__main__':
    import sys
    import argparse
    import json

    parser = argparse.ArgumentParser(
        prog='topology_registry',
        description='拓扑注册表：`validate`（默认，registry 完整性自检）或 `supports`（挑拓扑）。',
    )
    sub = parser.add_subparsers(dest='cmd')

    # validate（默认子命令）
    sub.add_parser('validate', help='校验 registry 完整性（9 拓扑全字段 + 流派全覆盖 + 护脸校验）。')

    # supports（挑拓扑）
    sp = sub.add_parser('supports', help='按 image_features 挑拓扑（读图链路第 2 步）。')
    sp.add_argument('--features', default=None, help='内联 JSON（键见 docstring）。' )
    sp.add_argument('--features-file', default=None, help='指向 image_features 的 JSON 文件路径。')

    args = parser.parse_args()

    if args.cmd == 'supports':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        if args.features:
            try:
                feat = json.loads(args.features)
            except json.JSONDecodeError as e:
                print('--features 不是合法 JSON:', e)
                sys.exit(2)
        elif args.features_file:
            try:
                with open(args.features_file, 'r', encoding='utf-8') as f:
                    feat = json.load(f)
            except FileNotFoundError:
                print(f'--features-file 不存在: {args.features_file}')
                sys.exit(2)
            except json.JSONDecodeError as e:
                print(f'--features-file({args.features_file}) 不是合法 JSON: {e}')
                sys.exit(2)
        else:
            print('supports 需要 --features 或 --features-file 之一。')
            sys.exit(2)
        res = topology_supports(feat)
        # stdout 已重配为 UTF-8（`sys.stdout.reconfigure(encoding="utf-8")`，见上），
        # 故用 ensure_ascii=False 输出中文（UTF-8 终端/管道可正常读取；GBK 控制台仅显示乱码）。
        print(json.dumps(res, ensure_ascii=False))
        sys.exit(0)

    # 默认 validate
    report = validate_registry()
    print('拓扑数量:', report['topology_count'])
    print('字段缺失:', report['missing_fields'] or '无')
    print('未入任一『主流派』的流派:', report['genres_not_primary'] or '无')
    print('未知流派名:', report['unknown_genres'] or '无')
    print('face_portrait 不护脸的流派:', report['face_portrait_unsafe'] or '无')
    # 问题 B 体检：流派 hero 落区 vs 注册表绑定拓扑
    lc = validate_layout_consistency()
    if lc['mismatches']:
        print('⚠️ hero 落区错位（复核）:')
        for m in lc['mismatches']:
            print(f"  - {m['genre']}: hero={m['hero_zone']} → {m['why']}")
    else:
        print('hero 落区一致性: 无错位')
    print('VALID:', 'OK' if report['ok'] else 'FAIL')
    if not report['ok']:
        sys.exit(1)
