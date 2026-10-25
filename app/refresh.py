import asyncio
from datetime import datetime, timedelta

from app.parsers import scrape_all_sources


async def run_refresh() -> int:
    items = await scrape_all_sources()
    return len(items)


async def periodic_refresh(interval_minutes: int = 10):
    while True:
        await run_refresh()
        await asyncio.sleep(interval_minutes * 60)


if __name__ == "__main__":
    print(asyncio.run(run_refresh()))
