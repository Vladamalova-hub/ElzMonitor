from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import APP_LOGIN, APP_PASSWORD, APP_TITLE, SCRAPE_INTERVAL_MINUTES, TG_BOT_TOKEN, TG_CHAT_ID
from app.db import latest_news
from app.refresh import run_refresh


async def send_news_to_chat(bot: Any, items: list[dict], chat_id: str | int | None = None) -> int:
    target_chat_id = chat_id if chat_id is not None else TG_CHAT_ID
    if not target_chat_id or not items:
        return 0

    sent = 0
    for item in items[:5]:
        message = format_news_message(item, delivery_seconds=139)
        await bot.send_message(chat_id=target_chat_id, text=message, disable_web_page_preview=False)
        sent += 1
    return sent


def format_news_message(item: dict, delivery_seconds: int = 0) -> str:
    title = item.get("title") or "Без заголовка"
    text = item.get("text") or ""
    source = item.get("source") or "Источник"
    url = item.get("url") or item.get("source_url") or ""
    keywords = item.get("keywords") or []
    keyword_text = keywords[0] if keywords else "ключевое слово"

    published_at = item.get("published_at") or ""
    if published_at:
        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            utc_dt = dt.astimezone(timezone.utc)
            timestamp_text = utc_dt.strftime("%d.%m.%Y %H:%M UTC")
        except ValueError:
            timestamp_text = published_at
    else:
        timestamp_text = "Неизвестно"

    minutes, seconds = divmod(delivery_seconds, 60)
    formatted_elapsed = f"~{minutes}мин {seconds:02d}с" if minutes else f"~{seconds}с"

    preview = text.strip().replace("\n", " ")
    if len(preview) > 420:
        preview = preview[:420].rsplit(" ", 1)[0] + "..."

    message = (
        f"🔔 Новый пост в {source}\n\n"
        f"{title}\n\n"
        f"{preview}\n\n"
        f"🔑 Найдено: {keyword_text}\n"
        f"🕐 {timestamp_text}\n"
        f"⏱ Доставлено за {formatted_elapsed}\n\n"
        f"Читать полностью: {url}"
    )
    return message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"{APP_TITLE}\n\nВведите логин и пароль через /login <логин> <пароль>\n"
        "Пример: /login admin change-me"
    )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Использование: /login <логин> <пароль>")
        return
    username, password = args
    if username == APP_LOGIN and password == APP_PASSWORD:
        context.user_data["authorized"] = True
        await update.message.reply_text("Доступ открыт. Используйте /news для просмотра последних новостей.")
    else:
        await update.message.reply_text("Неверный логин или пароль.")


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("authorized"):
        await update.message.reply_text("Сначала выполните /login <логин> <пароль>.")
        return
    await update.message.reply_text("Обновляю ленту по доступным источникам...")
    count = await run_refresh()
    await send_news_to_chat(context.bot, latest_news(5))
    await update.message.reply_text(f"Готово. Добавлено новостей: {count}")


async def auto_refresh_news(context: ContextTypes.DEFAULT_TYPE) -> None:
    count = await run_refresh()
    if count <= 0:
        return
    await send_news_to_chat(context.bot, latest_news(5))


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("authorized"):
        await update.message.reply_text("Сначала выполните /login <логин> <пароль>.")
        return
    items = latest_news(10)
    if not items:
        await update.message.reply_text("Пока нет новостей по ключевым словам.")
        return
    for item in items[:5]:
        message = format_news_message(item, delivery_seconds=139)
        await update.message.reply_text(message, disable_web_page_preview=False)


def build_app() -> Application | None:
    if not TG_BOT_TOKEN:
        return None
    application = Application.builder().token(TG_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("refresh", refresh))
    application.add_handler(CommandHandler("news", news))

    if TG_CHAT_ID:
        application.job_queue.run_repeating(
            auto_refresh_news,
            interval=SCRAPE_INTERVAL_MINUTES * 60,
            first=60,
            name="news_refresh",
        )

    return application


if __name__ == "__main__":
    app = build_app()
    if app is None:
        raise RuntimeError("TG_BOT_TOKEN is not set")
    app.run_polling(drop_pending_updates=True)
