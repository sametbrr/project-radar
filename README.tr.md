[![GitHub release](https://img.shields.io/github/v/release/sametbrr/project-radar?display_name=tag&sort=semver)](https://github.com/sametbrr/project-radar/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

# Project Radar

Günlük bir trend & topluluk keşif radarı, bir Claude Agent Skill olarak paketlenmiştir — GitHub Trending'in tamamını çeker; Hacker News, Reddit, Product Hunt, Google, YouTube, X ve genel webde konuşulanları tarar, her adayı gerçek dünya faydası açısından 0–100 puanlar, sabit imza tasarımıyla tek dosyalık, kendi içinde tam bir Türkçe HTML rapor üretir ve proje bazlı detay raporlarıyla kalıcı bir watchlist tutar.

> 🇬🇧 For English see [README.md](README.md)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/sametbrr/project-radar.git
cp -r project-radar ~/.claude/skills/project-radar
pip install jinja2 markupsafe
```

Yeni bir oturum başlatın, ardından `project radar çalıştır` / `run the radar` ile tetikleyin (veya `/project-radar` ile çağırın).

---

## Özellikler

- **Yalnızca keşif** — aday repoları asla clone/install/build/run yapmaz; kaynakları okur, değerlendirir ve raporlar.
- **Fayda puanlaması** — her adayı gerçek dünya faydasına göre 0–100 puanlar; AI/LLM araçları öne çıkan bir ilgi alanıdır ama tek kriter değildir.
- **GitHub Trending'in tamamı** — deterministik bir scraper (`fetch_github_trending.py`) günün tüm trending listesini, sabit bir alt küme değil, tüm dillerde çeker; weekly/monthly istendiğinde.
- **Çoklu kaynak taraması** — Hacker News, Reddit, Product Hunt, Google, YouTube, X ve genel web; yalnızca AI/LLM değil, genel teknoloji + ürün gündemi.
- **Kalıcı watchlist** — herhangi bir GitHub reposunu ekleyin; README + metadata'sı okunarak orta derinlikte bir detay raporu (Markdown + imza HTML) üretilir ve dosya referanslarıyla listelenir.
- **İmza HTML rapor** — sabit tasarımda (tek Inter fontu, animasyonlar açık) tek dosyalık, kendi içinde tam Türkçe HTML; PDF opsiyonel.
- **Ajandan bağımsız** — agentskills.io ile uyumlu her araçta çalışan standart bir `SKILL.md` klasörü.

---

## Gereksinimler

- Python 3 — rapor üreticisi ve yardımcı scriptler için.
- `jinja2` ve `markupsafe` — HTML çıktısı için zorunlu.
- `curl` — Trending scraper ve watchlist çekme işlemi için kullanılır (Python `urllib`'e düşer).
- `gh` CLI — opsiyonel; watchlist, kimlik doğrulamalı GitHub API için bunu kullanır, yoksa kimliksiz `curl`'e düşer.
- `playwright` + Chromium — opsiyonel, yalnızca PDF çıktısı için.
- `SKILL.md` formatını destekleyen bir ajan (Claude Code, Hermes, Codex CLI, Cursor, Gemini CLI …).

---

## Kurulum

Skill standart bir `SKILL.md` klasörüdür, bu yüzden formatı destekleyen her ajanda çalışır.

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

Claude.ai / Cowork için: Settings → Capabilities → Skills → paketlenmiş `project-radar.skill` dosyasını yükleyin.

Yeni bir oturum başlatın ve yüklendiğini doğrulamak için `/skills` çalıştırın.

---

## Kullanım

Her şeyin çalıştığını doğrulamak için pakete dahil örneği render edin, ardından yardımcı scriptleri doğrudan kullanın.

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

## Yapılandırma

- `PROJECT_RADAR_WATCHLIST_DIR` — kalıcı watchlist'in tutulduğu yer (varsayılan: skill dizini altındaki `watchlist/`). `watchlist.py --dir` bayrağı bunu geçersiz kılar.
- Rapor tasarımı — renkler, skor eşikleri, tek Inter fontu — tasarım gereği `assets/report-template.html` içinde sabittir ve düzenlenmemesi gerekir.

---

## Nasıl Çalışır

```
fetch_github_trending.py ─┐
HN · Reddit · PH · Google · YouTube · X · web ─┤→ agent scores & filters → report-data.json → build_report.py → HTML
```

1. `scripts/fetch_github_trending.py` Trending'in tam listesini çeker; ajan, `references/sources-and-scoring.md` içinde tanımlı diğer kaynakları tarar.
2. Ajan, `references/report-schema.md`'deki şemaya birebir uyan bir `report-data.json` yazar.
3. `scripts/build_report.py`, bu JSON'u `assets/report-template.html` üzerinden standalone bir HTML dosyasına render eder. PDF opsiyoneldir.

Ayrıca `scripts/watchlist.py` kalıcı bir watchlist yönetir (bkz. `references/watchlist.md`): bir reponun README + GitHub metadata'sını okuyup proje bazlı bir detay raporu (Markdown + HTML) üretir — yine yalnızca keşif, clone/çalıştırma yok.

Rapor tek bir font kullanır — Inter — ve Google Fonts'tan yüklenir (SIL OFL, ücretsiz, skill'e gömülü değil); çevrimdışıyken sistem sans-serif fontuna düşer, yerleşim birebir aynı kalır.

---

## Proje Yapısı

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

## Lisans

MIT — bkz. [LICENSE](LICENSE).
