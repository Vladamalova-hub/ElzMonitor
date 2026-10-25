# ElzMonitor

ElzMonitor — это проект мониторинга новостей по ключевым словам. Он собирает публикации из разных источников, фильтрует их по словам и источникам, показывает их в одном интерфейсе и отправляет в Telegram.

## Что умеет проект

- сбор новостей с сайтов, Telegram-каналов, Max и VK
- фильтрация по ключевым словам
- фильтрация по источнику
- единая страница со всеми новостями
- авторизация через один логин и пароль
- Telegram-бот с уведомлениями
- автоматическое обновление каждые 10 минут

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

## Запуск на Render

Используйте команду:

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
APP_TITLE=ElzMonitor
BASE_URL=http://localhost:8000
TG_BOT_TOKEN=your_telegram_bot_token_here
SCRAPE_INTERVAL_MINUTES=10
```

## GitHub

```bash
git remote add origin https://github.com/ВАШ_ЛОГИН/ElzMonitor.git
git branch -M main
git push -u origin main
```

## Render

После загрузки проекта в GitHub:

1. Создать новый Web Service в Render
2. Подключить GitHub-репозиторий ElzMonitor
3. Выбрать Python
4. В Environment Variables добавить:
   - `APP_LOGIN`
   - `APP_PASSWORD`
   - `APP_TITLE`
   - `BASE_URL`
   - `TG_BOT_TOKEN`
   - `SCRAPE_INTERVAL_MINUTES`
5. Стартовая команда: `bash start.sh`

## Примечание

Локальный файл `.env` не должен попадать в GitHub. Используйте `.env.example` как шаблон, а секреты храните в Render или GitHub Secrets.

