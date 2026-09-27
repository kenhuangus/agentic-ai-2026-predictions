#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "assets" / "csa-article-card.html"
OUT = ROOT / "assets" / "images" / "csa-top-10-predictions-2026.png"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    url = HTML.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(url, wait_until="networkidle")
        page.locator("body").screenshot(path=str(OUT))
        browser.close()
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
