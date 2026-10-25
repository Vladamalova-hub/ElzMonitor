from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "news.json"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class NewsItem:
    title: str
    text: str
    source: str
    source_url: str
    url: str
    published_at: str
    language: str = "ru"
    keywords: List[str] | None = None
    raw_json: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["keywords"] = payload.get("keywords") or []
        return payload


def load_news() -> list[dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_news(items: list[dict[str, Any]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def add_news_item(item: NewsItem) -> None:
    items = load_news()
    payload = item.to_dict()
    payload["saved_at"] = datetime.now(timezone.utc).isoformat()

    existing_by_url = {entry.get("url") for entry in items if entry.get("url")}
    if payload.get("url") and payload["url"] in existing_by_url:
        return

    items.insert(0, payload)
    save_news(items)


def latest_news(limit: int = 200, source: str | None = None, keyword: str | None = None) -> list[dict[str, Any]]:
    items = load_news()
    if source:
        items = [item for item in items if (item.get("source") or "").lower() == source.lower()]
    if keyword:
        items = [
            item for item in items
            if keyword.lower() in [str(k).lower() for k in (item.get("keywords") or [])]
        ]
    items = sorted(items, key=lambda x: x.get("published_at") or "", reverse=True)
    return items[:limit]
