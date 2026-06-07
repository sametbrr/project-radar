[![GitHub release](https://img.shields.io/github/v/release/sametbrr/project-radar?display_name=tag&sort=semver)](https://github.com/sametbrr/project-radar/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

# Project Radar

A daily trending & community discovery radar, packaged as a Claude Agent Skill — it pulls the full GitHub Trending list and scans what's discussed across Hacker News, Reddit, Product Hunt, Google, YouTube, X and the wider web, scores each candidate 0–100 on real-world usefulness, renders a single self-contained Turkish HTML report in a fixed signature design, and keeps a persistent watchlist with per-project detail reports.

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
- **Full GitHub Trending** — a deterministic scraper (`fetch_github_trending.py`) pulls the entire daily Trending list across all languages, not a fixed subset; weekly/monthly on demand.
- **Multi-source scan** — Hacker News, Reddit, Product Hunt, Google, YouTube, X and the wider web; general tech + product agenda, not only AI/LLM.
- **Persistent watchlist** — add any GitHub repo; its README + metadata are read into a medium-depth detail report (Markdown + signature HTML) and listed back with file references.
- **Signature HTML report** — one self-contained Turkish HTML file in a fixed design (single Inter font, animations on); PDF optional.
- **Agent-agnostic** — a standard `SKILL.md` folder that works in any agentskills.io-compatible tool.

---

## Requirements

- Python 3 — for the report renderer and helper scripts.
- `jinja2` and `markupsafe` — required for HTML output.
- `curl` — used by the Trending scraper and watchlist fetch (falls back to Python `urllib`).
- `gh` CLI — optional; the watchlist uses it for authenticated GitHub API, falling back to unauthenticated `curl`.
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

Render the bundled example to verify everything works, then use the helper scripts directly.

```bash
# Render the bundled example:
python3 scripts/build_report.py \
  --data assets/report-data.example.json \
  --out  Project-Radar-$(date +%F).html

# Pull the full GitHub Trending list (deterministic, all languages):
python3 scripts/fetch_github_trending.py --out /tmp/github-trending-raw.json

# Watchlist: add a repo, render its detail report, list everything with refs:
python3 scripts/watchlist.py add owner/repo
python3 scripts/watchlist.py render owner__repo
python3 scripts/watchlist.py list

# Mobile-friendly PDF instead (A4 portrait, paginated):
python3 scripts/build_report.py --data <data.json> --out report.pdf
```

---

## Configuration

- `PROJECT_RADAR_WATCHLIST_DIR` — where the persistent watchlist lives (default: `watchlist/` under the skill directory). The `watchlist.py --dir` flag overrides it.
- The report design — colors, score thresholds, single Inter font — is fixed in `assets/report-template.html` by design and is not meant to be edited.

---

## How It Works

```
fetch_github_trending.py ─┐
HN · Reddit · PH · Google · YouTube · X · web ─┤→ agent scores & filters → report-data.json → build_report.py → HTML
```

1. `scripts/fetch_github_trending.py` pulls the full Trending list; the agent scans the other sources defined in `references/sources-and-scoring.md`.
2. The agent writes a `report-data.json` matching `references/report-schema.md`.
3. `scripts/build_report.py` renders that JSON through `assets/report-template.html` into a standalone HTML file. PDF is optional.

Separately, `scripts/watchlist.py` manages a persistent watchlist (see `references/watchlist.md`): it reads a repo's README + GitHub metadata and renders a per-project detail report (Markdown + HTML) — still discovery-only, no cloning or running.

The report uses a single font — Inter — loaded from Google Fonts (SIL OFL, free, not bundled with the skill); offline it falls back to the system sans-serif with identical layout.

---

## Project Structure

```
project-radar/
├── SKILL.md                            # agent instructions + triggers
├── references/
│   ├── sources-and-scoring.md          # sources, interests, 0–100 scoring, action classes
│   ├── report-schema.md                # report-data.json schema → HTML sections
│   └── watchlist.md                    # persistent watchlist: layout, schema, commands
├── assets/
│   ├── report-template.html            # the signature design (Jinja2)
│   ├── watchlist-report-template.html  # per-project watchlist detail (HTML)
│   └── report-data.example.json        # sample data (expanded trending + 4 candidates)
└── scripts/
    ├── fetch_github_trending.py        # deterministic GitHub Trending scraper
    ├── watchlist.py                    # persistent watchlist manager (add/render/list)
    ├── build_report.py                 # JSON → HTML (default) / PDF
    └── requirements.txt
```

---

## License

MIT — see [LICENSE](LICENSE).
