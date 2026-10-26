import logging
from datetime import datetime, timezone, timedelta

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
)

from config import (
    BOT_TOKEN, ADMIN_CHAT_ID, CHECK_INTERVAL,
    WEBSITES, TELEGRAM_CHANNELS, VK_GROUPS, MAX_CHANNELS,
)
from database import Database
from parsers.websites import parse_all_websites
from parsers.telegram_parser import parse_telegram_channels, disconnect_client
from parsers.vk_parser import parse_vk_groups
from parsers.max_parser import parse_max_channels

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

db = Database()
KAMCHATKA_TZ = timezone(timedelta(hours=12))


# ---------- Утилиты ----------

def format_news_message(news: dict) -> str:
    kw = news.get('keywords', [])
    if isinstance(kw, str):
        kw = [k for k in kw.split(',') if k]
    keywords_str = ', '.join(kw[:5])

    title = news['title']
    if len(title) > 300:
        title = title[:300] + '…'

    return (
        f"📰 <b>{title}</b>\n\n"
        f"📍 Источник: {news['source']}\n"
        f"🔑 {keywords_str}\n"
        f'🔗 <a href="{news["url"]}">Читать полностью</a>'
    )


def format_dt(dt_str: str) -> str:
    """SQLite CURRENT_TIMESTAMP — UTC. Переводим в Камчатку."""
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        return dt.astimezone(KAMCHATKA_TZ).strftime('%d.%m.%Y %H:%M (Камч.)')
    except Exception:
        return dt_str


# ---------- Команды ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для мониторинга новостей Елизовского округа.\n\n"
        "Команды:\n"
        "/news — Последние новости\n"
        "/search &lt;запрос&gt; — Поиск\n"
        "/sources — Источники\n"
        "/stats — Статистика\n"
        "/help — Справка",
        parse_mode='HTML',
    )


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Загружаю последние новости…")
    news_list = await db.get_recent_news(limit=10)
    if not news_list:
        await update.message.reply_text("📭 Новостей пока нет.")
        return
    for news in news_list:
        await update.message.reply_text(
            format_news_message(news),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /search &lt;запрос&gt;", parse_mode='HTML')
        return
    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Ищу: {query}")
    results = await db.search_news(query)
    if not results:
        await update.message.reply_text("📭 Ничего не найдено.")
        return
    await update.message.reply_text(f"Найдено: {len(results)}")
    for news in results[:10]:
        await update.message.reply_text(
            format_news_message(news),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )


async def sources_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["📰 <b>Источники мониторинга</b>\n", "🌐 <b>Сайты:</b>"]
    lines += [f"• {s['name']}" for s in WEBSITES]
    lines += ["\n📱 <b>Telegram:</b>"]
    lines += [f"• @{c}" for c in TELEGRAM_CHANNELS]
    lines += ["\n💬 <b>ВКонтакте:</b>"]
    lines += [f"• {g}" for g in VK_GROUPS]
    lines += ["\n📺 <b>MAX:</b>"]
    lines += [f"• {m['name']}" for m in MAX_CHANNELS]
    await update.message.reply_text('\n'.join(lines), parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = await db.get_stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"Всего новостей: {s['total']}\n"
        f"Сайты: {s['websites']}\n"
        f"Telegram: {s['telegram']}\n"
        f"ВКонтакте: {s['vk']}\n"
        f"MAX: {s['max']}\n\n"
        f"Последнее обновление: {format_dt(s['last_update']) if s['last_update'] != 'Нет данных' else 'Нет данных'}"
    )
    await update.message.reply_text(text, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Помощь</b>\n\n"
        "Бот мониторит новости Елизовского округа и присылает уведомления.\n\n"
        "<b>Команды:</b>\n"
        "/start — Начать\n"
        "/news — Последние новости\n"
        "/search &lt;запрос&gt; — Поиск\n"
        "/sources — Список источников\n"
        "/stats — Статистика\n"
        "/help — Справка",
        parse_mode='HTML',
    )


# ---------- Периодическая задача ----------

async def check_news_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("⏱ Старт проверки источников…")
    all_news: list[dict] = []

    try:
        website_news = parse_all_websites(WEBSITES)
        all_news.extend(website_news)
        logger.info(f"Сайты: {len(website_news)}")
    except Exception as e:
        logger.exception(f"Ошибка парсинга сайтов: {e}")

    try:
        tg_news = await parse_telegram_channels(TELEGRAM_CHANNELS)
        all_news.extend(tg_news)
        logger.info(f"Telegram: {len(tg_news)}")
    except Exception as e:
        logger.exception(f"Ошибка парсинга Telegram: {e}")

    try:
        vk_news = parse_vk_groups(VK_GROUPS)
        all_news.extend(vk_news)
        logger.info(f"VK: {len(vk_news)}")
    except Exception as e:
        logger.exception(f"Ошибка парсинга VK: {e}")

    try:
        max_news = parse_max_channels(MAX_CHANNELS)
        all_news.extend(max_news)
        logger.info(f"MAX: {len(max_news)}")
    except Exception as e:
        logger.exception(f"Ошибка парсинга MAX: {e}")

    new_count = 0
    for news in all_news:
        if await db.news_exists(news['url']):
            continue
        added = await db.save_news(news)
        if not added:
            continue
        new_count += 1
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=format_news_message(news),
                parse_mode='HTML',
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление: {e}")

    logger.info(f"✅ Проверка завершена. Новых: {new_count}")


# ---------- Lifecycle ----------

async def post_init(application: Application):
    await db.init_db()
    logger.info("База данных инициализирована")


async def post_shutdown(application: Application):
    await disconnect_client()
    logger.info("Telethon-клиент отключён")


def main():
    logger.info("🚀 Запуск бота…")
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("sources", sources_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))

    application.job_queue.run_repeating(
        check_news_job,
        interval=CHECK_INTERVAL,
        first=15,
        name="news_checker",
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()