"""
Обработчик ошибок и специальных ситуаций ChatGPT
"""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

class ChatGPTErrorHandler:
    """Класс для обнаружения и обработки ошибок ChatGPT"""
    
    # Известные сообщения об ошибках
    ERROR_PATTERNS = {
        'rate_limit': [
            "You've reached our limit",
            "Too many requests",
            "Rate limit",
            "превышен лимит",
            "слишком много запросов"
        ],
        'network': [
            "Network error",
            "Unable to load",
            "Connection failed",
            "ошибка сети",
            "не удалось загрузить"
        ],
        'capacity': [
            "at capacity",
            "high demand",
            "перегружен",
            "высокая нагрузка"
        ],
        'auth': [
            "Sign in",
            "Log in",
            "Authentication required",
            "войдите",
            "требуется авторизация"
        ]
    }
    
    def __init__(self, driver):
        self.driver = driver
    
    def check_for_errors(self):
        """
        Проверяет страницу на наличие ошибок
        Возвращает: (error_type, error_message) или (None, None)
        """
        try:
            # Проверяем весь текст страницы
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # Проверяем каждый тип ошибки
            for error_type, patterns in self.ERROR_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in page_text:
                        return error_type, f"Обнаружена ошибка: {pattern}"
            
            # Проверяем модальные окна с ошибками
            error_modals = self.driver.find_elements(By.CSS_SELECTOR, "[role='dialog'], .modal, .error-message")
            for modal in error_modals:
                if modal.is_displayed():
                    error_text = modal.text
                    if error_text:
                        return 'unknown', f"Модальное окно: {error_text[:200]}"
            
            return None, None
            
        except Exception as e:
            print(f"    ⚠️ Ошибка при проверке: {e}")
            return None, None
    
    def handle_rate_limit(self):
        """Обработка превышения лимита запросов"""
        print("    ⚠️ Обнаружено превышение лимита запросов!")
        print("    💡 Рекомендации:")
        print("       1. Подождите 1 час")
        print("       2. Используйте ChatGPT Plus для увеличения лимитов")
        print("       3. Или остановите скрипт и продолжите позже")
        
        choice = input("\n    Продолжить ожидание (y) или остановить (n)? >>> ").lower()
        if choice == 'y':
            print("    ⏳ Ожидание 1 час...")
            time.sleep(3600)  # 1 час
            return True
        return False
    
    def handle_capacity_error(self):
        """Обработка ошибки перегрузки"""
        print("    ⚠️ ChatGPT перегружен!")
        print("    💡 Пробую подождать 2 минуты и продолжить...")
        time.sleep(120)
        return True
    
    def handle_network_error(self):
        """Обработка сетевой ошибки"""
        print("    ⚠️ Ошибка сети!")
        print("    💡 Пробую перезагрузить страницу...")
        self.driver.refresh()
        time.sleep(10)
        return True
    
    def handle_auth_error(self):
        """Обработка ошибки авторизации"""
        print("    ⚠️ Требуется повторная авторизация!")
        print("    💡 Залогиньтесь заново в браузере")
        input("    Нажмите ENTER после авторизации >>> ")
        return True
    
    def handle_error(self, error_type):
        """
        Обрабатывает ошибку в зависимости от типа
        Возвращает True если можно продолжить, False если нужно остановить
        """
        handlers = {
            'rate_limit': self.handle_rate_limit,
            'capacity': self.handle_capacity_error,
            'network': self.handle_network_error,
            'auth': self.handle_auth_error
        }
        
        handler = handlers.get(error_type)
        if handler:
            return handler()
        
        # Неизвестная ошибка
        print(f"    ⚠️ Неизвестная ошибка: {error_type}")
        choice = input("    Продолжить (y) или остановить (n)? >>> ").lower()
        return choice == 'y'