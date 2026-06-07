#!/usr/bin/env python3
"""
Project Radar — GitHub Trending fetcher (deterministic, zero-dependency).

GitHub Trending'in listesini (dil/tür fark etmeksizin) çeker. Günlük radar için
varsayılan `daily` aralığıdır — "bugün ivme kazanan" repolar. `weekly`/`monthly`
yavaş değiştiği için her gün çekmek tekrara yol açar; bunlar opt-in'dir (haftalık özet
için `--since weekly`). `--since all` üçünü birleştirip `owner/repo` ile tekilleştirir.
İsteğe bağlı dil sayfaları da eklenir.

HTML'i `curl` ile çeker (yoksa stdlib urllib'e düşer), `html.parser`/regex ile ayrıştırır.
Skor ÜRETMEZ ve açıklamayı Türkçeleştirmez — bunlar ajanın işidir (bkz. SKILL.md adım 2).

Çıktı: report-schema.md'deki `trending[]` ile uyumlu, ham bir JSON listesi:
  [{ "owner", "repo", "lang", "stars", "today", "url", "desc" }]

Kullanım:
  python3 scripts/fetch_github_trending.py --out /tmp/github-trending-raw.json   # daily (varsayılan)
  python3 scripts/fetch_github_trending.py --out /tmp/gh.json --since weekly      # haftalık özet
  python3 scripts/fetch_github_trending.py --out /tmp/gh.json --languages "rust,go,python"
"""
from __future__ import annotations
import argparse, html, json, re, shutil, subprocess, sys
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
BASE = "https://github.com/trending"
RANGES = ("daily", "weekly", "monthly")

# repo kartı: <article class="Box-row"> ... </article>
ARTICLE_RE = re.compile(r'<article\s+class="Box-row">(.*?)</article>', re.S)
REPO_RE    = re.compile(r'<h2[^>]*class="h3 lh-condensed"[^>]*>.*?<a[^>]+href="/([^"/]+)/([^"/?#]+)"', re.S)
DESC_RE    = re.compile(r'<p[^>]*class="col-9[^"]*"[^>]*>(.*?)</p>', re.S)
LANG_RE    = re.compile(r'<span\s+itemprop="programmingLanguage"[^>]*>([^<]+)</span>', re.S)
STARS_RE   = re.compile(r'<a[^>]+href="[^"]*/stargazers"[^>]*>(.*?)</a>', re.S)
TODAY_RE   = re.compile(r'<span[^>]*class="[^"]*float-sm-right[^"]*"[^>]*>(.*?)</span>', re.S)
TAG_RE     = re.compile(r'<[^>]+>')
NUM_RE     = re.compile(r'[\d,\.]+')


def fetch(url: str, timeout: int) -> str:
    """HTML'i curl ile çeker; curl yoksa urllib'e düşer."""
    if shutil.which("curl"):
        r = subprocess.run(
            ["curl", "-sL", "-A", UA, "--max-time", str(timeout), url],
            capture_output=True, text=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        print(f"[warn] curl başarısız ({url}): rc={r.returncode}", file=sys.stderr)
    from urllib.request import Request, urlopen
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _clean(s: str) -> str:
    return html.unescape(TAG_RE.sub("", s or "")).strip()


def _num(s: str) -> int:
    m = NUM_RE.search(s or "")
    if not m:
        return 0
    try:
        return int(m.group(0).replace(",", "").replace(".", ""))
    except ValueError:
        return 0


def parse_trending(html_text: str) -> list[dict]:
    out: list[dict] = []
    for block in ARTICLE_RE.findall(html_text):
        repo_m = REPO_RE.search(block)
        if not repo_m:
            continue
        owner, repo = repo_m.group(1).strip(), repo_m.group(2).strip()
        desc_m, lang_m = DESC_RE.search(block), LANG_RE.search(block)
        stars_m, today_m = STARS_RE.search(block), TODAY_RE.search(block)
        out.append({
            "owner": owner,
            "repo":  repo,
            "lang":  _clean(lang_m.group(1)) if lang_m else "—",
            "stars": _num(_clean(stars_m.group(1))) if stars_m else 0,
            "today": _num(_clean(today_m.group(1))) if today_m else 0,
            "url":   f"https://github.com/{owner}/{repo}",
            "desc":  _clean(desc_m.group(1)) if desc_m else "",
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="GitHub Trending'in tam listesini çeker (ham JSON).")
    ap.add_argument("--out", required=True, help="çıktı JSON dosyası")
    ap.add_argument("--since", choices=["daily", "weekly", "monthly", "all"], default="daily",
                    help="zaman aralığı (varsayılan: daily; haftalık özet için weekly; all = üçü birleşik)")
    ap.add_argument("--languages", default="",
                    help="opsiyonel virgülle ayrılmış dil listesi (ör. 'rust,go,python')")
    ap.add_argument("--timeout", type=int, default=30, help="istek zaman aşımı (sn)")
    args = ap.parse_args()

    ranges = list(RANGES) if args.since == "all" else [args.since]
    langs = [l.strip() for l in args.languages.split(",") if l.strip()]

    # daily/weekly/monthly sırası önemli: dedup ilk görüleni (daily) korur
    seen: dict[tuple, dict] = {}
    stats: list[str] = []
    for since in ranges:
        urls = [f"{BASE}?since={since}"]
        urls += [f"{BASE}/{lang}?since={since}" for lang in langs]
        for url in urls:
            try:
                repos = parse_trending(fetch(url, args.timeout))
            except Exception as e:
                print(f"[warn] çekilemedi {url}: {e}", file=sys.stderr)
                continue
            added = 0
            for r in repos:
                key = (r["owner"].lower(), r["repo"].lower())
                if key not in seen:
                    seen[key] = r
                    added += 1
            stats.append(f"{url} → {len(repos)} repo ({added} yeni)")

    result = list(seen.values())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n".join(f"  {s}" for s in stats), file=sys.stderr)
    print(f"[ok] {len(result)} tekil repo yazıldı: {out}", file=sys.stderr)
    if not result:
        print("[warn] hiç repo bulunamadı — GitHub HTML yapısı değişmiş olabilir.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
