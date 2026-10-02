# Cover Plan · 封面计划

> Cover Plan（封面计划）—— 给任何照片一张刊物级封面。

English | **简体中文**

**Cover Plan 不修图。** 它读你的照片 → 挑一副版式骨架 → 从 60 套刊物气质里选一套 → 用纯 HTML/CSS/SVG 把照片、标题、日期、装饰叠成一张封面。像素零改动 —— 所有设计都发生在渲染层。

## 效果展示

八张照片进去，十六张刊物级封面出来 —— 每张原片配 **两款不同风格**：

| 原图 | 成片 1 | 成片 2 |
|---|---|---|
| <img src="docs/assets/showcase/01-before.jpg" width="270" alt="原图 1"> | <img src="docs/assets/showcase/01-after.jpg" width="270" alt="成片 1a"><br><sub>french_elegance</sub> | <img src="docs/assets/showcase/01-after2.jpg" width="270" alt="成片 1b"><br><sub>kinfolk_air</sub> |
| <img src="docs/assets/showcase/02-before.jpg" width="270" alt="原图 2"> | <img src="docs/assets/showcase/02-after.jpg" width="270" alt="成片 2a"><br><sub>slender_zen</sub> | <img src="docs/assets/showcase/02-after2.jpg" width="270" alt="成片 2b"><br><sub>specimen</sub> |
| <img src="docs/assets/showcase/03-before.jpg" width="270" alt="原图 3"> | <img src="docs/assets/showcase/03-after.jpg" width="270" alt="成片 3a"><br><sub>film_rsx_sprocket</sub> | <img src="docs/assets/showcase/03-after2.jpg" width="270" alt="成片 3b"><br><sub>playbill</sub> |
| <img src="docs/assets/showcase/04-before.jpg" width="270" alt="原图 4"> | <img src="docs/assets/showcase/04-after.jpg" width="270" alt="成片 4a"><br><sub>torn_journal</sub> | <img src="docs/assets/showcase/04-after2.jpg" width="270" alt="成片 4b"><br><sub>music_manuscript</sub> |
| <img src="docs/assets/showcase/05-before.jpg" width="270" alt="原图 5"> | <img src="docs/assets/showcase/05-after.jpg" width="270" alt="成片 5a"><br><sub>silhouette</sub> | <img src="docs/assets/showcase/05-after2.jpg" width="270" alt="成片 5b"><br><sub>bedrock_stele</sub> |
| <img src="docs/assets/showcase/06-before.jpg" width="270" alt="原图 6"> | <img src="docs/assets/showcase/06-after.jpg" width="270" alt="成片 6a"><br><sub>doodle_summer</sub> | <img src="docs/assets/showcase/06-after2.jpg" width="270" alt="成片 6b"><br><sub>nordic_meander</sub> |
| <img src="docs/assets/showcase/07-before.jpg" width="270" alt="原图 7"> | <img src="docs/assets/showcase/07-after.jpg" width="270" alt="成片 7a"><br><sub>pop_lichtenstein</sub> | <img src="docs/assets/showcase/07-after2.jpg" width="270" alt="成片 7b"><br><sub>collage_man</sub> |
| <img src="docs/assets/showcase/08-before.jpg" width="270" alt="原图 8"> | <img src="docs/assets/showcase/08-after.jpg" width="270" alt="成片 8a"><br><sub>swiss_red_grid</sub> | <img src="docs/assets/showcase/08-after2.jpg" width="270" alt="成片 8b"><br><sub>torn_deckle</sub> |

## 边界

| 它做 | 它不做 |
|---|---|
| 版式 / 构图 / 字重 / 装饰的完整设计 | 修改照片像素（不调色、不磨皮、不裁人） |
| 读图 → 自动推荐骨架（拓扑）与风格 | 生成照片本身（照片是输入） |
| 60 款风格 × 5 种画幅（3:4 / 4:3 / 16:9 / 9:16 / 1:1） | 输出动态/视频（只出静态封面） |
| 人物照护脸（关键部位不压字） | 替代修图师的像素级精修 |

## 工作原理

```
照片 ──读图──▶ 选拓扑（9 种骨架）──▶ 选风格（60 款刊物气质）
                                          │
                                          ▼
        封面.jpg ◀──Chrome 截图── HTML/CSS/SVG 渲染层
```

## 安装

获取源码（二选一）：

- **压缩包**：仓库页 → *Code → Download ZIP*，下载后解压
- **克隆**：`git clone https://github.com/wei972568-bot/cover-plan.git`
- **国内镜像（Gitee）**：`https://gitee.com/wei972568-bot/cover-plan.git`

然后装三个 Python 依赖：

```bash
pip install -r requirements.txt   # Pillow · fontTools ≥ 4.53 · brotli —— 零 npm 依赖
```

- **Python** 3.12+
- **Chrome headless**（HTML → 图片）—— 装了 Chrome 即可
- **字体** —— 把 `scripts/` 内 `FONTS_DIR` 指到你自己的字体目录
- **装完自检**：`python scripts/_test_modern_cultural.py` → `PASS … FAIL 0`
- 可选：分发 HTML 加 `--embed-fonts --embed-photo`（完全自包含，约 +2MB）

## 快速上手

### 支持哪些 Agent

Cover Plan 是纯 CLI + HTML 管线 —— **任何能跑终端命令的 coding agent 都能直接用**，无需插件：

- **国外主流：** Claude Code · Codex · Cursor
- **国内主流：** 字节 Trae · 阿里 Qoder · 腾讯 WorkBuddy
- 其它：GitHub Copilot · 豆包 MarsCode · 文心快码 · ThinCoder · 或裸终端

读图环节配一个**视觉多模态模型**效果最好，也可以使用本地具有识图能力的模型；没有模型时 `analyze_pixel.py` 的像素分析也能给出可用的拓扑提示。ThinCoder 类 harness 可直接加载技能文件 `.thincoder/skills/cover-plan.md`。

### 在 Agent 里怎么调用

把照片**拖进对话窗口**（路径 agent 自己会拿到），说一句就行：

- **技能型 harness**（已加载 cover-plan 技能）：「做个封面」
- **通用 agent**（Claude Code / Cursor …）：「用 cover-plan 做个封面」
- 手动给路径也可以：`D:/photos/cat.jpg`

### 三步出图

```bash
# 1) 读图（可选：像素测量挑拓扑）
python scripts/analyze_pixel.py --photo <图> --json-out

# 2) 出图（--genre 从 60 款中选）
python scripts/engine_v2.py --photo <图> --genre <id> \
  --title <标题> --sub <副标> --date YYYY.MM.DD --location <地点> \
  --out out.html

# 3) HTML → 图（任何 headless Chrome 都行）
chrome --headless --screenshot=cover.png --window-size=900,1200 out.html
```

### 不满意？直接用自然语言说

不用记参数 —— 如果觉得不满意或想具体调整某些地方，对你的 agent 说人话就行。比如：

- 「标题再大一点 / 换个安静点的字体」
- 「把云朵往左挪 / 去掉喇叭那个装饰」
- 「文字别压到脸」
- 「这版太闹了，换个素净的款」
- 「日期换成秋天，文案用中文」

## 六十款 · 五个家族

| 家族 | 款数 | 气质 |
|---|---:|---|
| 引擎基础 | 13 + 2 别名 | 内置基础风格 |
| 装裱影格 | 13 | 外框思维：画框 / 邮票 / 拍立得…… |
| 载体隐喻 | 7 | 物格思维：乐谱 / 手稿 / 票据…… |
| 蓝图补齐 | 6 | 概念蓝图系列 |
| 设计语言 | 19 | 现代杂志版式：波点 / 留白 / 展签框…… |
| **合计** | **60** | **唯一权威清单：[`docs/美术规范.md`](./docs/美术规范.md)** |

## 已知限制

- 字体路径为本地配置，克隆后自行调整；直接分发 HTML 加 `--embed-fonts --embed-photo`（两者默认关）
- 款数/清单如有出入，一律以 [`docs/美术规范.md`](./docs/美术规范.md) 为准
- 待办：`_exif_location` GPS 读法（PIL10+）；deep_interlock / silhouette 真咬合（另案）

## 项目结构

```
docs/       款清单权威规范 + showcase 示例图
scripts/    五族引擎（engine_v2 / matting / metaphor / blueprint / design）+ 质检
```

## 许可

[GPL-3.0](./LICENSE) © 2026 cover-plan contributors
