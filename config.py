"""
Конфигурация проекта
"""
import os

# Excel настройки
EXCEL_FILE = "requests.xlsx"
SHEET_NAME = "Sheet1"

# Колонки в Excel
COL_REQUEST = 1   # A - Запрос
COL_RESPONSE = 2  # B - Ответ
COL_STATUS = 3    # C - Статус
COL_DATE = 4      # D - Дата выполнения
COL_ERROR = 5     # E - Описание ошибки
COL_PROJECT = 6   # F - Проект ChatGPT (опционально)
COL_MODEL = 7     # G - Модель (GPT-4, GPT-4o, o1, etc.)
COL_CHAT_MODE = 8 # H - Режим чата (new/continue/series)

# Браузер настройки
BRAVE_PATH = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
PROFILE_DIR = os.path.abspath(os.path.join(os.getcwd(), "chatgpt_profile"))

# Таймауты (секунды)
DELAY_BETWEEN_REQUESTS = 5
PAGE_LOAD_TIMEOUT = 15
ELEMENT_WAIT_TIMEOUT = 20
RESPONSE_WAIT_TIMEOUT = 90
GENERATION_MAX_WAIT = 120

# Задержки для переключения проектов/моделей
PROJECT_SWITCH_DELAY = 3
MODEL_SWITCH_DELAY = 2

# Режимы работы с чатами
USE_NEW_CHAT_FOR_EACH_REQUEST = True  # По умолчанию (можно переопределить в Excel)

# Retry настройки
MAX_RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 5
RETRY_EXPONENTIAL_BACKOFF = True

# Backup настройки
BACKUP_ENABLED = True
KEEP_LAST_BACKUPS = 5

# Логирование
LOG_ENABLED = True
LOG_DIR = "logs"

# ChatGPT URL
CHATGPT_URL = "https://chat.openai.com/"

# Статусы
STATUS_PENDING = None
STATUS_IN_PROGRESS = "В процессе"
STATUS_SUCCESS = "Выполнен"
STATUS_ERROR = "Ошибка"
STATUS_RATE_LIMIT = "Превышен лимит"
STATUS_NETWORK_ERROR = "Ошибка сети"
STATUS_TIMEOUT = "Таймаут"

# Поддерживаемые модели (обновленный список для GPT-5)
SUPPORTED_MODELS = {
    'gpt-5.2': 'GPT-5.2',
    'gpt-5.1': 'GPT-5.1', 
    'gpt-5': 'GPT-5 (o3)',
    'gpt-4o': 'GPT-4o',
    'gpt-4': 'GPT-4',
    'o1': 'o1-preview',
    'o1-mini': 'o1-mini',
    'o3': 'o3',
}

# Режимы чата
CHAT_MODE_NEW = 'new'          # Новый чат
CHAT_MODE_CONTINUE = 'continue' # Продолжить текущий чат
CHAT_MODE_SERIES = 'series'     # Серия запросов в одном чате

# JSON настройки
JSON_ENABLED = True
JSON_OUTPUT_DIR = "json_results"
JSON_SAVE_INCREMENTAL = True  # Сохранять после каждого запроса