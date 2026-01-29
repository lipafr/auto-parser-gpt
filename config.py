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

# ============================================================
# HUMANIZATION SETTINGS
# ============================================================

HUMANIZATION_CONFIG = {
    # === ЗАДЕРЖКИ МЕЖДУ ЗАПРОСАМИ ===
    'delay_min': 20,          # Минимум 20 секунд между запросами
    'delay_max': 45,          # Максимум 45 секунд
    'delay_micro_pauses': True,  # Добавлять случайные микропаузы
    
    # === СКОРОСТЬ НАБОРА ===
    'typing_wpm_min': 55,     # Минимум 55 слов/минуту
    'typing_wpm_max': 85,     # Максимум 85 слов/минуту
    
    # === ОПЕЧАТКИ ===
    'typo_enabled': True,     # Включить имитацию опечаток
    'typo_probability': 0.03, # 3% символов с опечатками
    
    # === СЛУЧАЙНЫЕ ДЕЙСТВИЯ ===
    'random_actions_enabled': True,  # Случайные действия перед запросом
    'random_actions_probability': 0.25,  # 25% вероятность
    
    # === АКТИВНОСТЬ ВО ВРЕМЯ ОЖИДАНИЯ ===
    'simulate_reading': True,  # Имитировать чтение ответа
    'reading_activity_interval': (10, 20),  # Активность каждые 10-20с
    
    # === КЛИКИ МЫШИ ===
    'human_click_enabled': True,  # Клики со смещением
    'click_offset_range': 0.3,    # ±30% от центра элемента
    
    # === РАСПИСАНИЕ РАБОТЫ (ОПЦИОНАЛЬНО) ===
    # ⚠️ Включайте только если хотите работать по расписанию!
    'human_schedule_enabled': False,  # False = работает всегда
    'work_hours': (9, 18),            # Рабочие часы 9:00-18:00
    'lunch_break': (13, 14),          # Обед 13:00-14:00
    'mini_break_probability': 0.15,   # 15% шанс перерыва
    'mini_break_duration': (300, 900),  # Перерыв 5-15 минут
}

# Уровни защиты (выберите один):
# 🟢 МИНИМАЛЬНЫЙ: delay_min=15, typo_enabled=False, random_actions=False
# 🟡 СРЕДНИЙ (рекомендуется): текущие настройки
# 🔴 МАКСИМАЛЬНЫЙ: delay_min=30, delay_max=60, human_schedule_enabled=True