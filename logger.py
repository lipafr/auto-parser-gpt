"""
Система логирования
"""
import logging
import os
from datetime import datetime
from config import *

class Logger:
    """Класс для логирования событий в файл и консоль"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Создаем имя файла с текущей датой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"parser_{timestamp}.log")
        
        # Настраиваем логгер
        self.logger = logging.getLogger("ChatGPTParser")
        self.logger.setLevel(logging.DEBUG)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Хендлер для файла
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Хендлер для консоли (только WARNING и выше)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file = log_file
        self.logger.info("=" * 70)
        self.logger.info("Логирование начато")
        self.logger.info(f"Файл лога: {log_file}")
        self.logger.info("=" * 70)
    
    def info(self, message):
        """Информационное сообщение"""
        self.logger.info(message)
    
    def warning(self, message):
        """Предупреждение"""
        self.logger.warning(message)
    
    def error(self, message):
        """Ошибка"""
        self.logger.error(message)
    
    def debug(self, message):
        """Отладочное сообщение"""
        self.logger.debug(message)
    
    def request_start(self, row, request_text):
        """Начало обработки запроса"""
        self.logger.info(f"[ROW {row}] Начало обработки: {request_text[:100]}")
    
    def request_success(self, row, response_length):
        """Успешная обработка"""
        self.logger.info(f"[ROW {row}] Успешно выполнено. Длина ответа: {response_length} символов")
    
    def request_error(self, row, error_type, error_message):
        """Ошибка при обработке"""
        self.logger.error(f"[ROW {row}] Ошибка ({error_type}): {error_message}")
    
    def retry_attempt(self, row, attempt, max_attempts):
        """Попытка повтора"""
        self.logger.warning(f"[ROW {row}] Попытка {attempt}/{max_attempts}")
    
    def get_log_file(self):
        """Возвращает путь к файлу лога"""
        return self.log_file
    
    def close(self):
        """Закрывает логгер"""
        self.logger.info("=" * 70)
        self.logger.info("Логирование завершено")
        self.logger.info("=" * 70)
        
        # Закрываем все хендлеры
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)