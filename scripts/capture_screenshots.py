#!/usr/bin/env python3
"""Capture demo screenshots of the running local app into docs/."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
URL = "http://127.0.0.1:5000"
SIZE = {"viewport": {"width": 1440, "height": 900}}


def launch(p):
    last = None
    for kwargs in (
        dict(channel="chrome", headless=True, args=["--headless=new", "--disable-gpu"]),
        dict(executable_path="/usr/bin/google-chrome", headless=True, args=["--headless=new", "--disable-gpu"]),
        dict(headless=True, args=["--disable-gpu"]),
    ):
        try:
            return p.chromium.launch(**kwargs)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not launch a browser: {last}")


def ready(page):
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_selector(".puzzle-card")
    page.wait_for_selector("#examples .grid")
    page.wait_for_timeout(400)


def main():
    DOCS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(**SIZE)

        # 01: first lesson + two hints, clean canvas
        ready(page)
        page.click("#btn-hint")
        page.wait_for_timeout(250)
        page.click("#btn-hint")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DOCS / "01-lesson-and-hint.png"), full_page=True)

        # 02: check the unpainted canvas (copy of the test input) so the
        # focus lands on a real shape cell, not a random painted pixel.
        page.click("#btn-check")
        page.wait_for_selector("#check-result")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DOCS / "02-check-attempt.png"), full_page=True)

        # 03: fresh session, explain + walkthrough, no failed check banner
        ready(page)
        page.click("#btn-hint")
        page.wait_for_timeout(200)
        page.click("#btn-explain")
        page.wait_for_selector("#steps-panel:not(.hidden)")
        page.wait_for_timeout(400)
        # Scroll so the walkthrough is in the shot but keep the header
        page.wait_for_timeout(200)
        page.screenshot(path=str(DOCS / "03-rule-walkthrough.png"), full_page=True)

        # 04: two-step lesson
        page.locator(".puzzle-card", has_text="Fall of Towers").click()
        page.wait_for_timeout(400)
        page.click("#btn-hint")
        page.wait_for_timeout(250)
        page.click("#btn-explain")
        page.wait_for_selector("#steps-panel:not(.hidden)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DOCS / "04-two-step-lesson.png"), full_page=True)

        browser.close()
    for name in [
        "01-lesson-and-hint.png",
        "02-check-attempt.png",
        "03-rule-walkthrough.png",
        "04-two-step-lesson.png",
    ]:
        path = DOCS / name
        print(path, path.stat().st_size)


if __name__ == "__main__":
    main()
