#!/usr/bin/env python3
"""Regenerate sitemap.xml with Google image tags for city heroes and galleries."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://globetrotwithveda.com/"
NS_SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS_IMAGE = "http://www.google.com/schemas/sitemap-image/1.1"
PHOTO_EXT = {".jpg", ".jpeg", ".webp"}
SKIP_NAMES = {"logo.png", "favicon.png"}


class ImgCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "img":
            return
        ad = {k: v or "" for k, v in attrs}
        src = ad.get("src", "").strip()
        if not src:
            return
        name = Path(src.split("?")[0]).name.lower()
        if name in SKIP_NAMES:
            return
        if Path(src.split("?")[0]).suffix.lower() not in PHOTO_EXT:
            return
        self.images.append((src, ad.get("alt", "").strip()))


def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def page_path_for_loc(loc: str) -> Path | None:
    path = loc.removeprefix(BASE.rstrip("/"))
    if not path or path == "/":
        return ROOT / "index.html"
    slug = path.strip("/")
    candidate = ROOT / slug / "index.html"
    return candidate if candidate.is_file() else None


def absolute_image_url(page_file: Path, src: str) -> str:
    page_url = BASE + str(page_file.relative_to(ROOT)).replace("index.html", "")
    return urljoin(page_url, src)


def disk_url(file_path: Path) -> str:
    return BASE + str(file_path.relative_to(ROOT)).replace("\\", "/")


def collect_titles(page_file: Path) -> dict[str, str]:
    parser = ImgCollector()
    parser.feed(page_file.read_text(encoding="utf-8"))
    titles: dict[str, str] = {}
    for src, alt in parser.images:
        titles[absolute_image_url(page_file, src)] = alt
    return titles


def city_images(loc: str, page_file: Path) -> list[tuple[str, str]]:
    slug = loc.removeprefix(BASE.rstrip("/")).strip("/")
    if not slug:
        return []

    titles = collect_titles(page_file)
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        if url in seen:
            return
        seen.add(url)
        ordered.append((url, titles.get(url, "")))

    hero = ROOT / f"{slug}-image.jpg"
    if hero.is_file():
        add(disk_url(hero))

    city_dir = ROOT / slug
    if city_dir.is_dir():
        for photo in sorted(city_dir.glob("*.jpg"), key=natural_key):
            add(disk_url(photo))
        for photo in sorted(city_dir.glob("*.jpeg"), key=natural_key):
            add(disk_url(photo))

    for url in titles:
        add(url)

    return ordered


def load_url_entries() -> list[dict[str, str]]:
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    tag = lambda local: f"{{{NS_SITEMAP}}}{local}"
    entries = []
    for url in root.findall(tag("url")):
        loc_el = url.find(tag("loc"))
        if loc_el is None or not loc_el.text:
            continue
        entry = {"loc": loc_el.text.strip()}
        for field in ("lastmod", "changefreq", "priority"):
            el = url.find(tag(field))
            if el is not None and el.text:
                entry[field] = el.text.strip()
        entries.append(entry)
    return entries


def render(entries: list[dict[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<urlset xmlns="{NS_SITEMAP}"',
        f'        xmlns:image="{NS_IMAGE}">',
    ]
    for entry in entries:
        loc = entry["loc"]
        page_file = page_path_for_loc(loc)
        images = city_images(loc, page_file) if page_file and page_file != ROOT / "index.html" else []
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        for field in ("lastmod", "changefreq", "priority"):
            if field in entry:
                lines.append(f"    <{field}>{escape(entry[field])}</{field}>")
        for image_url, title in images:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{escape(image_url)}</image:loc>")
            if title:
                lines.append(f"      <image:title>{escape(title)}</image:title>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    xml = render(load_url_entries())
    SITEMAP.write_text(xml, encoding="utf-8")
    image_count = xml.count("<image:loc>")
    url_count = xml.count("    <loc>")
    print(f"Wrote {SITEMAP.relative_to(ROOT)} ({url_count} pages, {image_count} images)")


if __name__ == "__main__":
    main()
