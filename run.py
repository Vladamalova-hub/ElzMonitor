from app.parsers import scrape_all_sources
import asyncio


async def main():
    items = await scrape_all_sources()
    print(f"Fetched {len(items)} items")


if __name__ == "__main__":
    asyncio.run(main())
