# Камчатский медиамониторинг

Проект для сбора новостей по ключевым словам с сайтов, Telegram, Max и VK с единой авторизацией.

## Быстрый запуск локально

```bash
cd '/Users/a111/Downloads/Новая папка'
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Открыть страницу:

```text
http://127.0.0.1:8001/login
```

Логин/пароль по умолчанию:

```text
admin / change-me
```

## Запуск Telegram-бота

```bash
cd '/Users/a111/Downloads/Новая папка'
python3 bot_main.py
```

## Запуск 24/7 на сервере

Для Render/другого хостинга используйте команду:

```bash
bash start.sh
```

Или отдельно:

- запуск веб-приложения: `python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- запуск бота: `python3 bot_main.py`

## Переменные окружения

```env
APP_LOGIN=admin
APP_PASSWORD=change-me
APP_TITLE=Камчатский медиамониторинг
BASE_URL=http://localhost:8000
TG_BOT_TOKEN=...
SCRAPE_INTERVAL_MINUTES=15
```
