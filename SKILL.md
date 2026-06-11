---
name: project-radar
description: >-
  Günlük trend & topluluk keşif radarı. Use this skill whenever the user asks to
  run the "Project Radar" (or just "the radar"), produce a daily report of trending
  and talked-about useful projects, scan GitHub trending, or summarize what's being
  discussed across GitHub, Hacker News, Product Hunt, newsletters and social —
  output is a standalone Turkish HTML report in the project's signature design.
  Surfaces practically useful projects (open-source repos, apps, devtools); AI/LLM
  tooling is prominent but real-world usefulness is the filter. Triggers: "project
  radar çalıştır", "proje radarı", "radar çalıştır", "github trending raporu",
  "bugün ne konuşuluyor", "run the radar". Also manages a persistent WATCHLIST:
  "<repo>'yu watchliste ekle" / "add <repo> to watchlist" writes a medium-depth
  detail report (Markdown + HTML); "watchlist'i getir" / "show watchlist" lists
  entries with file references. Discovery-only: NEVER clones, installs, builds,
  or runs candidate repos.
metadata:
  version: "1.1.1"
  author: sametbrr@gmail.com
---

# Project Radar

Her gün **trend olan** ve toplulukta **konuşulan işe yarar projeleri** (yeni app'ler,
open-source repolar, devtools) keşfeder; sadece popüler diye değil, **Samet'in günlük
işine pratik fayda** ve (uygunsa) **LLM/ajan araçlarına (Claude, Codex, Hermes vb.) entegrasyon** potansiyeline göre filtreler.
AI/LLM araçları öne çıkan bir ilgi alanıdır ama tek kriter değildir. Çıktı, referans
tasarımla birebir aynı, tek dosyalık bir **Türkçe HTML** rapordur — her seferinde HTML üretilir.

## Kesin kural: test yok
Bu radar **clone / install / build / run yapmaz**. Sadece keşif, kaynak okuma,
README/landing page inceleme, topluluk sinyali ve fayda/risk değerlendirmesi yapar.
Bir aday özellikle seçilirse test **ayrı, manuel** bir adımdır — günlük radara dahil
değildir.

## İş akışı (sırayla)

1. **Kaynakları tara.** `references/sources-and-scoring.md` dosyasındaki kategori ve
   arama sorgularını kullan.
   - **Önce GitHub Trending'i çek (deterministik).** Dil/tür fark etmeksizin günün trend
     listesini almak için scraper'ı çalıştır (günlük radarda **daily** varsayılan):
     ```bash
     python3 scripts/fetch_github_trending.py --out /tmp/github-trending-raw.json
     ```
     Bu, "bugün ivme kazanan" repoları çekip ham `[{owner, repo, lang, stars, today, url, desc}]`
     JSON'u yazar (skor/Türkçe açıklama yok). Sen bu listedeki repoları skorlar, Türkçe
     açıklamayı yazar ve `trending[]`'e taşırsın.
     - **Haftalık özet istendiğinde** daily yerine `--since weekly` kullan (weekly/monthly
       yavaş değiştiği için günlük koşuda çekilmez; istenirse `--since all` üçünü birleştirir).
   - **Sonra diğer platformları tara** (`web_search` / `web_fetch` / curl ve varsa bağlı
     MCP araçları): Google (arama + Trends), Reddit (subreddit top/hot), YouTube (trending +
     arama), Hacker News, X / Twitter, genel web. Yalnızca AI/LLM değil; **genel teknoloji
     ve ürün gündemi** de kapsama dahildir.
2. **Skorla ve sınıflandır.** Her aday için 0–100 pratik fayda skoru ve bir aksiyon
   sınıfı üret (bkz. `references/sources-and-scoring.md`).
3. **Filtrele.** Uzun ham liste verme. Sadece anlamlı adayları taşı; gerisini
   `watchlist` veya `hype` bölümlerine düşür.
4. **Veriyi yaz.** Sonucu `references/report-schema.md`'deki şemaya birebir uyan bir
   JSON dosyasına yaz (ör. `/tmp/report-data.json`). Tüm metin **Türkçe**; teknik
   terimler İngilizce kalır.
5. **HTML üret.** Render script'ini çalıştır (çıktı uzantısı `.html` → standalone HTML):
   ```bash
   python3 scripts/build_report.py \
     --data /tmp/report-data.json \
     --out  "/path/Project-Radar-$(date +%F).html"
   ```

## Skor → rozet eşlemesi
Skor 0–100 üretilir; raporda `/10` rozet olarak gösterilir (85 → 8.5/10). Renkler:
85+ sage (çok yüksek), 75–84 mist-blue (yüksek), 70–74 yellow (iyi), 70 altı
orange (niş/temkinli). Bu eşik ve renkler tasarımda sabittir — değiştirme.

## Rapor bölümleri (HTML)
Sırasıyla: **Kısa sonuç** → **En iyi adaylar** (tüm kaynaklar, zengin kartlar) →
**GitHub trending** (referans kart düzeni) → **Bugün konuşulanlar** (konu başlıkları)
→ **Workflow / Agent fikirleri** → **Watchlist önerileri** → **Hype / şüpheli / reddedilenler**.
Boş bölümler otomatik gizlenir — uydurma içerik ekleme.

## Render motoru
`build_report.py` varsayılan olarak **tek dosyalık HTML** üretir: referans tasarımla
birebir aynı, animasyonlar açık. **Font:** tek font olarak **Inter** kullanılır ve
template'te **Google Fonts**'tan yüklenir (SIL OFL, ücretsiz, her yerde; skill'e gömülü
font yok). Çevrimdışıyken sistem sans'ına düşer, yerleşim değişmez. PDF gerekirse
`--out *.pdf`: mobil için A4 dikey, sayfalı, satır başına 2 kompakt kart düzeni (headless
Chromium; HTML çıktısı değişmez). Gereksinimler: `scripts/requirements.txt`.

## Watchlist (kalıcı)
Günlük rapordaki **"Watchlist önerileri"** geçici öneridir. Kalıcı, curate edilmiş watchlist
ayrıdır ve `scripts/watchlist.py` ile yönetilir. Detaylar: `references/watchlist.md`.
- **Ekle** ("<repo>'yu watchliste ekle"): `python3 scripts/watchlist.py add <owner/repo|url>`
  → GitHub metadata + README **okunur** (clone YOK), `reports/<slug>.raw.json` + `analysis.json`
  stub'ı yazılır. Sen `analysis.json`'u **Orta derinlikte Türkçe** doldurursun, sonra
  `python3 scripts/watchlist.py render <slug>` → `.md` + imza `.html` üretilir.
- **Getir** ("watchlist'i getir"): `python3 scripts/watchlist.py list` → tüm kayıtlar
  **dosya referanslarıyla** (md/html yolları) listelenir.
- Klasör default `<SKILL_DIR>/watchlist` (env `PROJECT_RADAR_WATCHLIST_DIR` / `--dir` ile değişir).

## Dosya haritası
- `references/sources-and-scoring.md` — kaynaklar, ilgi alanları, skorlama, aksiyon sınıfları.
- `references/report-schema.md` — JSON şeması + alanların rapor bölümlerine eşlenmesi.
- `references/watchlist.md` — kalıcı watchlist: klasör düzeni, analiz şeması, komutlar, tetikleyiciler.
- `assets/report-template.html` — birebir tasarım (Jinja2). **Tasarımı bozma.**
- `assets/watchlist-report-template.html` — tek-proje watchlist detay raporu (imza HTML).
- `assets/report-data.example.json` — referans örnek veri (genişletilmiş trending + adaylar).
- `scripts/fetch_github_trending.py` — GitHub Trending'in tam listesini çeken deterministik scraper (curl + stdlib).
- `scripts/watchlist.py` — kalıcı watchlist yöneticisi (add / render / list / remove).
- `scripts/build_report.py` — JSON → HTML (varsayılan) / PDF.

## Hızlı doğrulama
GitHub scraper'ı dene (gerçek veriye karşı):
```bash
python3 scripts/fetch_github_trending.py --out /tmp/github-trending-raw.json
```
Şema değişikliği sonrası örnek veriyle render dene:
```bash
python3 scripts/build_report.py --data assets/report-data.example.json --out /tmp/ornek.html
```