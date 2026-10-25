from __future__ import annotations

import asyncio
import html
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.db import NewsItem, add_news_item
from app.keywords import find_keyword_hits
from app.sources import SOURCE_LIST

REQUEST_TIMEOUT = 20.0


def resolve_article_url(soup: BeautifulSoup, source_url: str) -> str:
    candidates = []
    for link in soup.select("a[href]"):
        href = (link.get("href") or "").strip()
        if not href or href.startswith("javascript:"):
            continue
        absolute_url = urljoin(source_url, href)
        if absolute_url == source_url:
            continue
        if absolute_url.startswith("http"):
            candidates.append(absolute_url)

    for candidate in candidates:
        if "telegram.me" in candidate or "/post/" in candidate or "/news/" in candidate or "/article/" in candidate:
            return candidate
    return source_url


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prune_noise(soup: BeautifulSoup) -> BeautifulSoup:
    for selector in [
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "script",
        "style",
        ".menu",
        ".sidebar",
        ".breadcrumbs",
        ".social",
        ".related",
        ".widget",
    ]:
        for tag in soup.select(selector):
            tag.decompose()
    return soup


def extract_best_content_block(soup: BeautifulSoup) -> tuple[str, str]:
    candidates = []
    selectors = [
        "article",
        "main",
        ".post-content",
        ".entry-content",
        ".news-content",
        ".article-body",
        ".story-body",
        ".content",
        "#content",
        ".text",
    ]

    for selector in selectors:
        for tag in soup.select(selector):
            if tag.name in {"nav", "header", "footer", "aside"}:
                continue
            text = clean_html(tag.get_text(" ", strip=True))
            if len(text) > 150:
                candidates.append((tag, text))

    if not candidates:
        body = clean_html(soup.get_text(" ", strip=True))
        return "", body

    best_tag, best_text = max(candidates, key=lambda pair: len(pair[1]))
    title = ""
    title_tag = best_tag.select_one("h1, h2, h3")
    if title_tag:
        title = clean_html(title_tag.get_text(" ", strip=True))
    return title, best_text


async def fetch_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def parse_source(source: Any) -> list[NewsItem]:
    try:
        page = await fetch_text(source.url)
    except Exception:
        return []

    soup = BeautifulSoup(page, "html.parser")
    prune_noise(soup)

    title, text = extract_best_content_block(soup)
    texts = []
    if title or text:
        texts.append((title, text))

    if not texts:
        title = clean_html(soup.title.get_text(" ", strip=True)) if soup.title else ""
        body = clean_html(soup.get_text(" ", strip=True))
        if title or body:
            texts.append((title, body))

    article_url = resolve_article_url(soup, source.url)
    result: list[NewsItem] = []
    for title, text in texts:
        combined = f"{title} {text}".strip()
        hits = find_keyword_hits(combined)
        if not hits:
            continue
        result.append(
            NewsItem(
                title=title or source.name,
                text=combined[:2000],
                source=source.name,
                source_url=source.url,
                url=article_url,
                published_at=datetime.now(timezone.utc).isoformat(),
                keywords=hits,
                raw_json={"source_type": source.source_type},
            )
        )
    return result


async def scrape_all_sources() -> list[NewsItem]:
    tasks = [parse_source(source) for source in SOURCE_LIST]
    results = await asyncio.gather(*tasks)
    collected: list[NewsItem] = []
    for chunk in results:
        collected.extend(chunk)
    for item in collected:
        add_news_item(item)
    return collected
