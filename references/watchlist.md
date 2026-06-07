# Project Radar — Watchlist (kalıcı)

Günlük rapordaki **"Watchlist önerileri"** geçici bir *öneri* listesidir. Bu doküman ise
kullanıcının **curate ettiği kalıcı watchlist**'i tanımlar: incelemeye değer bulunan GitHub
repoları ayrı bir klasöre alınır, metadata + README **okunarak** orta-derinlikte bir detay
raporu (Markdown + imza HTML) üretilir.

**Keşif-only:** clone / install / build / run YOK. Yalnızca GitHub API/raw ile okuma yapılır.

## Klasör yapısı
Default `<SKILL_DIR>/watchlist`; `--dir` veya env `PROJECT_RADAR_WATCHLIST_DIR` ile değişir.
```
watchlist/
  index.json                       # kanonik liste (dedup + "getir")
  index.md                         # insan-okur tablo, her rapora link
  reports/
    <owner>__<repo>.raw.json       # çekilen metadata + README (kaynak)
    <owner>__<repo>.analysis.json  # ajanın yazdığı analiz — TEK KAYNAK
    <owner>__<repo>.md             # render edilen detay (Markdown)
    <owner>__<repo>.html           # render edilen detay (imza HTML)
```

## Komutlar — `scripts/watchlist.py`
```bash
python3 scripts/watchlist.py add <owner/repo | github-url> [--dir D]
python3 scripts/watchlist.py render <owner__repo>            [--dir D]
python3 scripts/watchlist.py list                            [--dir D]
python3 scripts/watchlist.py remove <owner__repo>            [--dir D]
python3 scripts/watchlist.py path                            [--dir D]
```

## İş akışı (ajan)
1. **Ekle:** `add` repoyu çözer, GitHub'dan metadata + README çeker (`gh` varsa onunla, yoksa
   curl/unauth), `reports/<slug>.raw.json` yazar ve `reports/<slug>.analysis.json` **stub**'ı
   (kimlik + meta dolu, analiz alanları boş) oluşturur; index'e `needs-analysis` girer.
2. **Analiz yaz:** `reports/<slug>.raw.json`'daki README'yi oku, `reports/<slug>.analysis.json`'u
   **Orta derinlikte** doldur (aşağıdaki şema). Tüm metin **Türkçe**, teknik terimler İngilizce.
3. **Render:** `render <slug>` → `.md` + `.html` üretir, index'i `done` + link alanlarıyla günceller.
4. **Getir:** `list` → tüm kayıtları **dosya referanslarıyla** (md/html yolları) listeler.

## Analiz şeması — `reports/<slug>.analysis.json` (Orta derinlik)
```jsonc
{
  "name": "...", "owner": "...", "repo": "...", "url": "...", "homepage": "...",
  "category": "Sales / CRM",      // kısa kategori
  "score": 85,                    // 0–100 (rapor /10 rozet)
  "action": "DETAYLI İNCELE",     // aksiyon sınıfı (bkz. sources-and-scoring.md)
  "summary": "Tek cümlelik özet",
  "what":     "Ne yapıyor ...",
  "install":  "Kurulum / benimsenme sinyali ...",
  "llm":      "LLM / MCP / API uyumu ...",
  "use_case": "Bizim işimize nerede yarar ...",
  "risks":    "Riskler ...",
  "decision": "Kısa karar / öneri ...",
  "meta": { "stars":0,"forks":0,"language":"...","license":"...",
            "last_activity":"YYYY-MM-DD","topics":[],"archived":false },
  "date_added": "YYYY-MM-DD"
}
```
> **Orta derinlik:** GitHub metadata + README okunur; `docs/` ve landing page taranmaz,
> ayrı "mimari" bölümü yoktur. (Daha derin inceleme istenirse manuel, ayrı adımdır.)

## Tetikleyiciler
- **Ekle:** "<repo>'yu watchliste ekle", "add <repo> to watchlist", "bunu watchlist'e al"
  (belirli bir repo/URL verildiğinde).
- **Getir:** "watchlist'i getir", "watchlist'tekileri getir", "watchlist listesi", "show watchlist".
- **Çıkar:** "watchlist'ten <repo> çıkar", "remove <repo> from watchlist".

## Günlük rapordan farkı
- Günlük rapordaki `watchlist[]` → "Watchlist önerileri": o günkü taramadan çıkan **öneriler**.
- Buradaki kalıcı watchlist → kullanıcının onayıyla eklenmiş, **detay raporu üretilmiş** kayıtlar.
