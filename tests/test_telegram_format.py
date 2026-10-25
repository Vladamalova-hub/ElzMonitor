import asyncio

from app.parsers import parse_source
from app.sources import SourceConfig
from app.telegram_bot import format_news_message, send_news_to_chat


def test_parse_source_uses_specific_post_url(monkeypatch):
    source = SourceConfig(
        slug="example",
        name="Example source",
        source_type="website",
        url="https://example.com/news",
        description="Example",
    )

    async def fake_fetch_text(_url):
        return """
        <html>
            <body>
                <article>
                    <h2><a href="https://example.com/post/42">ЧП Камчатка: новости</a></h2>
                    <p>В Елизово закрыли школу после проверки.</p>
                </article>
            </body>
        </html>
        """

    monkeypatch.setattr("app.parsers.fetch_text", fake_fetch_text)

    result = asyncio.run(parse_source(source))

    assert result
    assert result[0].url == "https://example.com/post/42"
    assert result[0].source_url == "https://example.com/news"


def test_parse_source_excludes_site_navigation_noise(monkeypatch):
    source = SourceConfig(
        slug="example",
        name="Example source",
        source_type="website",
        url="https://example.com/news",
        description="Example",
    )

    async def fake_fetch_text(_url):
        return """
        <html>
            <body>
                <nav>
                    <a>Новости и репортажи</a>
                    <a>Контакты</a>
                </nav>
                <main>
                    <h1>В Елизово открыли новую библиотеку</h1>
                    <p>В Елизово прошёл праздник с участием жителей и школьников. Местные власти отметили открытие нового здания.</p>
                </main>
            </body>
        </html>
        """

    monkeypatch.setattr("app.parsers.fetch_text", fake_fetch_text)

    result = asyncio.run(parse_source(source))

    assert result
    assert "Новости и репортажи" not in result[0].text
    assert "В Елизово прошёл праздник" in result[0].text


def test_send_news_to_chat_sends_to_configured_chat():
    calls = []

    class DummyBot:
        async def send_message(self, chat_id, text, disable_web_page_preview=False):
            calls.append({"chat_id": chat_id, "text": text, "disable_web_page_preview": disable_web_page_preview})

    item = {
        "title": "Новая новость",
        "text": "Отправка в Telegram работает корректно.",
        "source": "ЧП Камчатка",
        "url": "https://example.com/post/2",
        "published_at": "2026-10-23T05:55:00+00:00",
        "keywords": ["елизово"],
    }

    asyncio.run(send_news_to_chat(DummyBot(), [item], chat_id=-1001234567890))

    assert len(calls) == 1
    assert calls[0]["chat_id"] == -1001234567890
    assert "Новая новость" in calls[0]["text"]


def test_format_news_message_contains_expected_sections():
    item = {
        "title": "Бастрыкин взял на контроль дело о гибели сбитой женщины в Елизовском районе",
        "text": "Сын погибшей обратился в СК и сообщил, что водитель, сбивший его мать, теперь оказывает на него давление. Бастрыкин поручил проверить обстоятельства и доклад по делу.",
        "source": "ЧП Камчатка",
        "url": "https://example.com/post/1",
        "published_at": "2026-10-23T05:55:00+00:00",
        "keywords": ["елизовском"],
    }

    text = format_news_message(item, delivery_seconds=139)

    assert "🔔 Новый пост в ЧП Камчатка" in text
    assert "Бастрыкин взял на контроль" in text
    assert "🔑 Найдено: елизовском" in text
    assert "🕐 23.10.2026 05:55 UTC" in text
    assert "⏱ Доставлено за ~2мин 19с" in text
    assert "Читать полностью" in text
