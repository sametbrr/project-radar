# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-06-11

### Fixed
- `build_report.py` now reports a clear one-line error (exit code 1) when `report-data.json` is missing or contains invalid JSON, instead of a raw traceback.
- PDF rendering failure now prints an explicit warning to stderr before falling back to HTML output (previously the fallback was silent).
- Concurrent renders no longer clash: the intermediate render file is PID-suffixed instead of the fixed `._render.html` name.

### Added
- `version` field in SKILL.md frontmatter, `CHANGELOG.md`, auto-release workflow.

## [1.1.0] - 2026-06-08

### Added
- Expanded discovery sources; GitHub Trending scraper (`fetch_github_trending.py`).
- Persistent watchlist (`watchlist.py`): add repos, generate medium-depth detail reports (Markdown + HTML), list with file references.

### Changed
- Synced SKILL.md and `references/sources-and-scoring.md` with the latest workflow guidance.

## [1.0.0] - 2026-06-07

### Added
- Initial release: daily trend & community discovery radar — scans GitHub, Hacker News, Product Hunt, newsletters and social, scores usefulness 0–100, renders a Turkish HTML report from `assets/report-template.html`.
- Standardized README and Turkish README.
