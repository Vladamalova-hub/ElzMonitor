from app.telegram_bot import format_news_message


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
