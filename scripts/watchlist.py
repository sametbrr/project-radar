#!/usr/bin/env python3
"""
Project Radar — Watchlist yöneticisi (kalıcı).

İncelemeye değer bulduğun GitHub repolarını ayrı bir watchlist klasörüne alır; projenin
GitHub metadata'sı + README'sini **okuyarak** (clone/install YOK — keşif-only) orta-derinlikte
bir detay raporu üretir. "getir" denince tüm liste dosya referanslarıyla listelenir.

Klasör (default `<SKILL_DIR>/watchlist`, `--dir` veya env PROJECT_RADAR_WATCHLIST_DIR ile değişir):
  index.json / index.md
  reports/<owner>__<repo>.raw.json       (çekilen metadata + README)
  reports/<owner>__<repo>.analysis.json  (ajanın yazdığı analiz — tek kaynak)
  reports/<owner>__<repo>.md / .html      (render edilen detay)

Komutlar:
  python3 scripts/watchlist.py add <owner/repo | github-url> [--dir D]
  python3 scripts/watchlist.py render <owner__repo>            [--dir D]
  python3 scripts/watchlist.py list                            [--dir D]
  python3 scripts/watchlist.py remove <owner__repo>            [--dir D]
  python3 scripts/watchlist.py path                            [--dir D]

Tipik akış (ajan): add  ->  reports/<slug>.analysis.json'u doldur  ->  render  ->  list
"""
from __future__ import annotations
import argparse, base64, datetime, json, os, re, shutil, subprocess, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
WL_TEMPLATE = "watchlist-report-template.html"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# build_report.py yardımcılarını paylaş (DRY); başarısız olursa yerel fallback
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_report import score_bg, lang_color, tr_num
except Exception:                                                  # pragma: no cover
    def score_bg(s):
        s = s or 0
        return "#a9b689" if s >= 85 else "#96aed1" if s >= 75 else "#d8cb8e" if s >= 70 else "#e6c0a3"
    def lang_color(_): return "#c9cabf"
    def tr_num(n):
        try: return f"{int(n):,}".replace(",", ".")
        except (TypeError, ValueError): return str(n)


# ----------------------------------------------------------------------------- helpers
def resolve_dir(arg_dir: str | None) -> Path:
    d = arg_dir or os.environ.get("PROJECT_RADAR_WATCHLIST_DIR") or str(SKILL_DIR / "watchlist")
    return Path(d).expanduser().resolve()


def parse_repo(s: str) -> tuple[str, str]:
    """owner/repo, github URL veya github.com/owner/repo -> (owner, repo)."""
    s = s.strip()
    s = re.sub(r'^https?://', '', s)
    s = re.sub(r'^github\.com/', '', s)
    s = s.split("?")[0].split("#")[0].rstrip("/")
    s = re.sub(r'\.git$', '', s)
    parts = [p for p in s.split("/") if p]
    if len(parts) < 2:
        raise SystemExit(f"[hata] repo çözülemedi: '{s}' (owner/repo veya github URL ver)")
    return parts[0], parts[1]


def slug_of(owner: str, repo: str) -> str:
    return f"{owner}__{repo}"


def _gh(args: list[str]) -> str | None:
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 and r.stdout.strip() else None


def _curl(url: str, accept: str = "application/vnd.github+json", timeout: int = 30) -> str | None:
    if not shutil.which("curl"):
        from urllib.request import Request, urlopen
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": accept})
            with urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception:
            return None
    r = subprocess.run(
        ["curl", "-sL", "-H", f"User-Agent: {UA}", "-H", f"Accept: {accept}",
         "--max-time", str(timeout), url],
        capture_output=True, text=True)
    return r.stdout if r.returncode == 0 and r.stdout.strip() else None


def fetch_repo(owner: str, repo: str) -> dict:
    """GitHub'dan metadata + README çeker (gh varsa onunla, yoksa curl/unauth)."""
    raw_meta = _gh([f"repos/{owner}/{repo}"]) or _curl(f"https://api.github.com/repos/{owner}/{repo}")
    if not raw_meta:
        raise SystemExit(f"[hata] metadata çekilemedi: {owner}/{repo} (GitHub API limiti/erişim?)")
    m = json.loads(raw_meta)
    if m.get("message") and not m.get("full_name"):
        raise SystemExit(f"[hata] GitHub: {m.get('message')} ({owner}/{repo})")

    readme = ""
    rd = _gh([f"repos/{owner}/{repo}/readme"]) or _curl(f"https://api.github.com/repos/{owner}/{repo}/readme")
    if rd:
        try:
            j = json.loads(rd)
            if j.get("content"):
                readme = base64.b64decode(j["content"]).decode("utf-8", "replace")
        except Exception:
            pass

    lic = (m.get("license") or {})
    return {
        "owner": owner, "repo": repo,
        "name": m.get("name") or repo,
        "url": m.get("html_url") or f"https://github.com/{owner}/{repo}",
        "homepage": (m.get("homepage") or "").strip(),
        "description": m.get("description") or "",
        "meta": {
            "stars": m.get("stargazers_count", 0),
            "forks": m.get("forks_count", 0),
            "language": m.get("language") or "—",
            "license": lic.get("spdx_id") or lic.get("name") or "—",
            "last_activity": (m.get("pushed_at") or "")[:10],
            "topics": m.get("topics") or [],
            "archived": bool(m.get("archived")),
        },
        "readme": readme,
        "fetched_at": datetime.date.today().isoformat(),
    }


# ----------------------------------------------------------------------------- index
def load_index(wl: Path) -> dict:
    f = wl / "index.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {"items": []}


def save_index(wl: Path, idx: dict) -> None:
    (wl / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    write_index_md(wl, idx)


def find_item(idx: dict, slug: str) -> dict | None:
    return next((it for it in idx["items"] if it["slug"] == slug), None)


def upsert_item(idx: dict, entry: dict) -> dict:
    existing = find_item(idx, entry["slug"])
    if existing:
        existing.update({k: v for k, v in entry.items() if k != "date_added"})
        return existing
    idx["items"].append(entry)
    return entry


def write_index_md(wl: Path, idx: dict) -> None:
    lines = ["# Project Radar — Watchlist", "",
             f"Toplam **{len(idx['items'])}** kayıt. Güncellendi: {datetime.date.today().isoformat()}", "",
             "| Proje | Kategori | Skor | Aksiyon | Eklendi | Durum | Rapor |",
             "|---|---|---|---|---|---|---|"]
    for it in sorted(idx["items"], key=lambda x: (-(x.get("score") or 0), x["slug"])):
        md = it.get("report_md") or ""
        html = it.get("report_html") or ""
        refs = " · ".join(filter(None, [
            f"[md]({md})" if md else "", f"[html]({html})" if html else ""])) or "—"
        lines.append("| [{name}]({url}) | {cat} | {score} | {action} | {added} | {status} | {refs} |".format(
            name=it.get("name", it["slug"]), url=it.get("url", ""),
            cat=it.get("category") or "—",
            score=(str(it["score"]) + "/100") if it.get("score") is not None else "—",
            action=it.get("action") or "—", added=it.get("date_added", "—"),
            status=it.get("status", "—"), refs=refs))
    (wl / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- render (md + html)
def _md_section(title: str, body: str) -> str:
    return f"## {title}\n{(body or '').strip() or '_(boş)_'}\n"


def render_markdown(a: dict) -> str:
    m = a.get("meta", {})
    head = [f"# {a.get('name','')}", ""]
    if a.get("summary"):
        head += [f"> {a['summary']}", ""]
    facts = [
        f"- **Repo:** [{a.get('owner','')}/{a.get('repo','')}]({a.get('url','')}) · "
        f"**Dil:** {m.get('language','—')} · **Lisans:** {m.get('license','—')}",
        f"- **Yıldız:** {tr_num(m.get('stars',0))} · **Fork:** {tr_num(m.get('forks',0))} · "
        f"**Son aktivite:** {m.get('last_activity','—')}"
        + (" · **arşivlenmiş**" if m.get("archived") else ""),
        f"- **Kategori:** {a.get('category') or '—'} · **Skor:** "
        f"{a.get('score','—')}/100 · **Aksiyon:** {a.get('action') or '—'}",
    ]
    if a.get("homepage"):
        facts.append(f"- **Site:** {a['homepage']}")
    if m.get("topics"):
        facts.append(f"- **Topics:** {', '.join(m['topics'])}")
    body = [
        _md_section("Ne yapıyor", a.get("what", "")),
        _md_section("Kurulum / benimsenme", a.get("install", "")),
        _md_section("LLM / MCP uyumu", a.get("llm", "")),
        _md_section("Kullanım senaryosu", a.get("use_case", "")),
        _md_section("Riskler", a.get("risks", "")),
        _md_section("Karar", a.get("decision", "")),
    ]
    foot = ("\n---\n_Project Radar watchlist · eklendi "
            f"{a.get('date_added','')} · kaynak: README + GitHub metadata "
            "(orta derinlik, keşif-only)_\n")
    return "\n".join(head + facts + [""] + body) + foot


def render_html(a: dict) -> str:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(loader=FileSystemLoader(str(ASSETS)),
                      autoescape=select_autoescape(["html"]))
    env.filters["tr_num"] = tr_num
    tpl = env.get_template(WL_TEMPLATE)
    return tpl.render(a=a, m=a.get("meta", {}), score_bg=score_bg, lang_color=lang_color)


# ----------------------------------------------------------------------------- commands
def cmd_add(args) -> int:
    wl = resolve_dir(args.dir)
    (wl / "reports").mkdir(parents=True, exist_ok=True)
    owner, repo = parse_repo(args.target)
    slug = slug_of(owner, repo)
    data = fetch_repo(owner, repo)

    (wl / "reports" / f"{slug}.raw.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # analysis.json stub — sadece yoksa oluştur (mevcut analizi ezme)
    apath = wl / "reports" / f"{slug}.analysis.json"
    if not apath.exists():
        stub = {
            "name": data["name"], "owner": owner, "repo": repo, "url": data["url"],
            "homepage": data["homepage"], "category": "", "score": None, "action": "WATCHLIST'E AL",
            "summary": "", "what": "", "install": "", "llm": "", "use_case": "",
            "risks": "", "decision": "", "meta": data["meta"],
            "date_added": datetime.date.today().isoformat(),
        }
        apath.write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding="utf-8")

    idx = load_index(wl)
    upsert_item(idx, {
        "slug": slug, "name": data["name"], "owner": owner, "repo": repo,
        "url": data["url"], "homepage": data["homepage"],
        "category": None, "score": None, "action": "WATCHLIST'E AL",
        "status": "needs-analysis",
        "date_added": datetime.date.today().isoformat(),
        "report_md": None, "report_html": None,
    })
    save_index(wl, idx)

    print(f"[ok] eklendi: {slug}  (★{tr_num(data['meta']['stars'])}, {data['meta']['language']})", file=sys.stderr)
    print(f"      raw:      reports/{slug}.raw.json", file=sys.stderr)
    print(f"      analiz:   reports/{slug}.analysis.json  (Orta derinlikte doldur)", file=sys.stderr)
    print(f"      sonra:    python3 scripts/watchlist.py render {slug}" +
          (f" --dir {args.dir}" if args.dir else ""), file=sys.stderr)
    print(slug)   # stdout = slug (pipeline için)
    return 0


def cmd_render(args) -> int:
    wl = resolve_dir(args.dir)
    slug = args.slug
    apath = wl / "reports" / f"{slug}.analysis.json"
    if not apath.exists():
        raise SystemExit(f"[hata] analiz yok: {apath} (önce 'add' ve analysis.json'u doldur)")
    a = json.loads(apath.read_text(encoding="utf-8"))
    a.setdefault("meta", {})

    md_path = wl / "reports" / f"{slug}.md"
    html_path = wl / "reports" / f"{slug}.html"
    md_path.write_text(render_markdown(a), encoding="utf-8")
    html_path.write_text(render_html(a), encoding="utf-8")

    idx = load_index(wl)
    it = find_item(idx, slug) or {"slug": slug, "date_added": a.get("date_added", datetime.date.today().isoformat())}
    it.update({
        "name": a.get("name", slug), "owner": a.get("owner"), "repo": a.get("repo"),
        "url": a.get("url"), "homepage": a.get("homepage"),
        "category": a.get("category"), "score": a.get("score"), "action": a.get("action"),
        "status": "done",
        "report_md": f"reports/{slug}.md", "report_html": f"reports/{slug}.html",
    })
    if not find_item(idx, slug):
        idx["items"].append(it)
    save_index(wl, idx)

    print(f"[ok] render: {slug}", file=sys.stderr)
    print(f"      md:   {md_path}", file=sys.stderr)
    print(f"      html: {html_path}", file=sys.stderr)
    return 0


def cmd_list(args) -> int:
    wl = resolve_dir(args.dir)
    idx = load_index(wl)
    items = sorted(idx["items"], key=lambda x: (-(x.get("score") or 0), x["slug"]))
    print(f"Watchlist — {len(items)} kayıt   (dir: {wl})")
    if not items:
        print("  (boş — 'watchlist.py add <owner/repo>' ile ekle)")
        return 0
    for it in items:
        sc = f"{it['score']}/100" if it.get("score") is not None else "—"
        print(f"\n[{it.get('status','—'):>13}] {it.get('name', it['slug'])}  "
              f"· {it.get('category') or '—'} · {sc} · {it.get('action') or '—'}  ({it.get('date_added','—')})")
        print(f"               {it.get('url','')}")
        for label, key in (("md", "report_md"), ("html", "report_html")):
            if it.get(key):
                print(f"               {label}:  {wl / it[key]}")
    print(f"\nİndeks: {wl / 'index.md'}  ·  {wl / 'index.json'}")
    return 0


def cmd_remove(args) -> int:
    wl = resolve_dir(args.dir)
    slug = args.slug
    for ext in ("raw.json", "analysis.json", "md", "html"):
        (wl / "reports" / f"{slug}.{ext}").unlink(missing_ok=True)
    idx = load_index(wl)
    n = len(idx["items"])
    idx["items"] = [it for it in idx["items"] if it["slug"] != slug]
    save_index(wl, idx)
    print(f"[ok] silindi: {slug}" if len(idx["items"]) < n else f"[uyarı] bulunamadı: {slug}", file=sys.stderr)
    return 0


def cmd_path(args) -> int:
    print(resolve_dir(args.dir))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Project Radar watchlist yöneticisi.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("add", "render", "list", "remove", "path"):
        sp = sub.add_parser(name)
        sp.add_argument("--dir", help="watchlist klasörü (default <SKILL_DIR>/watchlist veya env)")
        if name in ("add",):
            sp.add_argument("target", help="owner/repo veya github URL")
        if name in ("render", "remove"):
            sp.add_argument("slug", help="<owner>__<repo>")
    args = ap.parse_args()
    return {"add": cmd_add, "render": cmd_render, "list": cmd_list,
            "remove": cmd_remove, "path": cmd_path}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
