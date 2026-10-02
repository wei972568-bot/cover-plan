# cover-plan — 封面计划（Photo → Editorial Cover）

## When to Use
用户给一张照片（+ 可选标题/副标/日期/地点），要把它做成"刊物级封面"。
识别触发词：封面、做成封面、出封面、cover、套个版式、排版成书封。

## ⚠️ 前置：需要视觉模型 + 能跑 Python 出图
本 skill 走"读图→挑拓扑→定制"链路，前提两条都要满足：
1. **视觉模型**：第 1 步要看图，智能体所在模型必须支持 `read_image`（视觉）。
   - 能看图 → 继续。
   - `read_image` 报错（纯文本模型如 DeepSeek V4 / GLM-5）→ **明确提示用户**："当前模型不支持识图，请切换到支持视觉的模型（如 Kimi K3 / Qwen3.8 / GLM-5.3-Flash）再试。"
2. **运行环境**：能跑 `python scripts/analyze_pixel.py` / `topology_registry.py` / `engine_v2.py`（PIL + 本地字体 `D:\dsh\fonts`），并有 chrome 截图（`screenshot.py`）。
   - 部分缺失 → 告知用户："像素分析/出图需 Python + 截图，当前只做识图建议。"

## 方法论：不是套模板，是读图定制

> **灵魂**：先读图识别客观特征 → 推导排版铁律 → 挑拓扑 → 按图定制。不是"28 套固定版式套参数"。
> **拓扑 = 骨架**（文字落哪/结构）；**流派 = 骨架上的微调**（字体/配色/纹饰/避坑）。同一拓扑能微调出多套流派。

### 第 1 步 · 识图（模型为主 + 像素为辅）→ 合成 image_features
**A. 模型识图（主）**：`read_image` 看照片，用自然语言记录**定性信息**（供第 3 步选流派）：
- 题材：人物 / 佛像 / 文物 / 风景 / 建筑 / 花鸟 / 街拍 / ...
- 主体位置印象 / 占比 / 是否脸部特写
- **昼夜 / 明暗 / 天气 / 季节 / 场景**（⚠️ 先锁客观事实，再推情绪——P0-9 图文一致，别"白天配夜色文案"）
- 色调 / 气质：胶片感 / 复古暖 / 暗调 / 亮净 / 黑白 / 清冷 / 浓艳 ...

**B. 像素测量（辅）**：跑 analyze_pixel.py 得**客观数值**（契约键，供挑拓扑）：
```
python scripts/analyze_pixel.py --photo "<照片路径>" --json-out <临时>.json
```
输出 `image_features`（键严格对齐 `topology_registry.py` 契约）：
| 键 | 类型 | 含义 |
|---|---|---|
| `subject_zone` | `{h,v}:left/center/right, top/center/bottom` | 主体方位 |
| `whitespace` | `{top,bottom,left,right}: 0~1` | 各边带留白占比 |
| `brightness` | `{top,bottom}: 0~255` | 上下平均亮度 |
| `composition` | `centered/vertical/horizontal/diagonal/symmetry` | 构图倾向 |
| `highkey` | bool | 是否高调白（死白/白墙） |
| `exposure` | `highkey/lowkey/normal` | 曝光倾向 |
| `height_ratio` | float | 内容高度占比 |
| `semantic` | `{subject_type: face_closeup\|...}`（可选，A 模型填） | 语义提示；**满幅脸必须填 `face_closeup`**（像素把头发误判成留白、判 center，识别不出"这是脸"）|

**C. 合并**：A（定性）+ B（定量）合成完整认知。B 的定量键直接喂 `topology_supports`；A 的定性信息在决定"选哪个流派"时起主导作用。**图是"脸满幅特写"时把 `semantic.subject_type='face_closeup'` 并入 image_features**（这是模型主路的显式入口）。

> **识图入口可替换**：第 1 步被封装成函数。当前用 本体 `read_image` + `analyze_pixel`；将来接独立多模态 API 时，只替换该函数内部（识图结果字段不变），流程无需改。

### 第 2 步 · 挑拓扑（topology_supports 建议 + 模型定性裁决）
跑：
```
python scripts/topology_registry.py supports --features-file <临时>.json
```
返回 `topology_id + confidence + reasons + candidates`；若 `needs_new_topology: True` → 说明 9 拓扑套不住，按"必要性+普适性"考虑新增（**绝不静默硬塞**）。

**用模型定性信息做最终裁决**（topology_supports 是建议，不是你照抄）：
- 结合 A 的题材/构图印象，在 candidates 里挑一个；分值 + reasons 供解释。
- A 与 B 冲突（如像素说"居中"，模型看主体明显偏左）→ 综合判断，别盲信像素。
- **满幅脸特写** → 把 `semantic.subject_type='face_closeup'` 传给 supports，它直接推**拓09 大头人像**（唯一不压脸的骨架，附 `face_safe_genres`）。
- `needs_new_topology` → 向用户说明该结构 9 槽位套不住、建议新增（或先收敛到最接近拓扑）。

**拓扑速查**（每拓扑 = 主体结构特征 + 文字落区）：
| 拓扑 | 适合结构 | 文字落区 |
|---|---|---|
| 01 正中天穹压顶 | 主体坐低、顶死白/大片上空 | 正上居中巨大字 |
| 02 底部泰山地基 | 主体居上中、下方空 | 正下居中 100-140 沉底 |
| 03 右翼悬挂 | 主体偏左、右侧空 | 右侧竖轴 |
| 04 天地对峙双极 | 上下皆白、主体居中拉高 | 顶部+底部巨字对峙 |
| 05 左下沉降锚点 | 主体右上、左下空 | 左下 |
| 06 四周边框环绕 | 主体居中、需框住 | 贴沿四周 |
| 07 右下角印章与手札 | 主体左上、右下空 | 右下印章/手札 |
| 08 大画廊卡纸装裱 | 高调白、需装裱 | 照片居中 + 下方白卡 |
| 09 大头人像 | 脸满幅/头部占大、直视、几乎无留白 | 仅额顶发际/两侧发缘/下颌（护脸；只配 text_on_photo==False 的流派）|

> **⚠️ 2026-09-14：原「06 水平居腰封/横带」已整体移除**（用户拍板根因否决：正视图中横贯照片不可行）——现为 **9 拓扑**（基础 8 + 拓09 大头人像），编号顺延如上。`topology_registry.py` 注册表/匹配规则/兼容映射已全删，`topology_supports()` 不再建议任何"中部横贯"骨架。

### 第 3 步 · 选流派（按"真实 hero 落区"判，不看拓扑元数据）
> ⚠️ 关键（实测发现）：注册表"拓扑↔流派"绑定**会错位**——nordic（2026-09-05 已下线，此处保留为历史案例）绑定拓07("沿边")但 hero 实际**居中**会压脸；stone 绑定拓08(右下)但竖排 hero **落在左侧**。**所以别用"选中拓扑的 primary_genres"当选择依据，要用流派【真实 hero 落区】判"这流派字落哪、会不会压主体/护脸"。**（权威接口：`topology_registry.py` 的 `hero_zone_for_genre()` / `face_safe_genres()`。）

**怎么挑（4 步）**：
1. 先按 A 的题材/气质/昼夜，锁 2-3 个候选 genre；
2. 查每个候选的 `hero_zone` + `text_on_photo`（下表）；
3. **筛掉会压主体/压脸的**：主体满幅或有脸 → 只留 `text_on_photo==False`（specimen），其余全弃；主体偏一侧 → 选 hero 落在空侧、避开主体的那个；
4. 用 A 的定性信息（题材/诗文）定 title/文案。
   4.5. **无"经典款/冷门款"标签（B17，最根本）**——**60 款全是潜在选择**，心里不要给款贴"经典/冷门"标签（贴了要么只用经典→固化/错配，要么只避经典→矫枉过正）。**选款唯一依据 = "这图是什么（气质/主体/位置）→ 哪个版式配它"**；匹配（文字落区不压主体 + 版式气质贴合图）→ 潜在选择，不匹配（压主体/气质违和）→ 排除。**"防固化/多样" = 不同图自然匹配不同版式**（因为图特质不同），**不是"刻意挑不同/挑剔款名"**。一句话：**心里只有"这版式配不配这图"，没有"这经典/冷门"**。
5. **选"骨架"而非固定配方（B20，关键）**——**别潜意识套"顶字×2+卡纸×3+胶片×1"这套配方**。选款 = 判图 → **选"骨架类型"**（这图适合哪种版式结构：**巨字压场 / 横贯打断 / 整体卡纸体 / 竖轴 / 隐喻载体（照片变身物）/ 长条竖排 / 居中大字**...），**每张图用不同骨架**（因图而异）。**自检**：出完 9 宫格，若发现"又是顶字+卡纸+胶片" → **强制换骨架**（重选）。别让"换款名换文案"掩盖"骨架没变"。


5. **文案是图的一部分（B16，作品级创意，非看图说话）**——**先判图片气质/情绪 → 配"有档次/审美/意境"的文案**（不是"古巷/金獸/車站"这种描述，而是「鎏金歲月」「巷深不知處」式**意象/留白/隐喻/张力**）。**图文一体、气质统一、互相成就**——好文案体现图片的档次与审美。
  - **九宫格跨文案（B15）**：9 款**各配不同创意文案**（每款用最配它的），**既比款式也比文案**；不要 9 张同一句文案。
  - **跨页已用池（B26，2026-09-25 用户裁定；同日 a 降档）**：**已选款**（进 README 精选的）必须跨页避开；**陪跑款允许跨页复用**（72 格 > 60 款的数学必然，第 7 页起生效 —— 用户拍板 a）。选款依据仍是**本图** 4 维+构图语言+主体坐标避让（脸/月/杯等主体压盖为 P0 级，渲后 9B 逐张复检）；页内 9 异是下限，跨页因图而异是本意（反例：三页同池/整页平移旧稿 = 被抓包"不是按图挑的"）。顺带避开：质检 ✗ 款（imperial/oriental_plain_paper）；**单人限定款（collage_man）在人像图上恰恰可用**。
  - 标题**避歧义**：不用含 `·`/超长易断行的（B1），保证单行大字款不折行。
  - **词必须对图，禁编造**（2026-09-24 用户裁定）——**图中没有的真实城市/时间/数字一律不写**（反例：图是无名墙配 `SHIBUYA`、随手 `DAWN 0540`、哪国的图都 `Café de Paris`）；`--date` 随图的季节（冬图 01.18、夜图 11.03，不是统一今天），`--location` 用**意象化栏目名**（WINTER ISSUE / 北岭手记 / STILL LAKE）而非真实地名。
  - **反大白话：禁"图片内容说明书"**（反例：`静物 · 陶与枯枝` / `咖啡 · 可颂 · 窗光`——把画面上的名词抄一遍 = 看图说话复读机）。文案先回答**"这张图在表达什么"**（对峙？光的行进？某个动作？色彩呼应？双关的可能？）→ 再为它落字：可动作叙事（`倚墙记`）、可拟人（`LIGHT WALKS THE KEYS`）、可双关（`器与隙`——窗隙的光×冰裂纹）、可抓呼应（图里三处紫 → `PURPLE SEASON`）。
  - **质量红线（用户原话）**：`文案不好，用户就会觉得这工具弱智`——文案是用户对工具水平的第一判据，**每条文案交付前自问：它读的是"图的意义"还是"图里有什么"？**


**出多款对比（9 宫格）—— 这是默认流程，且必须"因图定制、防重复"**：
> 用户要求："出 9 宫格才能展示引擎丰富度，但要因图多样、不许重复/雷同"。**单张不足以看全样式；9 宫格是标准呈现。**

**A. 一定要按"图标签"选款，跨气质、防重复**（**严禁偷懒套固定清单**）：
 1. 读图先判【主体位置 / 色调 / 气质 / 题材】4 维度 + **构图语言辅助维**（这图是框中框？引导线？负空间？边角/留白式？——查《美术规范》§8 附录"构图语言→拓扑/款映射"得候选参考；**映射是线索不是规则**，最终仍按 2-4 步的落区/护脸/气质判断定夺）；
  2. **按这 4 维从 60 款里筛候选集**（示例：冷极简→kinfolk_air/museum_frame/gallery_centered_axis/film…；萌宠暖调→卡纸/顶部大字/右竖…），**不是用一个固定 9 款清单**；
3. **防重复硬规则（必须逐条满足）**：
   - 9 款须**跨 ≥4 个气质**（天幕大字/竖轴文人/极简留白/胶片媒介/期刊大刊/物格载体/装裱卡纸…），**不许 9 个同气质/雷同**；
    - **同版式族最多 1-2 个（B7 教训，关键）**：**9 宫格里不许同一个"版式族"出现 ≥3 个**——引擎 60 款里很多款是**同一版式族的不同 id**（如卡纸族 gallery_frame_warm/gallery_ice_crack 都"画面+卡纸+标题"仅颜色边框微调；画框族、影格族同理）。**9 款必须跨"真正不同版式"**，同一版式族 ≤1-2 个。**判断版式族**：看"文字落区结构 + 是否独立卡纸/画框 + 主体呈现方式"是否雷同，**不能只看款 id 不同就当作不同款**（pop_lichtenstein/pop_press 同血统但版式结构不同=不同族，9 宫格同屏 ≤1 的既有规则沿用）。

   - 每款 `hero_zone` 须**避开主体**（P0-7：有脸/满幅主体→只留 `text_on_photo==False` 护脸款）；**且必须逐款用 `hero_zone_for_genre()` 验证**，不能凭感觉——**⚠️ 历史教训（B6 实例，已根治）：中部横贯款（`equator_belt` 拓扑，原绑定 piercing/horizon）在"主体居中/居腰"的图上必横贯遮主体；该拓扑已于 2026-09-14 按用户拍板整体移除、piercing/horizon 于 2026-09-05 下线，现役 60 款中已无 hero_zone=middle 的款**（bauhaus 真实落区是 top_or_center，勿再按"腰封款"理解）；
   - **文字落区 by 主体位置（硬判据，实测有效，图6夜景验证）**：
     * **主体在上中部**（宝塔/山/上探物）→ 用 **bottom_card / bottom_center 款**（specimen/dark_contact_print/auction_catalog/bedrock_stele + 装裱/设计语言族 bottom_card 款如 gallery_centered_axis/kinfolk_air/museum_frame；⚠️ stamp/amber_gallery/monochrome_noir/letterbox_gold/cinemascope 已于 2026-09-05 删除）——**文字落底，避开上部主体**；**禁用 top_center 款**（会压宝塔/上主体）。
     * **主体在下部**（底部坐物/展台）→ 用 **top_center 款**（字落顶）；禁用 bottom 款。
     * **主体居中 / 有水平横带**（地平线/岸树/倒影带）→ **禁用中部横贯款**（`equator_belt` 拓扑已于 2026-09-14 整体移除、piercing/horizon 于 2026-09-05 下线，**现无此类款**；bauhaus 实为 top_or_center）；用 bottom_card 或上下避让款。
     * **满幅脸/满幅主体** → 只留 `text_on_photo==False` 护脸款（specimen/装裱F族）。
     * **人像特写（脸占比大但有安全区）**——**关键修正（B9+用户2次纠正，别默认卡纸保守）**：**先判"脸占画面比例"和"安全区在哪"**。脸在上半部、**下半身/背景是安全区** → **优先用"文字落中下部安全区"的字大款**（silhouette/deep_interlock/stone 竖排/zen 等），**利用安全区放大字、版式多样**；**不要默认回退卡纸族**（specimen/gallery_centered_axis 等 bottom_card "画面+底部卡纸"版式单一）。只有**脸+主体几乎满幅、无安全区**（真大头特写）才全用护脸卡纸款。

   - 视觉模型对"文字带是否压到细景物（树/水纹/塔尖）"精度有限 → **以 `analyze_pixel.py` 的 subject_zone（top/bottom/center）+ 定性读图**定"主体在上下中哪个区"，再按上面判据定文字落区，**不凭感觉**。
   - **与上一张图的 9 款重叠 ≤2 个**（防"同一批款换照片"——这是用户指出的核心问题）；
   - **若你察觉"上一轮就是这几个款"→ 强制重新按标签筛**（换一批款），不是复用。
4. 给用户成品时**逐款说明**"为什么适合这张图的哪个标签"（强制解释，能暴露"套模板"）。

**B. 诚实边界**：若两张图确实同气质（都极简/都古风），"重叠≤2"可放宽但**仍须跨气质**，且逐款说明差异；**绝不**因为"省事"复用上一批款。


**GENRE_LAYOUT_SIGNATURE（实际 hero 落区 + 是否压照片）**：
| genre | hero_zone | text_on_photo | 一句气质 |
|---|---|---|---|
| zen | right_vertical | True | 东方泼墨竖排+印 |
| slender_zen | vertical_masthead | True | 日系清秀手札 |
| film | upper_left | True | 胶片齿孔 |
| layered | left_giant | True | 压底穿插巨字居左 |
| pulip | top_center | True | 先锋大刊 |
| monumental | top_center | True | 君临天幕 |
| nocturne | top_center | True | 时尚夜曲 |
| imperial | top_center | True | 汉唐金石 |
| blue_note | top_center | True | Blue Note 黑胶 |
| stone | left_vertical | True | 金石碑拓竖排落左 |
| specimen | **bottom_card** | **False** | 科考档案（字落下方卡纸，**唯一不压照片**）|
| bauhaus | top_or_center | True | 包豪斯几何 |
| ~~nordic~~ 已下线 | — | — | 2026-09-05 删除，勿再选（原北欧极简，hero 居中会压脸）|
| dual_portals | top_and_bottom | True | 天地双极 |

> **满幅脸 / 满幅主体**：所有 `text_on_photo==True` 的流派都会把字压到主体上。此时**只选 `text_on_photo==False`（specimen）**；若嫌档案卡冷，告知用户"满幅脸需卡纸流派(拓08/09)，或换有留白的构图"。**P0-7 优先于风格。**

**每拓扑可挑的已实现 genre**（**只作兜底线索，非选择依据**——选择看上面的 hero 落区；⚠️ 权威清单见 `docs/美术规范.md`，此处拓02/05 已补上）：
| 拓扑 | 优先（已实现） | ⚠️ 无专属时的就近回退 |
|---|---|---|
| 01 zenith_center | pulip / monumental / nocturne / imperial / blue_note / bauhaus / slender_zen / torn_journal / exhibition_poster … | — |
| 02 bedrock_base | **bedrock_stele** / lunar_dial / script_bottom / cinzel_bottom / pop_lichtenstein / pop_press … | — |
| 03 right_wing | zen / film / layered / stone / silhouette / deep_interlock / slender_zen / oriental_plain_paper … | — |
| 04 dual_poles | dual_portals / french_elegance（2026-09-14 微调批2 −elegance_yeseva） | — |
| 05 bottom_left | **light_leak** | — |
| 06 perimeter_orbit | 装裱/影格 E 族：french_par_avion / art_deco_gatsby / nordic_meander / film_rsx_sprocket / par_avion_marcellus（+ 别名 french / gatsby） | — |
| 07 bottom_right | street_zine / branch_magazine | — |
| 08 matted_gallery | specimen + 装裱 A/B/C 族 + auction_catalog | — |
| 09 face_portrait | **specimen** + 装裱/影格族护脸款（`face_safe_genres()` 现役 22 款，如 specimen/dark_contact_print/gallery_centered_axis/gallery_frame_warm/gallery_ice_crack/french_par_avion/art_deco_gatsby/nordic_meander/film_rsx_sprocket/par_avion_marcellus 等；⚠️ amber_gallery/white_polaroid/letterbox_gold 2026-09-05 已删）| — |

> ⚠️ **2026-09-14 拓扑编号重排**：原「06 水平居腰封/横带」已整体移除，上表 06–09 为**顺延后的新编号**（原 07/08/09/10 → 现 06/07/08/09）。本表仅列代表款、**非穷举**；权威清单见 `scripts/topology_registry.py` 与 `docs/美术规范.md` §2。

> 🆕 **装裱/影格流派族**（`scripts/matting_configs.py` + `matting_engine.py`，`--genre` 可调 **13 款**〔2026-09-05 真删 24 款后 14 + 字体驱动 5；2026-09-14 −fashion_vogue → 18；2026-09-14 微调批2 −5 款 → 13，详见《美术规范》§3.2〕）：其中 **F 窗式/B 宝丽来/C 影格/E 纹饰** 是 `text_on_photo==False` 的**护脸款**（满幅脸可用），**D 顶栏式**（french_elegance/oriental_plain_paper；~~fashion_vogue~~ 2026-09-14 用户拍板彻底删除；~~swiss_grid/vinyl_record~~ 2026-09-05 删除）是 `text_on_photo==True`（文字压照片、仅避五官，**不标护脸**，需人工核）。**D+ 底部落字家族**（hero=bottom_center，text_on_photo==True，不护脸需人工核；~~vogue_bottom~~ 2026-09-14 微调批2 用户拍板彻底删除）：**script_bottom / cinzel_bottom**（2026-09-05 §5：手账甜美=BodoniModa 76px+✦✦✦点缀+斜体副标〔#18：字体+字号继承自原 vogue_bottom〕/ 罗马碑刻=CinzelBold+金线金菱点缀+#efe6cf 副标；家族共用 `_render_bottom` 参数化模板：title_spacing/bottom_ornament/sub_italic/sub_color 四键 + 统一渐变 rgba(0,0,0,.82)→.52@30%→透明45%；**满幅人像+头顶无留白时优先选本家族**，顶栏族压头部的解法）。装裱族画幅按源图比例 5 档自适应（3:4→900×1200 / 4:3→1200×900 / 16:9→1200×675 / 9:16→675×1200 / 1:1→1080×1080），必须裁时用 `--photo-focus-y 0-100` 控制取景（0=保顶）。选流派按 `hero_zone_for_genre()` / `face_safe_genres()`。详情见 `docs/装裱影格流派设计.md`。
>
> **B24 双层框款**：装裱族 **5 款**已带照片白内框（`photo_border`，与卡纸外框+框间留白成"双层框"）= gallery_centered_axis / art_deco_gatsby / french_par_avion / par_avion_marcellus / french_elegance（2026-09-05 真删 24 款后由 15 款收敛；2026-09-14 微调批2 −elegance_yeseva；`gallery_frame_warm` 以 `outline_style` 外框线双层）。**选款**：图需"装裱感/高调白/需框住/照片被白框装裱" → 优先这些双层框款。
>
> **B23 法式规避头部款**：`french_elegance`（人物特写/大头像首选）——**顶部英文大字偏上/左上 + 右上 ISSUE_04 红标 + 底部中文条带 + 头部区（中上）留空**，规避人物特写头部。**选款**：人物特写/脸占比大的图，想用"文字叠照片的分层大刊"样式但要**避开头部** → 选它（不选会压头顶的 `fashion_vogue`——该款已于 2026-09-14 按用户拍板彻底删除，此处仅存历史对照）。文案映射：`--title`→顶部英文大字、`--sub`→底部中文条带、`--date/--location/--lens`→顶部注脚。
>
> 🆕 **载体隐喻/UI叠层流派族**（`scripts/metaphor_configs.py` + `metaphor_engine.py`，`--genre` 可调 **7 款**）：auction_catalog(拍卖图录)/playbill(剧场节目单)/declassified_file(解密档案)/lunar_dial(月相历法盘)/music_manuscript(乐谱手稿)/arch_curved(拱顶弧线)/viewfinder_ui(相机取景器)。**均为通用风格、不进 face_safe**（文字按"物"解剖落位，非护脸设计；text_on_photo=True 的 4 款满幅脸需人工核）。选流派亦可按 hero_zone_for_genre()。详情见 `docs/载体隐喻流派设计.md`。
>
> 🆕 **蓝图补齐流派族**（`scripts/blueprint_configs.py` + `blueprint_engine.py`，`--genre` 可调 **6 款**〔2026-09-05 -piercing -horizon 下线后〕）：light_leak(漏光日杂)/deep_interlock(深度咬合)/draping(悬垂垂落)/silhouette(身形环绕)/bedrock_stele(泰山巨碑)/midnight(暗夜黑胶)。**均 text_on_photo=True**（文字压照片，**不进 face_safe**，满幅脸需人工核）。补全蓝图 **21 概念**（13 直出 + 2 装裱别名 + 6 新增；原始 28 套目标减 nordic〔B11〕与 piercing/horizon/4 别名〔2026-09-05〕后现役 21）。详情见 `docs/蓝图补齐流派设计.md`。
>
> 🆕 **设计语言流派族**（`scripts/design_configs.py` + `design_engine.py` + `design_templates_b.py`，`--genre` 可调 **19 款**，2026-09-06 六款 + 2026-09-07 彩活四款 + 2026-09-08 构图三款 + 2026-09-09 撕纸手帐 + 2026-09-10 展览海报 + 撕纸两款 + 2026-09-15 新款入库批两款 · 第 5 族 · 探针定稿整版语义）：pop_halftone(孟菲斯波点)/kinfolk_air(素白金线)/museum_frame(馆签双框·框色随图自动)/swiss_red_grid(红格瑞士)/super_index(刊头索引·四栏目录参数化)/retro_tv(复古电视·RGB 故障字)/**street_zine(街头小志·楷体白字+箭头指右上)**/**duo_pop(双色波普·方案 b 照片原色+12 圆点)**/**doodle_summer(涂鸦夏日·洗白渐隐+三朵云)**/**collage_man(杂拼人物·蛋窗+词墙，单人照限定)**/**branch_magazine(折枝杂志·米白纸底+花枝 SVG+双层斜切照片窗，护脸)**/**pop_lichtenstein(波普宣言·黄底 Ben-Day 圆点+大红星破界+星群 12 颗)**/**pop_press(报纸印刷波普·三段律+半调网点渐隐+白网点 overlay)**/**torn_journal(撕纸手帐·四层纸纹底+逐字微旋转主标朱红强调+照片直撕·深咬口撕边〔2026-09-25 裁定：照片撑满撕口、取消白边装裱环带〕+14 件涂鸦拼贴，日期全款唯一)**/**exhibition_poster(展览海报·纯白画布+左上红方块页眉徽标+居中主标思源宋 Heavy+左右竖排霞鹜文楷大字+朱砂红展签+底部三栏信息条，护脸安全)**/**torn_peephole(撕纸·破洞窥视·牛皮纸封面+零裁剪 contain 破洞〔承诺对象=洞内容器矩形，4 锋刺为装饰性撕口允许越出〕+撕边恒朝外+洞缘白纤维毛边+4 根不对称锋刺+双胶带+NO.04 几何编号，护脸)**/**torn_deckle(撕纸·双层撕纸·灰底+大毛边照片〔同种子同号锯齿严格内缩=撕口白纤维〕+骑线标题纸片〔仅压照片底 6.5%〕+左下手记纸片+骑线 NO.08 圆戳+牛皮纸条+单胶带，护脸)**/**modern_spread(现代网格杂志风·暖亚麻底 #D6CEBB+外框线系统+居中双层主标〔西文 Prata/中文思源黑 Heavy〕+三段式元数据条+内嵌大图〔1px 细框，无画中画〕+页脚两行，护脸)**/**cultural_journal(东方手记风·暖纸纹底+居中标题群+单张卡纸装裱照片+手绘箭头/做旧邮戳/凹压钢印 SVG+手写注记+年份行内联 SVG 双三角标记，护脸)**。护脸 12 款（kinfolk_air/museum_frame/super_index/retro_tv/collage_man/pop_halftone〔v3 黑底贴纸款〕/branch_magazine/**exhibition_poster**/**torn_peephole**/**torn_deckle**/**modern_spread**/**cultural_journal**，top=False）；swiss_red_grid/street_zine/duo_pop/doodle_summer/pop_lichtenstein/pop_press/torn_journal 不护脸（需人工核）。思源黑 Heavy、ZhuoKaiKai（清松手写体1）主标款缺字自动思源宋兜底（font_guard）；构图三款起固定装饰文案走 fg_texts **dict 形态**（按文案自身 font 逐字预检）。collage_man 词墙支持 `--words "词1,词2"` 注入用户词。**实现契约与逐款终值**见 `docs/批量设计-新设计语言六款-设计.md` §1 + `docs/批量设计-彩活四款-设计.md` §1 + `docs/批量设计-构图三款-设计.md` §1 + `docs/批量设计-torn_journal-设计.md` §1 + `docs/批量设计-展览海报-设计.md` §1 + `docs/批量设计-撕纸两款-设计.md` §1 + `docs/新款入库批-设计.md` §1；样张 `examples/_design_new/`。

> 拓02（主体在上、下方空）→ **specimen**（大照片窗+底部档案卡）或 **dual_portals**（上下巨字）。
> 拓05（主体右上、左下空）→ **stone**（竖排标题落左）或 **specimen**。

### 第 4 步 · 定制出图 → 截图 → 输出
```
# HTML（在项目根目录跑）
python scripts/engine_v2.py \
  --photo "<照片绝对路径>" --genre <选定的genre> \
  --title "<标题>" --sub "<副标>" --date "<日期>" --location "<地点>" \
  --out "cover_<genre>.html"
# （可选）覆盖固定装饰文案：上述命令后追加 --fg-texts "right_name=见山;f_title=冬之衣·混凝土展"（仅 exhibition_poster / torn_deckle 消费，键名表见下）

# 截图成 JPG（任何 headless Chrome 都行）
chrome --headless --screenshot=cover_<genre>.png --window-size=900,1200 cover_<genre>.html
```
- **固定装饰文案注入 `--fg-texts`**（格式 `key=词;key2=词2`：分号分隔、键名 = config `layout.fixed` 键、值可含中文与空格但不含分号；未知键名打印警告并丢弃；只改本次出图、不动 config 默认词；标「兜底」的键在对应参数有值时被参数顶掉、注入不渲）：
  - **支持范围（2026-10-02 扩面：原 2 款白名单 → 能力判定）**：凡 config 声明了 `layout.fixed` 的款都可注入，现役 5 款：
  - **exhibition_poster（14 键）**：`badge_logo` 左上徽标馆名英文 · `badge_sub` 徽标下行英文 · `left_meta_top` 左翼上注记 · `left_name` 左翼竖排大字人名 · `left_role` 左翼竖排小字身份 · `left_meta_bot` 左翼下注记 · `right_name` 右翼竖排大字人名 · `right_role` 右翼竖排小字身份 · `right_tag` 右翼朱砂红竖排展签 · `f_title` 底栏左·展览标题 · `f_desc` 底栏左·展览副描述 · `f_hours` 底栏中·开放时间（含休馆日） · `f_venue` 底栏右·展馆（兜底：`--location` 有值渲 location） · `f_adm` 底栏右·票务信息
  - **torn_deckle（6 键）**：`lead_en` 标题纸片英文引题（兜底：`--sub` 有值渲 sub） · `micro` 标题纸片微标行（兜底：`--date` 有值渲 date） · `note` 左下手记纸片中文句 · `note_meta` 手记纸片元数据行 · `stamp` 骑线圆戳编号 · `strip` 左下牛皮纸条文案
  - **torn_peephole（3 键）**：`sub` 英文副题 · `lead` 破洞口手记中文句 · `micro` 微标行
  - **modern_spread（5 键）**：`meta_mid` 中段元数据行 · `feat_bold` 特稿粗标 · `feat_thin` 特稿细标 · `issued` 期号标签 · `deck` 导语行
  - **cultural_journal（10 键）**：`eyebrow` 眉标英文 · `sub` 副标 · `caption` 图注英文 · `note_en` 手记英文 · `note_cn` 手记中文 · `postmark_city` 邮戳城市 · `postmark_country` 邮戳国家 · `emboss_l1` / `emboss_l2` 钢印两行
  - ⚠️ **默认词义务与预检边界（2026-09-25 审查补充 · 2026-10-02 扩款）**：exhibition_poster / modern_spread / cultural_journal 的默认装饰词是**引擎占位词**，多半含真实或具体实体（TOKYO / KYOTO / 安藤忠雄 · JIANGNAN 水乡 · 古镇 GUZHEN 等，缺省渲染保留为契约）——**图中没有的实体一律 `--fg-texts` 按图覆盖**（与「词必须对图」同口径）；注入值走 fixed 装饰位**不参与缺字预检**（无兜底 span），生僻字可能缺字直渲——常规用字无虞。
- 想让"流派布局"贴合某个非默认拓扑 → 可加 `--topology <id> --material <mat>`（engine 支持，但**默认即最优**，非必要不加）。
- 给用户成品图路径 + 说明用了哪个 genre / 为什么（识图依据）。想换风格 → 问用户换 genre / 标题 / 副标。

## 字体（渲染层用字 · 2026-09-25 入册）

- **字体目录**：各引擎 `FONTS_DIR` 常量（本机 font_guard 记录 = `D:/dsh/fonts/`，300+ 款）—— **机器相关**，clone 后按 `scripts/` 内常量调整。@font-face 以 `file:///` 绝对路径注入 → **渲染机必须有字体文件**；成品 jpg/png 已固化不依赖，换机器打开 html 才依赖（**默认不内嵌**）。
- **`--embed-fonts` + `--embed-photo`（方案 A · 2026-09-25 用户拍板，同日补齐照片）**：字体按**本页用字**子集化为 **woff2 base64**（fontTools subset + brotli，同参字节确定，9 款 ~360KB）；照片 `img file://` → **data URI**（mimetypes 定 mime、percent 路径 unquote 还原）。**两开关合用 = html 全自包含**——端到端实测全页 `file:///` 残留 0（字体 8/8 + 照片 1/1，整页 ≈2.1MB），分发到裸机器浏览器直接看。边界：**渲染机仍需有字体文件**（子集在其上做）；单项失败保留原引用+告警不阻断；默认关（零回归，关时字节 SAME）。
- **在用 22 款**（`DESIGN_CONFIGS`+`GENRE` 的 `fonts` 字段全量统计）：
  | 组 | 字体（括号=挂载款数） |
  |---|---|
  | 思源主力 | SourceSerifHeavy(19) · SourceHanSansHeavy(7) · SourceHanSerifMedium(3) · SourceHanSansBold(1) · SourceSerifCN-Light(1) |
  | 数据等宽 | **SpaceMono(29·坐标号/日期)** · Courier New(6) · Helvetica(1) |
  | 中文手写·楷 | LXGWWenKai 霞鹜文楷(8·**日文句同走**) · ZhuoKaiKai 清松手写体(3) · YanShiQiuHong 演示秋鸿楷(1) |
  | 西文装饰 | CinzelBold(4) · CaveatBold(2) · Prata · ArchivoBlack · BarlowCondensed-Black · Unbounded · BodoniModa · CormorantGaramond-Italic（各1） |
  | 系统兜底 | Songti SC · PingFang SC |
- **缺字兜底（font_guard，fontTools≥4.53）**：渲染前 cmap 逐字查 —— 整段覆盖 **<50% → 整段换思源宋**（保排版完整）· **≥50% 零星缺字 → 逐字 `<span>`** 兜底 · **兜底仍缺 = `uncoverable` → 质检 ✗ 绝不静默**（引擎侧仅白名单款启用）。
- **铁律**：字体是款设计的一部分（各款 `fonts.hero/emotion/data`）——**换字体=改款**；给款配文案先过该字体 cmap（与 B16 词对图同口径）。

## 读图排版铁律（从图像特征推出的避坑规则）
- **顶部死白**（`brightness.top` 高 / `highkey`）→ 白字必死 → 墨色压印 或 白卡纸反衬（偏 09/01）。
- **底部暗带**（`brightness.bottom` 低）→ 白字落座前微压暗。
- **高调白** → 白照片配白卡（`#f8f5ee`）+ 黑字；或纯黑典藏接触印相（黑卡 `#101418` 反衬）。
- **纯净素雅** → 极简画廊 / 东方素笺 / 瑞士极简 / 法式优雅，拒浓艳。
- **反边缘龟缩** → 文字与主体中轴呼应或结构拥抱（人像天顶中轴下沉 5-7%）。
- **复杂背景 / 主体贴边 / 死白不均** → 强制画框/卡纸装裱（画框是"不容易出错"的数学解）。

## 诚实边界
- **像素只能测客观数值**；题材/脸/昼夜/场景/气质**必须靠模型识图**。A 与 B 冲突时以 A（模型）为主。
- **「拓扑↔流派」绑定会错位**（stone/bauhaus/slender_zen；nordic〔已下线〕为历史案例，已在 `validate_layout_consistency()` 暴露）：选流派**别信**"拓扑的 primary_genres"，要用**真实 hero 落区**（`hero_zone_for_genre()`）判字落哪。
- **满幅脸 P0-7 优先于风格**：所有 `text_on_photo==True` 的流派都会压脸 → 只选 **specimen**，否则明确告知用户需卡纸流派或换有留白的构图。
- **无留白（主体满幅）**：大字版式必压主体 → 选**边缘装裱/卡纸**（specimen）或提示用户换构图。
- **识别不准** → 如实告诉用户，让用户确认/换图；**疑义即降级**（P0-9）：昼夜/场景置信度低时禁止编造高确定性文案，降级为中性文案或交用户确认。
- ~~**拓02/拓05 无专属流派**~~（**已过时**，2026-09-02 蓝图补齐后 `bedrock_stele`→拓02、`light_leak`→拓05 已实现；权威清单见 `docs/美术规范.md` §2）。

## Legacy
- `scripts/selector.py`（旧"位置先行选 genre"）已**废弃**，不再出现在流程中（保留供对照）。新链路用 `analyze_pixel.py` + `topology_registry.py`。
