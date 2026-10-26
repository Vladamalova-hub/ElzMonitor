import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import KEYWORDS

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0 Safari/537.36'
    )
}


def _match_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw in text_lower]


def parse_website(name: str, url: str) -> list[dict]:
    """Парсит один сайт, возвращает список новостей."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"[website] {name}: ошибка запроса {e}")
        return []

    try:
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        logger.warning(f"[website] {name}: ошибка парсинга HTML {e}")
        return []

    base_host = urlparse(url).netloc
    articles = []
    seen_urls = set()

    for link in soup.find_all('a', href=True):
        title = link.get_text(strip=True)
        if len(title) < 15:
            continue

        href = urljoin(url, link['href'])
        parsed = urlparse(href)

        # Только внутренние ссылки
        if parsed.netloc and parsed.netloc != base_host:
            continue
        # Пропускаем главную и якоря
        if parsed.path in ('', '/') and not parsed.query:
            continue
        if href in seen_urls:
            continue

        matched = _match_keywords(title)
        if not matched:
            continue

        seen_urls.add(href)
        articles.append({
            'title': title,
            'url': href,
            'source': name,
            'source_url': url,
            'source_type': 'website',
            'keywords': matched,
        })

    return articles[:10]


def parse_all_websites(websites: list[dict]) -> list[dict]:
    all_news = []
    for site in websites:
        try:
            all_news.extend(parse_website(site['name'], site['url']))
        except Exception as e:
            logger.exception(f"[website] {site['name']}: неожиданная ошибка {e}")
    return all_news