from app.db import NewsItem, add_news_item, latest_news


def test_add_news_item_deduplicates_same_url(tmp_path, monkeypatch):
    from app import db

    monkeypatch.setattr(db, "DATA_PATH", tmp_path / "news.json")

    item1 = NewsItem(
        title="Елизово",
        text="комплекс", 
        source="source1",
        source_url="https://example.com",
        url="https://example.com/post-1",
        published_at="2026-10-24T00:00:00+00:00",
        keywords=["елизово"],
    )
    item2 = NewsItem(
        title="Елизово 2",
        text="комплекс 2",
        source="source1",
        source_url="https://example.com",
        url="https://example.com/post-1",
        published_at="2026-10-24T01:00:00+00:00",
        keywords=["елизово"],
    )

    add_news_item(item1)
    add_news_item(item2)

    items = latest_news(10)
    assert len(items) == 1
    assert items[0]["title"] == "Елизово"


def test_latest_news_returns_most_recent_first(tmp_path, monkeypatch):
    from app import db

    monkeypatch.setattr(db, "DATA_PATH", tmp_path / "news.json")

    add_news_item(
        NewsItem(
            title="first",
            text="a",
            source="s",
            source_url="https://a",
            url="https://a/1",
            published_at="2026-10-24T00:00:00+00:00",
            keywords=["елизово"],
        )
    )
    add_news_item(
        NewsItem(
            title="second",
            text="b",
            source="s",
            source_url="https://b",
            url="https://b/2",
            published_at="2026-10-24T02:00:00+00:00",
            keywords=["елизово"],
        )
    )

    items = latest_news(10)
    assert items[0]["title"] == "second"
