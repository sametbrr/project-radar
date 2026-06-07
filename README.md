# Project Radar

> Türkçe açıklama için bkz. `README.tr.md` (talep üzerine eklenir).

A daily **trending & community discovery radar**, packaged as a [Claude Agent
Skill](https://code.claude.com/docs/en/skills). It scans GitHub Trending and what's
being discussed across Hacker News, Product Hunt, newsletters and social, scores each
candidate **0–100 on real-world usefulness** (AI/LLM tooling is a prominent interest
but not the only filter), classifies an action, and renders a single, self-contained
**Turkish HTML report** in a fixed signature design.

**Discovery-only:** the skill never clones, installs, builds, or runs candidate repos.
It reads sources, evaluates, and reports.

## How it works

```
sources  →  (agent scores & filters per references/)  →  report-data.json  →  build_report.py  →  HTML
```

1. The agent scans the sources in `references/sources-and-scoring.md`.
2. It writes a `report-data.json` matching `references/report-schema.md`.
3. `scripts/build_report.py` renders that JSON through `assets/report-template.html`
   into a standalone HTML file (single font Inter via Google Fonts, animations on). PDF is optional.

## Install

The skill is a standard `SKILL.md` folder, so it works in any agent that supports the
format (Claude Code, OpenClaw, Codex CLI, Cursor, Gemini CLI …).

### Claude Code / Hermes (local)

```bash
# Personal (all projects) — Hermes runs on top of Claude Code, so this also
# makes the skill available to Hermes on the same machine.
git clone https://github.com/sametbrr/project-radar.git
cp -r project-radar ~/.claude/skills/project-radar
# (project-scoped instead: cp -r project-radar .claude/skills/project-radar)

# Runtime deps (HTML output needs only the first two):
pip install jinja2 markupsafe
# Optional PDF output:
pip install playwright && playwright install chromium
```

Start a new session and run `/skills` to confirm it loaded. Trigger it with
`project radar çalıştır` / `run the radar`, or invoke directly with `/project-radar`.

> If Hermes uses a custom skills directory, drop the `project-radar/` folder there
> instead of `~/.claude/skills/`.

### Claude.ai / Cowork

Settings → Capabilities → Skills → upload the packaged `project-radar.skill`.

## Usage

```bash
# Render the bundled example to verify everything works:
python3 scripts/build_report.py \
  --data assets/report-data.example.json \
  --out  Project-Radar-$(date +%F).html

# PDF instead:
python3 scripts/build_report.py --data <data.json> --out report.pdf
```

## Structure

```
project-radar/
├── SKILL.md                      # agent instructions + triggers
├── references/
│   ├── sources-and-scoring.md    # sources, interests, 0–100 scoring, action classes
│   └── report-schema.md          # report-data.json schema → HTML sections
├── assets/
│   ├── report-template.html      # the signature design (Jinja2)
│   └── report-data.example.json  # sample data (14 trending + 4 candidates)
└── scripts/
    ├── build_report.py           # JSON → HTML (default) / PDF
    └── requirements.txt
```

## Fonts & licensing

The report uses a **single font — [Inter](https://fonts.google.com/specimen/Inter)** —
loaded from **Google Fonts** in the template. It is **non-commercial (SIL OFL), free to
use anywhere, and not bundled** with the skill (no font files in the repo). Offline, it
falls back to the system sans-serif; layout is unchanged either way.

No commercial fonts are involved, so the repo is safe to publish publicly as-is.

Project code: MIT (`LICENSE`).
