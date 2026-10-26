import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram Bot ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
_admin_id = os.getenv('ADMIN_CHAT_ID')
ADMIN_CHAT_ID = int(_admin_id) if _admin_id else None

# --- VK API ---
VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')

# --- Telegram API (Telethon) ---
_api_id = os.getenv('API_ID')
API_ID = int(_api_id) if _api_id else None
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
SESSION_PATH = os.getenv('SESSION_PATH', 'sessions/tg')

# --- База данных ---
DATABASE_URL = os.getenv('DATABASE_URL', 'news_database.db')

# --- Периодичность проверки (в секундах) ---
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '1800'))  # 30 минут

# --- Валидация при старте ---
_REQUIRED = ['BOT_TOKEN', 'ADMIN_CHAT_ID']
_missing = [name for name in _REQUIRED if not globals()[name]]
if _missing:
    raise RuntimeError(f"Не заданы переменные окружения: {', '.join(_missing)}")

# --- Ключевые слова ---
KEYWORDS = [
    'елизово', 'елизовский', 'емо', 'емр', 'елизове', 'елизова',
    'соснови', 'пионерск', 'светл', 'крутобереков', 'вулкан', 'ганал',
    'дальн', 'малк', 'начик', 'паратунк', 'термальн', 'коряк',
    'зелён', 'зелен', 'нагорн', 'раздольн', 'николаевк', 'сокочи',
    'двуречь', 'керкин', 'пиначев', 'лесн', 'березняк',
]

# --- Источники ---
WEBSITES = [
    {'name': 'КамчаткаИнфо', 'url': 'https://kamchatinfo.com'},
    {'name': 'KAM24', 'url': 'https://kam24.ru'},
    {'name': 'Камчатка Сегодня', 'url': 'https://kamtoday.ru'},
    {'name': 'Кам-Край', 'url': 'https://kam-kray.ru'},
    {'name': 'РИА Камчатка', 'url': 'https://ria.ru/location_Kamchatskijj_krajj/'},
    {'name': 'Полуостров Камчатка', 'url': 'https://www.poluostrov-kamchatka.ru'},
    {'name': 'Елизово БезФормата', 'url': 'https://elizovo.bezformata.com'},
    {'name': 'Lenta — Елизово', 'url': 'https://lenta.ru/tags/geo/elizovo/'},
    {'name': 'КамИнформ — Елизово', 'url': 'https://kaminform.online/news/segodnja-v-kamchatskom-krae/novosti-elizovo'},
    {'name': 'Госуслуги Елизово', 'url': 'https://elizovo.gosuslugi.ru/dlya-zhiteley/novosti-i-reportazhi/'},
]

TELEGRAM_CHANNELS = [
    'chpkamchatka',
    'bezfiltra_41',
    'massmediakam',
    'kamchatka_smi',
    'new_elizovo',
    'kamgov41',
    'kamchatskaya_zhizn',
    'kamreporter',
]

VK_GROUPS = [
    'overhear_elizovo',
    'elizovo_group_41',
    'razeb41',
    'infokamch',
    'kamgov41',
    'kamchatrip',
    'kamotzovik',
]

MAX_CHANNELS = [
    {'name': 'KAM24', 'url': 'https://max.ru/kam24ru'},
    {'name': 'Камчатка Now', 'url': 'https://max.ru/kamchatka_now'},
    {'name': 'КамРепортер', 'url': 'https://max.ru/kamreporter'},
]