[![GitHub release](https://img.shields.io/github/v/release/sametbrr/project-radar?display_name=tag&sort=semver)](https://github.com/sametbrr/project-radar/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

# Project Radar

A daily trending & community discovery radar, packaged as a Claude Agent Skill — it scans GitHub Trending and what's discussed across Hacker News, Product Hunt, newsletters and social, scores each candidate 0–100 on real-world usefulness, and renders a single self-contained Turkish HTML report in a fixed signature design.

> 🇹🇷 Türkçe için [README.tr.md](README.tr.md)

---

## Quick Start

```bash
git clone https://github.com/sametbrr/project-radar.git
cp -r project-radar ~/.claude/skills/project-radar
pip install jinja2 markupsafe
```

Start a new session, then trigger it with `project radar çalıştır` / `run the radar` (or invoke `/project-radar`).

---

## Features

- **Discovery-only** — never clones, installs, builds, or runs candidate repos; it reads sources, evaluates, and reports.
- **Usefulness scoring** — scores each candidate 0–100 on real-world usefulness; AI/LLM tooling is a prominent interest but not the only filter.
- **Multi-source scan** — GitHub Trending plus what's being discussed across Hacker News, Product Hunt, newsletters, and social.
- **Signature HTML report** — one self-contained Turkish HTML file in a fixed design (single Inter font, animations on); PDF optional.
- **Agent-agnostic** — a standard `SKILL.md` folder that works in any agentskills.io-compatible tool.

---

## Requirements

- Python 3 — for the report renderer.
- `jinja2` and `markupsafe` — required for HTML output.
- `playwright` + Chromium — optional, only for PDF output.
- An agent that supports the `SKILL.md` format (Claude Code, Hermes, Codex CLI, Cursor, Gemini CLI …).

---

## Installation

The skill is a standard `SKILL.md` folder, so it works in any agent that supports the format.

```bash
# Personal (all projects) — Hermes runs on top of Claude Code, so this also
# makes the skill available to Hermes on the same machine.
git clone https://github.com/sametbrr/project-radar.git
cp -r project-radar ~/.claude/skills/project-radar
# project-scoped instead: cp -r project-radar .claude/skills/project-radar

# Runtime deps (HTML output needs only the first two):
pip install jinja2 markupsafe
# Optional PDF output:
pip install playwright && playwright install chromium
```

For Claude.ai / Cowork: Settings → Capabilities → Skills → upload the packaged `project-radar.skill`.

Start a new session and run `/skills` to confirm it loaded.

---

## Usage

Render the bundled example to verify everything works, or point `--data` at your own report JSON.

```bash
# Render the bundled example:
python3 scripts/build_report.py \
  --data assets/report-data.example.json \
  --out  Project-Radar-$(date +%F).html

# PDF instead:
python3 scripts/build_report.py --data <data.json> --out report.pdf
```

---

## How It Works

```
sources  →  (agent scores & filters per references/)  →  report-data.json  →  build_report.py  →  HTML
```

1. The agent scans the sources in `references/sources-and-scoring.md`.
2. It writes a `report-data.json` matching `references/report-schema.md`.
3. `scripts/build_report.py` renders that JSON through `assets/report-template.html` into a standalone HTML file. PDF is optional.

The report uses a single font — Inter — loaded from Google Fonts (SIL OFL, free, not bundled with the skill); offline it falls back to the system sans-serif with identical layout.

---

## Project Structure

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

---

## License

MIT — see [LICENSE](LICENSE).
