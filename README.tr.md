[![GitHub release](https://img.shields.io/github/v/release/sametbrr/project-radar?display_name=tag&sort=semver)](https://github.com/sametbrr/project-radar/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

[Hızlı Başlangıç](#hızlı-başlangıç) • [Kurulum](#kurulum) • [Kullanım](#kullanım) • [Nasıl Çalışır](#nasıl-çalışır) • [Sorun Giderme](#sorun-giderme) • [Katkıda Bulunma](#katkıda-bulunma)

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

| | |
|---|---|
| **Yalnızca keşif** | Aday repoları asla clone/install/build/run yapmaz; kaynakları okur, değerlendirir ve raporlar |
| **Fayda puanlaması** | Her adayı gerçek dünya faydasına göre 0–100 puanlar; AI/LLM araçları öne çıkan bir ilgi alanıdır ama tek kriter değildir |
| **GitHub Trending'in tamamı** | Deterministik bir scraper (`fetch_github_trending.py`) günün tüm trending listesini, sabit bir alt küme değil, tüm dillerde çeker; weekly/monthly istendiğinde |
| **Çoklu kaynak taraması** | Hacker News, Reddit, Product Hunt, Google, YouTube, X ve genel web; yalnızca AI/LLM değil, genel teknoloji + ürün gündemi |
| **Kalıcı watchlist** | Herhangi bir GitHub reposunu ekleyin; README + metadata'sı okunarak orta derinlikte bir detay raporu (Markdown + imza HTML) üretilir ve dosya referanslarıyla listelenir |
| **İmza HTML rapor** | Sabit tasarımda (tek Inter fontu, animasyonlar açık) tek dosyalık, kendi içinde tam Türkçe HTML; PDF opsiyonel |
| **Ajandan bağımsız** | Agentskills.io ile uyumlu her araçta çalışan standart bir `SKILL.md` klasörü |

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

Claude Code eklentisi olarak, [skill-hub](https://github.com/sametbrr/skill-hub) marketplace'inden:

```bash
claude plugin marketplace add sametbrr/skill-hub
claude plugin install project-radar@skill-hub
pip install jinja2 markupsafe
```

Skill aynı zamanda standart bir `SKILL.md` klasörüdür, bu yüzden formatı destekleyen her ajanda çalışır:

```bash
# Kişisel (tüm projeler) — Hermes Claude Code üzerinde çalıştığı için bu,
# skill'i aynı makinedeki Hermes'e de açar.
git clone https://github.com/sametbrr/project-radar.git
cp -r project-radar ~/.claude/skills/project-radar
# bunun yerine proje kapsamlı: cp -r project-radar .claude/skills/project-radar

# Çalışma bağımlılıkları (HTML çıktısı yalnızca ilk ikisini ister):
pip install jinja2 markupsafe
# Opsiyonel PDF çıktısı:
pip install playwright && playwright install chromium
```

Claude.ai / Cowork için: Settings → Capabilities → Skills → paketlenmiş `project-radar.skill` dosyasını yükleyin.

Yeni bir oturum başlatın ve yüklendiğini doğrulamak için `/skills` çalıştırın.

---

## Kullanım

```text
> run the radar                  # günlük rapor: GitHub Trending'in tamamı + topluluk taraması → HTML
> project radar çalıştır         # aynısı, Türkçe tetikleyici
> github trending raporu         # GitHub Trending odaklı rapor
> bugün ne konuşuluyor           # bugün neler konuşuluyor
> add owner/repo to watchlist    # orta derinlikte detay raporu (Markdown + HTML)
> owner/repo'yu watchliste ekle  # aynısı, Türkçe tetikleyici
> show watchlist                 # watchlist kayıtlarını dosya referanslarıyla listele
> watchlist'i getir              # aynısı, Türkçe tetikleyici
/project-radar                   # doğrudan çağır (eklenti kurulumunda: /project-radar:project-radar)
```

Haftalık özet isterseniz radar günlük yerine haftalık Trending listesini çeker.

### Yardımcı script'ler

Kurulumu doğrulamak için pakete dahil örneği render edin ya da skill'in kullandığı script'leri doğrudan çalıştırın:

```bash
# Pakete dahil örneği render et:
python3 scripts/build_report.py \
  --data assets/report-data.example.json \
  --out  Project-Radar-$(date +%F).html

# GitHub Trending'in tam listesini çek (deterministik, tüm diller):
python3 scripts/fetch_github_trending.py --out /tmp/github-trending-raw.json

# Watchlist: repo ekle, detay raporunu render et, hepsini referanslarıyla listele:
python3 scripts/watchlist.py add owner/repo
python3 scripts/watchlist.py render owner__repo
python3 scripts/watchlist.py list

# Bunun yerine mobil uyumlu PDF (A4 dikey, sayfalı):
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
├── SKILL.md                            # ajan talimatları + tetikleyiciler
├── references/
│   ├── sources-and-scoring.md          # kaynaklar, ilgi alanları, 0–100 puanlama, aksiyon sınıfları
│   ├── report-schema.md                # report-data.json şeması → HTML bölümleri
│   └── watchlist.md                    # kalıcı watchlist: düzen, şema, komutlar
├── assets/
│   ├── report-template.html            # imza tasarım (Jinja2)
│   ├── watchlist-report-template.html  # proje bazlı watchlist detayı (HTML)
│   └── report-data.example.json        # örnek veri (genişletilmiş trending + 4 aday)
└── scripts/
    ├── fetch_github_trending.py        # deterministik GitHub Trending scraper
    ├── watchlist.py                    # kalıcı watchlist yöneticisi (add/render/list)
    ├── build_report.py                 # JSON → HTML (varsayılan) / PDF
    └── requirements.txt
```

---

## Sorun Giderme

**Watchlist `add`, `GitHub: API rate limit exceeded` ya da `metadata çekilemedi` ile duruyor** — kimliksiz GitHub API saatte 60 isteğe izin verir. `gh` CLI'ı kurup `gh auth login` çalıştırın; `PATH`'te olduğunda watchlist onu otomatik kullanır.

**`.pdf` çıktı yolu HTML dosyası ve `No PDF engine available` uyarısı veriyor** — PDF motorunu kurun: `pip install playwright && playwright install chromium`. `PATH`'teki `wkhtmltopdf` de yedek olarak çalışır.

**Trending scraper `curl başarısız` yazıyor** — curl GitHub'a ulaşamadı (ağ, proxy ya da zaman aşımı); script kendiliğinden Python `urllib` ile yeniden dener. O da başarısız olursa `https://github.com/trending` adresinin aynı makineden açıldığını kontrol edin.

---

## Katkıda Bulunma

- Sorular ve fikirler: [Discussions](https://github.com/sametbrr/project-radar/discussions)
- Hatalar: [issue takibi](https://github.com/sametbrr/project-radar/issues)
- Pull request'ler: önce [katkı rehberini](https://github.com/sametbrr/.github/blob/main/CONTRIBUTING.md) okuyun
- Güvenlik bildirimleri: herkese açık issue yerine [güvenlik politikasını](https://github.com/sametbrr/project-radar/security/policy) izleyin

---

## Lisans

MIT — bkz. [LICENSE](LICENSE). Üçüncü taraf notları (Inter fontu) [NOTICE](NOTICE) dosyasındadır.
