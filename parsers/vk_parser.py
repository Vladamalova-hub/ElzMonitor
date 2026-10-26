import logging

import vk_api

from config import VK_ACCESS_TOKEN, KEYWORDS

logger = logging.getLogger(__name__)


def _match_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw in text_lower]


def parse_vk_groups(groups: list[str]) -> list[dict]:
    if not VK_ACCESS_TOKEN:
        logger.warning("[vk] Не задан VK_ACCESS_TOKEN — пропуск")
        return []

    try:
        vk_session = vk_api.VkApi(token=VK_ACCESS_TOKEN)
        vk = vk_session.get_api()
    except Exception as e:
        logger.error(f"[vk] Ошибка инициализации: {e}")
        return []

    all_news = []

    for group in groups:
        try:
            response = vk.wall.get(domain=group, count=20)
        except Exception as e:
            logger.warning(f"[vk] {group}: {e}")
            continue

        for post in response.get('items', []):
            text = post.get('text', '')
            if not text:
                continue

            matched = _match_keywords(text)
            if not matched:
                continue

            title = text if len(text) <= 100 else text[:100] + '…'
            post_url = f"https://vk.com/wall{post['owner_id']}_{post['id']}"

            all_news.append({
                'title': title,
                'content': text,
                'url': post_url,
                'source': group,
                'source_url': f"https://vk.com/{group}",
                'source_type': 'vk',
                'keywords': matched,
            })

    return all_news