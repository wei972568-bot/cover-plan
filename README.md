# Cover Plan

> Cover Plan — give any photo a magazine-grade cover.

**English** | [简体中文](./README.zh-CN.md)

**Cover Plan never edits your photo.** It reads the image → picks a layout skeleton (topology) → selects one of 60 editorial styles → composites photo, headline, dates and ornaments into a full cover using pure HTML/CSS/SVG. Every design decision happens at the render layer.

## Showcase

Eight photos in, sixteen magazine-grade covers out — each source photo paired with **two different styles**:

| Photo | Cover 1 | Cover 2 |
|---|---|---|
| <img src="docs/assets/showcase/01-before.jpg" width="270" alt="source photo 1"> | <img src="docs/assets/showcase/01-after.jpg" width="270" alt="cover 1a"><br><sub>french_elegance</sub> | <img src="docs/assets/showcase/01-after2.jpg" width="270" alt="cover 1b"><br><sub>kinfolk_air</sub> |
| <img src="docs/assets/showcase/02-before.jpg" width="270" alt="source photo 2"> | <img src="docs/assets/showcase/02-after.jpg" width="270" alt="cover 2a"><br><sub>slender_zen</sub> | <img src="docs/assets/showcase/02-after2.jpg" width="270" alt="cover 2b"><br><sub>specimen</sub> |
| <img src="docs/assets/showcase/03-before.jpg" width="270" alt="source photo 3"> | <img src="docs/assets/showcase/03-after.jpg" width="270" alt="cover 3a"><br><sub>film_rsx_sprocket</sub> | <img src="docs/assets/showcase/03-after2.jpg" width="270" alt="cover 3b"><br><sub>playbill</sub> |
| <img src="docs/assets/showcase/04-before.jpg" width="270" alt="source photo 4"> | <img src="docs/assets/showcase/04-after.jpg" width="270" alt="cover 4a"><br><sub>torn_journal</sub> | <img src="docs/assets/showcase/04-after2.jpg" width="270" alt="cover 4b"><br><sub>music_manuscript</sub> |
| <img src="docs/assets/showcase/05-before.jpg" width="270" alt="source photo 5"> | <img src="docs/assets/showcase/05-after.jpg" width="270" alt="cover 5a"><br><sub>silhouette</sub> | <img src="docs/assets/showcase/05-after2.jpg" width="270" alt="cover 5b"><br><sub>bedrock_stele</sub> |
| <img src="docs/assets/showcase/06-before.jpg" width="270" alt="source photo 6"> | <img src="docs/assets/showcase/06-after.jpg" width="270" alt="cover 6a"><br><sub>doodle_summer</sub> | <img src="docs/assets/showcase/06-after2.jpg" width="270" alt="cover 6b"><br><sub>nordic_meander</sub> |
| <img src="docs/assets/showcase/07-before.jpg" width="270" alt="source photo 7"> | <img src="docs/assets/showcase/07-after.jpg" width="270" alt="cover 7a"><br><sub>pop_lichtenstein</sub> | <img src="docs/assets/showcase/07-after2.jpg" width="270" alt="cover 7b"><br><sub>collage_man</sub> |
| <img src="docs/assets/showcase/08-before.jpg" width="270" alt="source photo 8"> | <img src="docs/assets/showcase/08-after.jpg" width="270" alt="cover 8a"><br><sub>swiss_red_grid</sub> | <img src="docs/assets/showcase/08-after2.jpg" width="270" alt="cover 8b"><br><sub>torn_deckle</sub> |

## What it does / doesn't

| Does | Doesn't |
|---|---|
| Full layout / composition / typography / ornament design | Modify photo pixels (no color grading, no retouching) |
| Read the image → recommend skeleton (topology) & style | Generate the photo itself (photo is the input) |
| 60 styles × 5 aspect ratios (3:4 / 4:3 / 16:9 / 9:16 / 1:1) | Output video/dynamic content (static covers only) |
| Face-safe rendering for portraits (text never covers faces) | Replace pixel-level retouching |

## How it works

```
photo ──analyze──▶ pick topology (9 skeletons) ──▶ pick style (60 editorial moods)
                                                      │
                                                      ▼
   cover.jpg ◀──Chrome headless── HTML/CSS/SVG render layer
```

## Install

Get the source (either way):

- **ZIP**: repo page → *Code → Download ZIP*, then unzip
- **Clone**: `git clone https://github.com/wei972568-bot/cover-plan.git`
- **Mirror (Gitee)**: `https://gitee.com/wei972568-bot/cover-plan.git`

Then install the three Python deps:

```bash
pip install -r requirements.txt   # Pillow · fontTools ≥ 4.53 · brotli — no npm needed
```

- **Python** 3.12+
- **Chrome headless** — any installed Chrome (HTML → image screenshot)
- **Fonts** — point `FONTS_DIR` in `scripts/` at your own font directory
- **Verify the install**: `python scripts/_test_modern_cultural.py` → `PASS … FAIL 0`
- Optional: `--embed-fonts --embed-photo` for a fully self-contained HTML when sharing (≈ +2MB)

## Quick start

### Works with any agent

Cover Plan is a plain CLI + HTML pipeline — any coding agent that can run shell commands works, no plugin required:

- **Global:** Claude Code · Codex · Cursor
- **China:** Trae (ByteDance) · Qoder (Alibaba) · WorkBuddy (Tencent)
- Others: GitHub Copilot · 豆包 MarsCode · 文心快码 · ThinCoder · plain terminal

Photo reading works best with a **vision-capable model** — a local one works too; without any model, `analyze_pixel.py` still gives a usable topology hint. ThinCoder-style harnesses can load the packaged skill at `.thincoder/skills/cover-plan.md`.

### Use it inside your agent

**Drag the photo into the chat** (the agent picks up the path itself), then say one line:

- **Skill harness** (cover-plan skill loaded): “Make a cover”
- **Generic agent** (Claude Code / Cursor …): “Use cover-plan to make a cover”
- Typing a path works too: `D:/photos/cat.jpg`

### Three steps

```bash
# 1) Analyze the photo (optional — recommends a topology)
python scripts/analyze_pixel.py --photo <photo> --json-out

# 2) Render the cover (--genre picks one of 60 styles)
python scripts/engine_v2.py --photo <photo> --genre <id> \
  --title <title> --sub <subtitle> --date YYYY.MM.DD --location <place> \
  --out out.html

# 3) Screenshot HTML → image (any headless Chrome works)
chrome --headless --screenshot=cover.png --window-size=900,1200 out.html
```

### Not happy? Just say it in plain language

No need to memorize flags — tell your agent, for example:

- "Make the title bigger / switch to a quieter font"
- "Move the cloud decoration left / drop the megaphone"
- "Keep the text off the face"
- "This one is too busy — pick a calmer style"
- "Use an autumn date and Chinese copy"

## Sixty styles · five families

| Family | Count | Mood |
|---|---:|---|
| Core engine | 13 + 2 aliases | Built-in classics |
| Matting & frames | 13 | Frames, stamps, Polaroids… |
| Object metaphors | 7 | Sheet music, manuscripts, tickets… |
| Blueprint concepts | 6 | Concept poster series |
| Design language | 19 | Modern magazine layouts: dots, whitespace, label frames… |
| **Total** | **60** | **Canonical list: [`docs/美术规范.md`](./docs/美术规范.md)** |

## Known limitations

- Font paths are machine-specific — adjust them after cloning; pass `--embed-fonts --embed-photo` when distributing the HTML itself (both default off)
- For the authoritative style list, always trust [`docs/美术规范.md`](./docs/美术规范.md)
- TODO: `_exif_location` GPS reading (PIL10+); deep_interlock / silhouette true interlock (tracked separately)

## Repository layout

```
docs/       the canonical style spec + showcase images
scripts/    the five engines (engine_v2 / matting / metaphor / blueprint / design) + QC
```

## License

[GPL-3.0](./LICENSE) © 2026 cover-plan contributors
