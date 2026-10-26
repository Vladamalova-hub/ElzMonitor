import logging

from telethon import TelegramClient

from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_PATH, KEYWORDS

logger = logging.getLogger(__name__)

_client: TelegramClient | None = None


async def get_client() -> TelegramClient:
    """Singleton Telethon-клиент. Первый запуск требует ручной авторизации."""
    global _client
    if _client is None:
        _client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
        await _client.start(phone=PHONE_NUMBER)
        logger.info("Telethon-клиент подключён")
    elif not _client.is_connected():
        await _client.connect()
    return _client


async def disconnect_client():
    global _client
    if _client is not None:
        await _client.disconnect()
        _client = None


def _match_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw in text_lower]


async def parse_telegram_channels(channels: list[str]) -> list[dict]:
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        logger.warning("[telegram] Не заданы API_ID/API_HASH/PHONE_NUMBER — пропуск")
        return []

    try:
        client = await get_client()
    except Exception as e:
        logger.error(f"[telegram] Не удалось подключиться: {e}")
        return []

    all_news = []

    for channel_username in channels:
        try:
            channel = await client.get_entity(channel_username)
            async for message in client.iter_messages(channel, limit=20):
                if not message.text:
                    continue

                matched = _match_keywords(message.text)
                if not matched:
                    continue

                text = message.text
                title = text if len(text) <= 100 else text[:100] + '…'

                all_news.append({
                    'title': title,
                    'content': text,
                    'url': f"https://t.me/{channel_username}/{message.id}",
                    'source': getattr(channel, 'title', channel_username),
                    'source_url': f"https://t.me/{channel_username}",
                    'source_type': 'telegram',
                    'keywords': matched,
                })
        except Exception as e:
            logger.warning(f"[telegram] {channel_username}: {e}")
            continue

    return all_news