# cover-plan 封面设计引擎 — 代理须知（AGENTS.md）

**读图 → 推导排版铁律 → 挑拓扑 → 按图定制出图**（Python 引擎 + HTML 渲染 + 截图）。
本项目自带工作流 skill：`.thincoder/skills/cover-plan.md`（识图 → 挑流派 → 出图），先 `skill list` 看它。

## 引擎纪律

- 引擎脚本（`scripts/engine_v2.py` 等）是稳定资产：**改动宁可小**；每次改完跑
  `python -m py_compile <改动文件>` + `python scripts/_test_modern_cultural.py`（应输出 `PASS … FAIL 0`）。
- 改大文件用**精确字符串替换**，不要整段重写。

## 字体路径必须实读盘

字体显示名与盘上文件名常不一致，**别按记忆或别名写路径**（写错 = 渲染豆腐块 □ 或回退到错误字体）。
`@font-face` 指向本机字体目录（各引擎 `FONTS_DIR` 常量）；要把 HTML 分发给没装字体的机器，加
`--embed-fonts --embed-photo`（字体子集 + 照片 base64 内嵌，自包含）。

## 文档入口

| 主题 | 文档 |
|---|---|
| 款清单 / P0 铁律 / CLI / 护脸（**唯一权威口径**，计数以此为准） | `docs/美术规范.md` |
| 安装与使用 | `README.md`（英）/ `README.zh-CN.md`（中） |
| 工作流 skill（识图 → 挑流派 → 出图） | `.thincoder/skills/cover-plan.md` |

## 交互约定

- **渲染出的图必须贴给用户看**（`read_image`）—— 不能只给路径或文字描述（2026-09-02 用户明确「以后都这样」）
- 用户不满意的调整**用自然语言直接说**即可（agent 翻译成 `--genre/--title/--fg-texts/--photo-focus-y` 等参数或 config 终值；写图前先确认）
- 常量级参数改完 → 重渲样张让用户目测验收
- 遇到问题三招：看**完整**错误输出（根因通常在末尾）→ 查官方文档 → 二分法定位
