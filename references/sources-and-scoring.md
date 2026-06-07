# Project Radar — Kaynaklar ve Skorlama

## Amaç
Her gün **trend olan** ve toplulukta **konuşulan işe yarar projeleri** (yeni app'ler,
open-source repolar, devtools, araçlar) takip etmek; ancak sadece popüler olduğu için
değil, **Samet'in günlük işlerini kolaylaştırma** ve (uygunsa) **LLM/ajan akışlarına
(Claude, Codex, Hermes vb.) entegrasyon** potansiyeline göre filtrelemek. AI/LLM araçları öne çıkan bir ilgi alanıdır, fakat tek
ölçüt değildir — değerlendirme her zaman **pratik işe yararlık** üzerinden yapılır
(örn. medya sunucusu, CRM, FinTech, devtool gibi AI-dışı projeler de adaydır).

## Test aşaması yoktur
Bu radar repo **clone / install / build / run yapmaz**. Sadece keşif, kaynak okuma,
README / landing page inceleme, topluluk sinyali, fayda/risk değerlendirmesi ve öneri
üretir. Bir proje özellikle seçilirse test ayrı manuel komutla yapılır; günlük radara
dahil değildir.

## Ana kaynak kategorileri

### 1. GitHub
- **Trending:** **tüm diller/türler** — dil filtresiyle sınırlı değil.
  `scripts/fetch_github_trending.py` ile çek. **Günlük radarda varsayılan `daily`** ("bugün
  ivme kazanan"). `weekly`/`monthly` yavaş değiştiği için her gün çekilmez; haftalık özet
  istendiğinde `--since weekly` (gerekirse `--since all` üçünü birleştirir). Script ham
  `[{owner, repo, lang, stars, today, url, desc}]` yazar; skor ve Türkçe açıklama sonradan
  agent tarafından eklenir.
- **Arama sorguları:** agent framework · claude code · mcp server · ai automation ·
  open source ai app · llm workflow · personal ai assistant · local ai · browser agent ·
  computer use · voice agent · rag · second brain ai · obsidian ai · notebooklm
  alternative · ai crm · ai sales automation · self hosted ai

### 2. Hacker News
AI, agents, Claude, OpenAI, MCP, local LLM, automation, self-hosted, devtools başlıkları;
ayrıca genel teknoloji/ürün gündemi (front page + Show HN + Launch HN).

### 3. Product Hunt / launch kaynakları
AI app'ler, productivity, developer tools, automation, sales/content araçları ve genel
ürün/launch gündemi.

### 4. Reddit
Subreddit'lerde günün öne çıkanları (top/hot) — JSON uçları curl/web_fetch ile çekilebilir
(`https://www.reddit.com/r/<sub>/top.json?t=day`): r/programming · r/MachineLearning ·
r/LocalLLaMA · r/selfhosted · r/SideProject · r/webdev · r/technology · r/Entrepreneur ·
r/artificial. Hem araç/proje isimleri hem genel teknoloji gündemi için.

### 5. Google (arama + Trends)
Genel teknoloji ve ürün gündemi aramaları (`web_search`) + Google Trends'te günün
yükselen aramaları (teknoloji/ürün odaklı süzülerek).

### 6. YouTube
Tech trending videoları + launch/kanal aramaları (yeni araç tanıtımları, demo'lar).

### 7. X / Twitter
Trending tech başlıkları + arama (auth yok; web/sonuç sayfası üzerinden). Konuşulan
araç, proje ve gündem isimleri.

### 8. Genel web
Büyük teknoloji haberleri, ürün/startup launch'ları, sektör gündemi (`web_search`).

### 9. RSS / blog / newsletter
Latent Space · Ben's Bites · The Rundown AI · TLDR AI · Simon Willison ·
Anthropic / OpenAI / Google DeepMind / Hugging Face blogları · MCP, agent, local LLM,
coding-agent odaklı teknik bloglar.

### 10. Sosyal / kaydedilenler
YouTube Watch Later ve post-scanner çıktıları; X / LinkedIn kaydedilenlerden çıkan
proje ve tool isimleri.

## Özel ilgi alanları
AI agent OS / personal operating system · Claude Code skill/plugin ekosistemi ·
MCP server'lar · Browser automation agent'ları · Second brain / Obsidian / NotebookLM
alternatifi araçlar · AI video/content automation · Lead generation / sales automation ·
CRM + AI agent sistemleri · Telegram/Discord/Gmail otomasyonları · Local-first AI app'ler ·
Self-hosted SaaS araçları · AI coding workflow araçları · Finans + AI / trading agent
araçları (dikkatli risk filtresiyle).

**Genel teknoloji + ürün gündemi de adaydır.** AI/LLM öne çıkan ilgi alanı olmaya devam
eder ama tek filtre değildir: dikkat çeken yeni ürün/launch'lar, önemli teknoloji haberleri,
güçlü açık kaynak projeler ve sektör gündemi de — pratik işe yararlık üzerinden — kapsama
girer.

## Skorlama
Her aday için **0–100** pratik fayda skoru üret. Kriterler:
- **Güncellik:** son 1–14 gün içinde çıkmış/güncellenmiş mi?
- **Momentum:** star/fork/comment/share artışı var mı?
- **Pratiklik:** günlük işleri kolaylaştırır mı?
- **Kurulum/benimsenme:** Docker/uv/npm/self-hosted dokümantasyon var mı?
- **Açıklık:** open-source mu, lisans ve kod açık mı?
- **LLM / ajan uyumu:** Claude, Claude Code, OpenAI, Codex, Hermes, OpenCode, Cursor, Gemini gibi LLM/ajan araçlarına (MCP/API/CLI/cron/browser/email vb.) bağlanabilir mi?
- **Kullanım alanı:** içerik, satış, araştırma, coding, not alma, otomasyon, second brain.
- **Risk:** security, data privacy, vendor lock-in, sadece demo, abandoned repo, aşırı hype.

### Skor → rozet (tasarımda sabit)
| Skor (0–100) | Rozet | Renk | Anlam |
|---|---|---|---|
| 85–100 | 8.5–10 /10 | sage-green `#a9b689` | çok yüksek |
| 75–84  | 7.5–8.4 /10 | mist-blue `#96aed1` | yüksek |
| 70–74  | 7.0–7.4 /10 | yellow `#d8cb8e` | iyi |
| 0–69   | <7.0 /10 | orange `#e6c0a3` | niş / temkinli |

## Aksiyon sınıfları
Bu etiketler PDF'te aksiyon rozeti olarak görünür — birebir bu yazımla kullan:
- `TAKIP ET` — ilginç ama hemen gerekmez.
- `WATCHLIST'E AL` — ileride işimize yarayabilir.
- `DETAYLI İNCELE` — README/docs daha çok okunmalı.
- `WORKFLOW / AGENT FİKRİ` — Claude Code, Codex, Gemini, OpenClaw, Hermes vb. ajanlara skill/cron/workflow olarak uyarlanabilir.
- `HYPE / REDDET` — çok ses var ama pratik fayda düşük.

## Çıktı dili ve format
- Dil: **Türkçe** (teknik terimler İngilizce kalır).
- Format: **HTML** — `assets/report-template.html` tasarımıyla birebir aynı, tek dosyalık
  standalone çıktı (fontlar gömülü, animasyonlar açık). Her seferinde HTML üretilir.
- Mobilde okunabilir kısa paragraflar; uzun ham liste değil, **filtrelenmiş** sonuç.
- Eski "TXT" çıktısı bırakılmıştır; rapor artık `scripts/build_report.py` ile üretilir.
  (PDF gerekirse aynı script `--out *.pdf` ile verir; varsayılan HTML'dir.)
