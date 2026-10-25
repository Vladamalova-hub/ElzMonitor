from app.db import latest_news


def test_latest_news_filters_by_source_and_keyword(tmp_path, monkeypatch):
    from app import db

    monkeypatch.setattr(db, 'DATA_PATH', tmp_path / 'news.json')

    first = {
        'title': 'Елизово: стройка',
        'text': 'В Елизово стартовал новый проект',
        'source': 'ЧП Камчатка',
        'source_url': 'https://example.com/a',
        'url': 'https://example.com/a/1',
        'published_at': '2026-10-24T10:00:00+00:00',
        'keywords': ['елизово'],
    }
    second = {
        'title': 'Новый отчет',
        'text': 'Проект в Нагорном районе',
        'source': 'Кам24',
        'source_url': 'https://example.com/b',
        'url': 'https://example.com/b/2',
        'published_at': '2026-10-24T12:00:00+00:00',
        'keywords': ['нагорный'],
    }

    db.save_news([first, second])

    filtered = latest_news(10, source='ЧП Камчатка', keyword='елизово')
    assert len(filtered) == 1
    assert filtered[0]['source'] == 'ЧП Камчатка'
    assert 'елизово' in filtered[0]['keywords']

    filtered2 = latest_news(10, source='Кам24')
    assert len(filtered2) == 1
    assert filtered2[0]['source'] == 'Кам24'
