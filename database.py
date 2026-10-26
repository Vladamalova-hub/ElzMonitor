import aiosqlite
from config import DATABASE_URL


class Database:
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url

    async def init_db(self):
        async with aiosqlite.connect(self.db_url) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_news_created ON news(created_at DESC)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_news_type ON news(source_type)')
            await db.commit()

    async def save_news(self, news: dict) -> bool:
        """Возвращает True, если новость добавлена, False — если уже была."""
        async with aiosqlite.connect(self.db_url) as db:
            try:
                await db.execute('''
                    INSERT INTO news (title, content, url, source, source_url, source_type, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news['title'],
                    news.get('content', ''),
                    news['url'],
                    news['source'],
                    news['source_url'],
                    news['source_type'],
                    ','.join(news['keywords']),
                ))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def news_exists(self, url: str) -> bool:
        async with aiosqlite.connect(self.db_url) as db:
            async with db.execute('SELECT 1 FROM news WHERE url = ?', (url,)) as cur:
                return await cur.fetchone() is not None

    async def get_recent_news(self, limit: int = 10) -> list[dict]:
        async with aiosqlite.connect(self.db_url) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT title, content, url, source, source_url, source_type, keywords, created_at
                FROM news
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,)) as cur:
                rows = await cur.fetchall()
                return [self._row_to_dict(r) for r in rows]

    async def search_news(self, query: str) -> list[dict]:
        # Экранируем LIKE-спецсимволы
        safe = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        pattern = f'%{safe}%'
        async with aiosqlite.connect(self.db_url) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT title, content, url, source, source_url, source_type, keywords, created_at
                FROM news
                WHERE title LIKE ? ESCAPE '\\' OR content LIKE ? ESCAPE '\\' OR keywords LIKE ? ESCAPE '\\'
                ORDER BY id DESC
                LIMIT 20
            ''', (pattern, pattern, pattern)) as cur:
                rows = await cur.fetchall()
                return [self._row_to_dict(r) for r in rows]

    async def get_stats(self) -> dict:
        async with aiosqlite.connect(self.db_url) as db:
            async def count(where: str = '', params: tuple = ()) -> int:
                sql = 'SELECT COUNT(*) FROM news'
                if where:
                    sql += f' WHERE {where}'
                async with db.execute(sql, params) as cur:
                    return (await cur.fetchone())[0]

            total = await count()
            websites = await count('source_type = ?', ('website',))
            telegram = await count('source_type = ?', ('telegram',))
            vk = await count('source_type = ?', ('vk',))
            max_count = await count('source_type = ?', ('max',))

            async with db.execute('SELECT MAX(created_at) FROM news') as cur:
                row = await cur.fetchone()
                last_update = row[0] if row and row[0] else 'Нет данных'

        return {
            'total': total,
            'websites': websites,
            'telegram': telegram,
            'vk': vk,
            'max': max_count,
            'last_update': last_update,
        }

    @staticmethod
    def _row_to_dict(row: aiosqlite.Row) -> dict:
        d = dict(row)
        d['keywords'] = [k for k in d['keywords'].split(',') if k]
        return d
