"""
Механизм повторных попыток
"""
import time
from config import *

class RetryHandler:
    """Класс для управления повторными попытками"""
    
    def __init__(self, max_attempts=3, base_delay=5, exponential_backoff=True):
        """
        max_attempts: максимальное количество попыток
        base_delay: базовая задержка между попытками (секунды)
        exponential_backoff: использовать ли экспоненциальную задержку
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.exponential_backoff = exponential_backoff
    
    def should_retry(self, error_type):
        """Определяет нужно ли повторять попытку для данного типа ошибки"""
        # Эти ошибки можно повторить
        retriable_errors = [
            'timeout',
            'network',
            'empty',
            'not_found',
            'exception',
            'capacity'
        ]
        
        # Эти ошибки повторять нельзя
        non_retriable_errors = [
            'rate_limit',  # Лимит - нужно ждать долго
            'auth'         # Авторизация - нужно вмешательство пользователя
        ]
        
        if error_type in non_retriable_errors:
            return False
        
        if error_type in retriable_errors:
            return True
        
        # Неизвестная ошибка - попробуем повторить
        return True
    
    def get_delay(self, attempt):
        """Вычисляет задержку перед следующей попыткой"""
        if self.exponential_backoff:
            # Экспоненциальная задержка: 5s, 10s, 20s, 40s...
            delay = self.base_delay * (2 ** (attempt - 1))
        else:
            # Фиксированная задержка
            delay = self.base_delay
        
        # Максимум 60 секунд
        return min(delay, 60)
    
    def execute_with_retry(self, func, *args, logger=None, row=None, **kwargs):
        """
        Выполняет функцию с повторными попытками
        
        func: функция для выполнения
        logger: объект логгера (опционально)
        row: номер строки Excel (для логирования)
        
        Возвращает: (success, result, error_type, error_message, attempts_used)
        """
        last_error_type = None
        last_error_message = None
        
        for attempt in range(1, self.max_attempts + 1):
            if logger and row:
                logger.retry_attempt(row, attempt, self.max_attempts)
            
            print(f"  🔄 Попытка {attempt}/{self.max_attempts}...")
            
            # Выполняем функцию
            success, result, error_type, error_message = func(*args, **kwargs)
            
            if success:
                if attempt > 1:
                    print(f"  ✅ Успешно со {attempt}-й попытки!")
                return True, result, None, None, attempt
            
            # Неудача
            last_error_type = error_type
            last_error_message = error_message
            
            # Проверяем можно ли повторить
            if not self.should_retry(error_type):
                print(f"  ⚠️ Ошибка {error_type} не подлежит повтору")
                return False, None, error_type, error_message, attempt
            
            # Если это не последняя попытка - делаем паузу
            if attempt < self.max_attempts:
                delay = self.get_delay(attempt)
                print(f"  ⏳ Пауза {delay} секунд перед следующей попыткой...")
                time.sleep(delay)
        
        # Все попытки исчерпаны
        print(f"  ❌ Все {self.max_attempts} попытки исчерпаны")
        return False, None, last_error_type, last_error_message, self.max_attempts