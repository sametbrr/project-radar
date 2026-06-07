#!/usr/bin/env python3
"""
Project Radar — report builder.

Pipeline:  report-data.json  ->  (Jinja2 + design template)  ->  HTML  [-> PDF]

DEFAULT output is a single HTML file identical to the reference design (animations on).
The report uses a single font — Inter — loaded from Google Fonts in the template
(SIL OFL, free, available everywhere; no fonts are bundled with the skill). Offline,
it falls back to a system sans.
PDF is optional (--out *.pdf or --format pdf): rendered via headless Chromium as one
tall page = full content height, so cards never split across page breaks.

Usage:
  python build_report.py --data report-data.json --out Project-Radar-2026-06-07.html
  python build_report.py --data report-data.json --out Project-Radar-2026-06-07.pdf
"""
from __future__ import annotations
import argparse, json, sys, shutil, subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
TEMPLATE = "report-template.html"

# language dot colours (from the reference design)
LANG_COLORS = {
    "TypeScript": "#96aed1", "TSX": "#96aed1", "JavaScript": "#d8cb8e",
    "Python": "#a9b689", "C#": "#dfceea", "Shell": "#e2bfce", "HTML": "#e6c0a3",
    "Go": "#bed0e3", "Rust": "#e6c0a3", "Jupyter Notebook": "#d8cb8e", "—": "#c9cabf",
}

# action class -> chip background
ACTION_COLORS = {
    "HERMES WORKFLOW FİKRİ": "#a9b689",
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
        hermes_ideas=data.get("hermes_ideas", []),
        watchlist=data.get("watchlist", []),
        hype=data.get("hype", []),
        score_bg=score_bg, action_bg=action_bg, lang_color=lang_color,
        ext_ico=Markup(EXT_ICO), star_ico=Markup(STAR_ICO), up_ico=Markup(UP_ICO),
    )


def html_to_pdf_playwright(html: str, out: Path, width: int, scale: int) -> bool:
    """Render via headless Chromium as one tall page = full content height."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    # write HTML to a temp file so the headless browser can load it via file://
    tmp = ASSETS / "._render.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": width, "height": 1200},
                                    device_scale_factor=scale)
            page.goto(tmp.as_uri(), wait_until="networkidle")
            try:
                page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(400)
            full_h = page.evaluate(
                "Math.ceil(Math.max(document.body.scrollHeight,"
                "document.documentElement.scrollHeight))")
            # PDF spec caps page height ~14400pt; guard with multi-page fallback
            if full_h * 0.75 > 14000:
                page.pdf(path=str(out), width=f"{width}px", format=None,
                         print_background=True, prefer_css_page_size=False,
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            else:
                page.pdf(path=str(out), width=f"{width}px", height=f"{full_h}px",
                         print_background=True,
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            browser.close()
        return True
    finally:
        tmp.unlink(missing_ok=True)


def html_to_pdf_wkhtmltopdf(html: str, out: Path, width: int) -> bool:
    if not shutil.which("wkhtmltopdf"):
        return False
    tmp = ASSETS / "._render.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        subprocess.run(
            ["wkhtmltopdf", "--enable-local-file-access", "--print-media-type",
             "--page-width", f"{width}px", "--page-height", "1800px",
             "--margin-top", "0", "--margin-bottom", "0",
             "--margin-left", "0", "--margin-right", "0",
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
    ap.add_argument("--width", type=int, default=1320, help="PDF render width in px (default 1320)")
    ap.add_argument("--scale", type=int, default=2, help="PDF device scale factor (default 2)")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
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

    # PDF: static (no animations so cards aren't captured mid-fade)
    html = render_html(data, body_class="pdf")
    if html_to_pdf_playwright(html, out, args.width, args.scale):
        print(f"[ok] PDF (Chromium): {out}")
        return 0
    print("[warn] Playwright/Chromium unavailable — trying wkhtmltopdf "
          "(grain/gradient atmosphere will be approximated).", file=sys.stderr)
    if html_to_pdf_wkhtmltopdf(html, out, args.width):
        print(f"[ok] PDF (wkhtmltopdf): {out}")
        return 0
    fallback = out.with_suffix(".html")
    fallback.write_text(render_html(data, body_class=""), encoding="utf-8")
    print(f"[warn] No PDF engine available. HTML written instead: {fallback}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
