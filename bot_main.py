from app.telegram_bot import build_app


if __name__ == "__main__":
    app = build_app()
    if app is None:
        raise RuntimeError("TG_BOT_TOKEN is not set. Fill .env or Render env variable.")
    app.run_polling(drop_pending_updates=True)
