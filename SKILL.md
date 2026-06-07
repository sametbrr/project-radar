---
name: project-radar
description: >-
  Günlük trend & topluluk keşif radarı. Use this skill whenever the user asks to
  run the "Project Radar" (or just "the radar"), produce a daily report of trending
  and talked-about useful projects, scan "what's trending on GitHub", or summarize
  what's being discussed across GitHub, Hacker News, Product Hunt, newsletters and
  social — and wants the result as a standalone HTML file in the project's signature
  design. It surfaces practically useful trending + discussed projects (open-source
  repos, apps, devtools); AI/LLM tooling is prominent but NOT the only filter —
  scoring is based on real-world usefulness. Triggers: "project radar çalıştır",
  "proje radarı", "radar çalıştır", "github trending raporu", "bugün ne konuşuluyor",
  "run the radar". Discovery-only: NEVER clones, installs, builds, or runs candidate
  repos — it reads sources, scores usefulness 0–100, classifies actions, then renders
  a Turkish HTML report identical to assets/report-template.html.
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
   arama sorgularını kullan. Veriyi `web_search` / `web_fetch` (ve varsa bağlı MCP
   araçları) ile topla. GitHub Trending için `https://github.com/trending` ve dil
   filtrelerini (Python, TypeScript, Go, Rust, Jupyter Notebook) tara.
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
→ **Hermes workflow fikirleri** → **Watchlist** → **Hype / şüpheli / reddedilenler**.
Boş bölümler otomatik gizlenir — uydurma içerik ekleme.

## Render motoru
`build_report.py` varsayılan olarak **tek dosyalık HTML** üretir: referans tasarımla
birebir aynı, animasyonlar açık. **Font:** tek font olarak **Inter** kullanılır ve
template'te **Google Fonts**'tan yüklenir (SIL OFL, ücretsiz, her yerde; skill'e gömülü
font yok). Çevrimdışıyken sistem sans'ına düşer, yerleşim değişmez. PDF gerekirse
`--out *.pdf` (headless Chromium, tek uzun sayfa). Gereksinimler: `scripts/requirements.txt`.

## Dosya haritası
- `references/sources-and-scoring.md` — kaynaklar, ilgi alanları, skorlama, aksiyon sınıfları.
- `references/report-schema.md` — JSON şeması + alanların rapor bölümlerine eşlenmesi.
- `assets/report-template.html` — birebir tasarım (Jinja2). **Tasarımı bozma.**
- `assets/report-data.example.json` — referans örnek veri (14 trending repo + adaylar).
- `scripts/build_report.py` — JSON → HTML (varsayılan) / PDF.

## Hızlı doğrulama
Şema değişikliği sonrası örnek veriyle render dene:
```bash
python3 scripts/build_report.py --data assets/report-data.example.json --out /tmp/ornek.html
```
