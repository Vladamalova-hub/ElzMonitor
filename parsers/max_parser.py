import logging
from urllib.parse import urljoin

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


def parse_max_channels(channels: list[dict]) -> list[dict]:
    """
    Парсит MAX через веб-версию.
    ВНИМАНИЕ: MAX — SPA, статический HTML может не содержать постов.
    Здесь — универсальная заготовка; при необходимости переключитесь на их API.
    """
    all_news = []

    for channel in channels:
        try:
            response = requests.get(channel['url'], headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                if len(title) < 15:
                    continue
                matched = _match_keywords(title)
                if not matched:
                    continue

                href = urljoin(channel['url'], a['href'])
                all_news.append({
                    'title': title,
                    'url': href,
                    'source': channel['name'],
                    'source_url': channel['url'],
                    'source_type': 'max',
                    'keywords': matched,
                })
        except Exception as e:
            logger.warning(f"[max] {channel['name']}: {e}")

    return all_news