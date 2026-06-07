# Project Radar — Rapor Veri Şeması

`build_report.py` bu şemaya uyan bir JSON dosyası okur ve **tek dosyalık standalone
HTML** rapor üretir (referans tasarımla birebir aynı). Eski `daily-report-template.txt`'in
tüm bölümleri burada JSON alanlarına eşlenmiştir. Boş bırakılan bölümler raporda
otomatik gizlenir — **uydurma içerik ekleme**.

## Üst seviye alanlar

| JSON alanı | Eski şablon bölümü | PDF bölümü |
|---|---|---|
| `date`, `date_human` | başlık tarihi | header eyebrow |
| `candidates[]` | EN IYI ADAYLAR | 01 — En iyi adaylar (en iyi **4** aday) |
| `trending[]` | (GitHub trending) | 02 — Bugün trend olan depolar |
| `topics[]` | BUGUNUN KONU BASLIKLARI | 03 — Bugün konuşulanlar |
| `agent_ideas[]` | WORKFLOW / AGENT FIKIRLERI | 04 — Workflow / Agent fikirleri |
| `watchlist[]` | WATCHLIST ÖNERILERI | 05 — Watchlist önerileri |
| `hype[]` | HYPE / SUPHELI / REDDEDILENLER | 06 — Hype / şüpheli / reddedilenler |

> Not: NOTLAR bölümü ("keşif amaçlıdır, test yapılmaz") PDF footer'ında sabittir.

## Alan tanımları

```jsonc
{
  "date": "2026-06-07",                 // ISO; sıralama/dosya adı için
  "date_human": "7 Haziran 2026",       // header'da görünen tarih

  "candidates": [                       // tüm kaynaklardan EN İYİ 4 ADAY (zengin kart)
    {
      "name":     "Understand-Anything",          // zorunlu — proje/app adı
      "owner":    "Lum1104",                       // opsiyonel — GitHub owner
      "url":      "https://github.com/...",        // opsiyonel
      "source":   "GitHub Trending",               // Kaynak (pill)
      "category": "Coding agents",                 // Kategori (pill)
      "score":    85,                              // 0–100
      "what":     "Ne yapıyor ...",
      "why":      "Neden gündemde ...",
      "benefit":  "Bizim işimize nerede yarar ...",
      "llm":      "LLM / ajan uyumu — hangi araçlarla çalışır/bağlanır (Claude, Claude Code, OpenAI, Codex, Hermes, OpenCode, Cursor, Gemini ...); MCP/API/CLI desteği",
      "adoption": "Kurulum/benimsenme sinyali ...",
      "risks":    "Riskler ...",
      "action":   "DETAYLI İNCELE"                 // aksiyon sınıfı (bkz. sources-and-scoring.md)
    }
  ],

  "trending": [                         // GitHub Trending — TAM liste (tüm diller/türler)
    {
      "owner": "Lum1104", "repo": "Understand-Anything",
      "lang":  "TypeScript",            // dil noktası rengi otomatik (tüm diller desteklenir)
      "stars": 36028, "today": 4697,    // tam sayı; PDF'te 36.028 / 4.697 olarak biçimlenir
      "score": 85,                      // 0–100
      "desc":  "Türkçe açıklama ...",
      "note":  "Opsiyonel uyarı notu ..."   // varsa italik dipnot
    }
    // Kaynak: scripts/fetch_github_trending.py çıktısı (owner/repo/lang/stars/today/url/desc);
    // score + Türkçe desc agent tarafından eklenir. Sabit ~14 sınırı yoktur — tam liste taşınır.
  ],

  "topics": [                           // platformlar arası konu başlıkları
    {
      "title": "MCP / integrations",
      "items": [
        { "text": "...", "source": "Hacker News", "url": "https://..." }   // url opsiyonel
      ]
    }
  ],

  "agent_ideas": [ "..." ],             // düz metin maddeler (Claude Code/Codex/Gemini/OpenClaw/Hermes vb.)

  "watchlist": [
    { "name": "...", "url": "https://...", "note": "..." }   // url/note opsiyonel
  ],

  "hype": [
    { "name": "...", "url": "https://...",                  // url opsiyonel
      "why_suspect": "Neden şüpheli ...",
      "why_noaction": "Neden bugün aksiyon yok ..." }
  ]
}
```

## Sıralama ve sayı
- `candidates`: **en iyi 4 aday** konur (3 değil). Skora göre azalan sıralanır.
- `trending`: **tam GitHub trending listesi** (tüm diller/türler). Sabit üst sınır yoktur;
  skora göre azalan sıralanır (eşitlik bozucu: `today` azalan). Render kapsız basar.
- `rank` her iki listede otomatik atanır; elle vermene gerek yok.

## Önerilen konu başlıkları (`topics[].title`)
Agent OS / AI workflow · MCP / integrations · Coding agents · Local/self-hosted AI ·
Content/video automation · Second brain / knowledge tools · Sales/CRM/lead automation ·
**Genel teknoloji gündemi** · **Ürün / launch gündemi**.
Sadece o gün gerçekten içerik olan başlıkları ekle.

Geçerli `topics[].items[].source` değerleri (örnek): GitHub · Hacker News · Product Hunt ·
Reddit · Google Trends · YouTube · X / Twitter · Web · Latent Space · TLDR AI.
