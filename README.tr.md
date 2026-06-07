[![GitHub release](https://img.shields.io/github/v/release/sametbrr/project-radar?display_name=tag&sort=semver)](https://github.com/sametbrr/project-radar/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

# Project Radar

Günlük bir trend & topluluk keşif radarı, bir Claude Agent Skill olarak paketlenmiştir — GitHub Trending'i ve Hacker News, Product Hunt, bültenler ve sosyal medyada konuşulanları tarar, her adayı gerçek dünya faydası açısından 0–100 puanlar ve sabit imza tasarımıyla tek dosyalık, kendi içinde tam bir Türkçe HTML rapor üretir.

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
- **Çoklu kaynak taraması** — GitHub Trending'in yanı sıra Hacker News, Product Hunt, bültenler ve sosyalde konuşulanlar.
- **İmza HTML rapor** — sabit tasarımda (tek Inter fontu, animasyonlar açık) tek dosyalık, kendi içinde tam Türkçe HTML; PDF opsiyonel.
- **Ajandan bağımsız** — agentskills.io ile uyumlu her araçta çalışan standart bir `SKILL.md` klasörü.

---

## Gereksinimler

- Python 3 — rapor üreticisi için.
- `jinja2` ve `markupsafe` — HTML çıktısı için zorunlu.
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

Her şeyin çalıştığını doğrulamak için pakete dahil örneği render edin veya `--data`'yı kendi rapor JSON'unuza yönlendirin.

```bash
# Render the bundled example:
python3 scripts/build_report.py \
  --data assets/report-data.example.json \
  --out  Project-Radar-$(date +%F).html

# PDF instead:
python3 scripts/build_report.py --data <data.json> --out report.pdf
```

---

## Nasıl Çalışır

```
sources  →  (agent scores & filters per references/)  →  report-data.json  →  build_report.py  →  HTML
```

1. Ajan, `references/sources-and-scoring.md` dosyasındaki kaynakları tarar.
2. `references/report-schema.md`'deki şemaya birebir uyan bir `report-data.json` yazar.
3. `scripts/build_report.py`, bu JSON'u `assets/report-template.html` üzerinden standalone bir HTML dosyasına render eder. PDF opsiyoneldir.

Rapor tek bir font kullanır — Inter — ve Google Fonts'tan yüklenir (SIL OFL, ücretsiz, skill'e gömülü değil); çevrimdışıyken sistem sans-serif fontuna düşer, yerleşim birebir aynı kalır.

---

## Proje Yapısı

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

## Lisans

MIT — bkz. [LICENSE](LICENSE).
