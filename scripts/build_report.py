#!/usr/bin/env python3
"""
Project Radar — report builder.

Pipeline:  report-data.json  ->  (Jinja2 + design template)  ->  HTML  [-> PDF]

DEFAULT output is a single HTML file identical to the reference design (animations on).
The report uses a single font — Inter — loaded from Google Fonts in the template
(SIL OFL, free, available everywhere; no fonts are bundled with the skill). Offline,
it falls back to a system sans.
PDF (--out *.pdf or --format pdf) is a MOBILE-optimised, A4-portrait, paginated layout:
two compact cards per row, rendered via headless Chromium. Easy to open and read on a
phone (swipe page by page); cards never split across page breaks (break-inside:avoid).
The mobile layout lives in the template under `body.pdf`; the HTML output is unaffected.

Usage:
  python build_report.py --data report-data.json --out Project-Radar-2026-06-07.html
  python build_report.py --data report-data.json --out Project-Radar-2026-06-07.pdf
"""
from __future__ import annotations
import argparse, json, os, sys, shutil, subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
TEMPLATE = "report-template.html"

# language dot colours (from the reference design palette)
LANG_COLORS = {
    "TypeScript": "#96aed1", "TSX": "#96aed1", "JavaScript": "#d8cb8e",
    "Python": "#a9b689", "C#": "#dfceea", "Shell": "#e2bfce", "HTML": "#e6c0a3",
    "Go": "#bed0e3", "Rust": "#e6c0a3", "Jupyter Notebook": "#d8cb8e", "—": "#c9cabf",
    # GitHub Trending tüm dilleri kapsadığı için palet renkleriyle genişletildi
    "C++": "#96aed1", "C": "#bed0e3", "Java": "#e6c0a3", "Kotlin": "#dfceea",
    "Swift": "#e6c0a3", "Ruby": "#e2bfce", "PHP": "#dfceea", "Dart": "#bed0e3",
    "Vue": "#a9b689", "Svelte": "#e6c0a3", "Zig": "#e6c0a3", "Lua": "#96aed1",
    "Elixir": "#dfceea", "Scala": "#e2bfce", "Haskell": "#dfceea", "R": "#bed0e3",
    "Julia": "#dfceea", "Dockerfile": "#bed0e3", "CSS": "#96aed1", "SCSS": "#e2bfce",
    "MDX": "#d8cb8e", "Astro": "#e6c0a3", "Objective-C": "#bed0e3", "Roff": "#c9cabf",
}

# action class -> chip background
ACTION_COLORS = {
    "WORKFLOW / AGENT FİKRİ": "#a9b689",
    "HERMES WORKFLOW FİKRİ": "#a9b689",   # geri uyum (eski etiket)
    "DETAYLI İNCELE": "#96aed1",
    "WATCHLIST'E AL": "#dfceea",
    "TAKIP ET": "#d8cb8e",
    "HYPE / REDDET": "#e4bdbd",
}

EXT_ICO  = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M5 3h8v8h-2V6.4l-6.3 6.3-1.4-1.4L9.6 5H5V3z"/></svg>'
STAR_ICO = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1.3l1.8 3.9 4.2.5-3.1 2.9.8 4.2L8 11.2 4.3 13l.8-4.2L2 5.9l4.2-.5L8 1.3z"/></svg>'
UP_ICO   = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 3l5 6H3l5-6z"/></svg>'


def score_bg(s: float) -> str:
    """0-100 usefulness score -> badge background (matches the reference thresholds)."""
    if s >= 85: return "#a9b689"   # sage  — çok yüksek
    if s >= 75: return "#96aed1"   # mist  — yüksek
    if s >= 70: return "#d8cb8e"   # yellow— iyi
    return "#e6c0a3"               # orange— niş/temkinli


def action_bg(a: str) -> str:
    return ACTION_COLORS.get((a or "").strip().upper(), "#d8cb8e")


def lang_color(lang: str) -> str:
    return LANG_COLORS.get(lang, "#c9cabf")


def tr_num(n) -> str:
    """Turkish thousands separator (1.234.567), like toLocaleString('tr-TR')."""
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(n)


def strip_scheme(url: str) -> str:
    return (url or "").replace("https://", "").replace("http://", "")


def render_html(data: dict, body_class: str = "") -> str:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(
        loader=FileSystemLoader(str(ASSETS)),
        autoescape=select_autoescape(["html"]),
    )
    from markupsafe import Markup
    env.filters["tr_num"] = tr_num
    env.filters["strip_scheme"] = strip_scheme
    tpl = env.get_template(TEMPLATE)

    # sort like the reference: by score desc, then trending momentum desc
    candidates = sorted(data.get("candidates", []),
                        key=lambda x: (-x.get("score", 0), -x.get("rank", 0)))
    for i, c in enumerate(candidates, 1):
        c.setdefault("rank", i); c["rank"] = i
    trending = sorted(data.get("trending", []),
                      key=lambda x: (-x.get("score", 0), -x.get("today", 0)))
    for i, d in enumerate(trending, 1):
        d["rank"] = i

    return tpl.render(
        body_class=body_class,
        date_human=data.get("date_human") or data.get("date", ""),
        candidates=candidates,
        trending=trending,
        topics=data.get("topics", []),
        agent_ideas=data.get("agent_ideas", data.get("hermes_ideas", [])),
        watchlist=data.get("watchlist", []),
        hype=data.get("hype", []),
        score_bg=score_bg, action_bg=action_bg, lang_color=lang_color,
        ext_ico=Markup(EXT_ICO), star_ico=Markup(STAR_ICO), up_ico=Markup(UP_ICO),
    )


def html_to_pdf_playwright(html: str, out: Path, scale: int) -> bool:
    """Render via headless Chromium as a paginated, mobile-friendly A4 portrait PDF.

    Print emulation honours the template's `body.pdf` rules (2 compact cards/row);
    Chromium paginates into A4 pages and `break-inside:avoid` keeps cards whole.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    # write HTML to a temp file so the headless browser can load it via file://
    # (PID-suffixed so concurrent renders don't overwrite each other)
    tmp = ASSETS / f"._render-{os.getpid()}.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 800, "height": 1130},
                                    device_scale_factor=scale)
            page.goto(tmp.as_uri(), wait_until="networkidle")
            try:
                page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(400)
            page.pdf(path=str(out), format="A4", print_background=True,
                     margin={"top": "10mm", "bottom": "10mm",
                             "left": "8mm", "right": "8mm"})
            browser.close()
        return True
    finally:
        tmp.unlink(missing_ok=True)


def html_to_pdf_wkhtmltopdf(html: str, out: Path) -> bool:
    if not shutil.which("wkhtmltopdf"):
        return False
    tmp = ASSETS / f"._render-{os.getpid()}.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        subprocess.run(
            ["wkhtmltopdf", "--enable-local-file-access", "--print-media-type",
             "--page-size", "A4", "--orientation", "Portrait",
             "--margin-top", "10mm", "--margin-bottom", "10mm",
             "--margin-left", "8mm", "--margin-right", "8mm",
             str(tmp), str(out)],
            check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"[wkhtmltopdf] failed: {e}", file=sys.stderr)
        return False
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build the Project Radar report (HTML by default, like the reference design).")
    ap.add_argument("--data", required=True, help="path to report-data.json")
    ap.add_argument("--out", required=True,
                    help="output file; .html (default) for the standalone report, .pdf for PDF")
    ap.add_argument("--format", choices=["auto", "html", "pdf"], default="auto",
                    help="override output format (default: inferred from --out, fallback html)")
    ap.add_argument("--width", type=int, default=1320,
                    help="(deprecated) ignored — PDF now uses a fixed A4 portrait page")
    ap.add_argument("--scale", type=int, default=2, help="PDF device scale factor (default 2)")
    args = ap.parse_args()

    try:
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[error] data file not found: {args.data}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"[error] invalid JSON in {args.data}: {e}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fmt = args.format
    if fmt == "auto":
        fmt = "pdf" if out.suffix.lower() == ".pdf" else "html"

    if fmt == "html":
        # single file, animations on; Inter loaded from Google Fonts in the template
        html = render_html(data, body_class="")
        out.write_text(html, encoding="utf-8")
        print(f"[ok] HTML written: {out}")
        return 0

    # PDF: mobile A4 layout (body.pdf), static (no animations mid-fade)
    html = render_html(data, body_class="pdf")
    if html_to_pdf_playwright(html, out, args.scale):
        print(f"[ok] PDF (Chromium): {out}")
        return 0
    print("[warn] Playwright/Chromium unavailable — trying wkhtmltopdf fallback.",
          file=sys.stderr)
    if html_to_pdf_wkhtmltopdf(html, out):
        print(f"[ok] PDF (wkhtmltopdf): {out}")
        return 0
    fallback = out.with_suffix(".html")
    fallback.write_text(render_html(data, body_class=""), encoding="utf-8")
    print(f"[warn] No PDF engine available. HTML written instead: {fallback}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
