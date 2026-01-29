"""
ChatGPT Handler - ФИНАЛЬНАЯ ВЕРСИЯ
С полной интеграцией humanization для защиты от детекции
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import re
from config import *
from error_handler import ChatGPTErrorHandler
from project_manager import ProjectManager
from humanization import HumanBehavior, HumanSchedule

class ChatGPTHandler:
    """
    Класс для работы с ChatGPT
    
    КЛЮЧЕВЫЕ УЛУЧШЕНИЯ:
    1. Проверка состояния поля ввода вместо фиксированных таймеров
    2. Полная интеграция humanization для защиты от детекции
    3. Имитация реального поведения пользователя
    """
    
    def __init__(self, driver, humanization_config=None):
        self.driver = driver
        self.error_handler = ChatGPTErrorHandler(driver)
        self.project_manager = ProjectManager(driver)
        self.in_project = False
        
        # ✨ Инициализируем humanization
        self.human = HumanBehavior(humanization_config)
        self.schedule = HumanSchedule(humanization_config)
        
        print("🎭 Humanization включен")
        if self.schedule.enabled:
            print("📅 Расписание работы активно")
    
    # ============================================================
    # ПРОВЕРКА ГОТОВНОСТИ (из улучшенной версии)
    # ============================================================
    
    def is_input_field_enabled(self, input_field=None):
        """Проверяет доступно ли поле ввода"""
        try:
            if input_field is None:
                input_field = self.find_input_field()
            
            if not input_field:
                return False, "Поле ввода не найдено"
            
            if not input_field.is_displayed():
                return False, "Поле не отображается"
            
            if input_field.get_attribute("disabled"):
                return False, "Поле заблокировано"
            
            if input_field.get_attribute("readonly"):
                return False, "Поле readonly"
            
            placeholder = input_field.get_attribute("placeholder")
            if placeholder and ("typing" in placeholder.lower() or "печатает" in placeholder.lower()):
                return False, "ChatGPT печатает"
            
            stop_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Stop')] | //button[contains(text(), 'Остановить')]")
            if stop_buttons and any(btn.is_displayed() for btn in stop_buttons):
                return False, "Кнопка Stop активна"
            
            return True, "Поле готово"
            
        except StaleElementReferenceException:
            return False, "Элемент устарел"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
    
    def wait_for_input_field_ready(self, max_wait=GENERATION_MAX_WAIT):
        """
        Ждет готовности поля ввода
        
        ✨ С ИМИТАЦИЕЙ АКТИВНОСТИ чтения!
        """
        print(f"  ⏳ Жду готовности поля (макс {max_wait}с)...")
        
        start_time = time.time()
        last_reason = ""
        last_activity = time.time()
        checks_count = 0
        
        while time.time() - start_time < max_wait:
            checks_count += 1
            
            # Проверяем готовность
            is_ready, reason = self.is_input_field_enabled()
            
            if is_ready:
                elapsed = time.time() - start_time
                print(f"  ✅ Поле готово за {elapsed:.1f}с (проверок: {checks_count})")
                return True, "Готово"
            
            # Логируем изменения
            if reason != last_reason:
                print(f"  ⏳ {reason}...")
                last_reason = reason
            
            # ✨ HUMANIZATION: Имитируем чтение каждые 10-20 секунд
            if self.human.config['simulate_reading']:
                interval_range = self.human.config['reading_activity_interval']
                interval = time.time() - last_activity
                
                if interval > interval_range[0]:
                    activity_duration = min(
                        random.uniform(2, 5),
                        max_wait - (time.time() - start_time)
                    )
                    if activity_duration > 0:
                        self.human.simulate_reading(self.driver, duration=activity_duration)
                        last_activity = time.time()
            
            # Проверяем ошибки
            error_type, error_msg = self.error_handler.check_for_errors()
            if error_type:
                return False, f"Ошибка: {error_msg}"
            
            time.sleep(2)
        
        elapsed = time.time() - start_time
        return False, f"Таймаут за {elapsed:.1f}с"
    
    # ============================================================
    # БАЗОВЫЕ ФУНКЦИИ
    # ============================================================
    
    def verify_in_project(self, project_name):
        """Проверяет что мы в проекте"""
        try:
            current_url = self.driver.current_url
            
            if '/project' in current_url:
                print(f"  ✅ В проекте (URL: /project)")
                self.in_project = True
                return True
            
            try:
                header = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{project_name}')]")
                if header and header.is_displayed():
                    print(f"  ✅ В проекте (заголовок)")
                    self.in_project = True
                    return True
            except:
                pass
            
            print(f"  ⚠️ НЕ в проекте")
            self.in_project = False
            return False
            
        except Exception as e:
            print(f"  ⚠️ Ошибка проверки: {e}")
            self.in_project = False
            return False
    
    def create_new_chat(self):
        """Создает новый чат"""
        try:
            if self.in_project:
                print(f"  ℹ️  В проекте уже новый чат")
                return True
            
            print(f"  🆕 Создаю новый чат...")
            
            # ✨ HUMANIZATION: Пауза перед действием
            self.human.pause('navigating')
            
            selectors = [
                (By.XPATH, "//button[contains(., 'Новый чат')]"),
                (By.XPATH, "//a[contains(., 'Новый чат')]"),
                (By.XPATH, "//button[contains(., 'New chat')]"),
                (By.XPATH, "//a[contains(., 'New chat')]"),
            ]
            
            for by, selector in selectors:
                try:
                    button = self.driver.find_element(by, selector)
                    if button and button.is_displayed():
                        # ✨ HUMANIZATION: Human click
                        self.human.click(self.driver, button)
                        time.sleep(2)
                        print(f"  ✅ Новый чат создан")
                        return True
                except:
                    continue
            
            print(f"  ⚠️ Кнопка не найдена, продолжаю")
            return True
            
        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
            return True
    
    def find_input_field(self):
        """Находит поле ввода"""
        selectors = [
            (By.ID, "prompt-textarea"),
            (By.CSS_SELECTOR, "textarea[placeholder*='Message']"),
            (By.CSS_SELECTOR, "textarea[placeholder*='Новый чат']"),
            (By.XPATH, "//textarea"),
        ]
        
        for by, selector in selectors:
            try:
                element = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((by, selector))
                )
                if element:
                    return element
            except:
                continue
        
        return None
    
    # ============================================================
    # ОТПРАВКА ЗАПРОСА (С HUMANIZATION)
    # ============================================================
    
    def send_request(self, prompt, project=None, model=None, use_new_chat=True):
        """
        Отправляет запрос в ChatGPT
        
        ✨ С ПОЛНОЙ HUMANIZATION!
        """
        try:
            # ✨ HUMANIZATION: Проверяем расписание
            self.schedule.wait_until_work_hours()
            
            # ✨ HUMANIZATION: Случайное действие перед запросом
            self.human.random_action(self.driver)
            
            # Настройка контекста
            if project:
                print(f"  📁 Перехожу в проект '{project}'...")
                
                if not self.project_manager.switch_to_project(project):
                    print(f"  ⚠️ Не удалось перейти в проект")
                    self.in_project = False
                else:
                    time.sleep(3)
                    
                    if self.verify_in_project(project):
                        print(f"  ✅ В проекте '{project}'")
                    else:
                        print(f"  ⚠️ Проверка не прошла")
                        self.in_project = False
            else:
                self.in_project = False
            
            if use_new_chat:
                self.create_new_chat()
            
            if model:
                print(f"  🤖 Выбираю модель '{model}'...")
                if not self.project_manager.switch_model(model):
                    print(f"  ⚠️ Не удалось выбрать модель")
            
            # Проверка ошибок
            error_type, error_msg = self.error_handler.check_for_errors()
            if error_type:
                print(f"    ⚠️ Ошибка: {error_msg}")
                if self.error_handler.handle_error(error_type):
                    print("    ✅ Обработана")
                else:
                    return False, None, error_type, error_msg
            
            # Находим поле ввода
            print(f"  ✏️ Ищу поле ввода...")
            input_box = self.find_input_field()
            
            if not input_box:
                return False, None, 'not_found', "Поле ввода не найдено"
            
            print(f"  ✅ Поле найдено")
            
            # Проверяем готовность
            is_ready, reason = self.is_input_field_enabled(input_box)
            if not is_ready:
                print(f"  ⚠️ Поле не готово: {reason}")
                print(f"  ⏳ Жду готовности...")
                success, msg = self.wait_for_input_field_ready(max_wait=30)
                if not success:
                    return False, None, 'timeout', msg
            
            # ✨ HUMANIZATION: Клик в поле (со смещением)
            print(f"  🖱️  Кликаю в поле...")
            self.human.click(self.driver, input_box)
            
            # ✨ HUMANIZATION: Пауза после клика (фокус)
            time.sleep(random.uniform(0.3, 0.8))
            
            # Очищаем поле
            self.driver.execute_script("arguments[0].value = '';", input_box)
            time.sleep(0.3)
            
            # ✨ HUMANIZATION: Набираем текст как человек!
            print(f"  ⌨️  Набираю текст как человек...")
            self.human.type_text(input_box, prompt)
            
            # ✨ HUMANIZATION: Пауза перед отправкой (перечитывание)
            self.human.pause('verifying')
            
            # Отправляем
            print(f"  📤 Отправляю запрос...")
            input_box.send_keys(Keys.RETURN)
            
            # Ждем ответа
            return self.wait_for_response_smart()
            
        except Exception as e:
            return False, None, 'exception', str(e)
    
    # ============================================================
    # ОЖИДАНИЕ ОТВЕТА (УМНОЕ)
    # ============================================================
    
    def wait_for_response_smart(self):
        """
        Умное ожидание ответа с humanization
        """
        try:
            # ШАГ 1: Ждем появления ответа
            print(f"  ⏳ Жду появления ответа...")
            try:
                WebDriverWait(self.driver, RESPONSE_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-message-author-role='assistant']"))
                )
                print(f"  ✅ Ответ начал появляться")
            except TimeoutException:
                error_type, error_msg = self.error_handler.check_for_errors()
                if error_type:
                    return False, None, error_type, error_msg
                return False, None, 'timeout', "Ответ не появился"
            
            # ШАГ 2: Ждем завершения генерации
            print(f"  ⏳ Жду завершения генерации...")
            success, msg = self.wait_for_input_field_ready(max_wait=GENERATION_MAX_WAIT)
            
            if not success:
                print(f"  ⚠️ {msg}")
                print(f"  💡 Пробую прочитать частичный ответ...")
            else:
                print(f"  ✅ Генерация завершена")
            
            # Небольшая пауза
            time.sleep(2)
            
            # ШАГ 3: Читаем ответ
            return self.read_final_response()
                
        except Exception as e:
            return False, None, 'exception', str(e)
    
    def read_final_response(self, max_attempts=3):
        """Читает финальный ответ"""
        print(f"  📖 Читаю ответ...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                messages = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[data-message-author-role='assistant']")
                
                if not messages:
                    if attempt < max_attempts:
                        print(f"  ⚠️ Сообщения не найдены, попытка {attempt}/{max_attempts}")
                        time.sleep(2)
                        continue
                    else:
                        return False, None, 'empty', "Сообщения не найдены"
                
                last_message = messages[-1]
                
                # Читаем через JavaScript
                response_text = self.driver.execute_script(
                    "return arguments[0].textContent;", 
                    last_message
                )
                
                if response_text and len(response_text.strip()) > 0:
                    print(f"  ✅ Ответ получен ({len(response_text)} символов)")
                    return True, response_text, None, None
                else:
                    if attempt < max_attempts:
                        print(f"  ⚠️ Ответ пустой, попытка {attempt}/{max_attempts}")
                        time.sleep(2)
                        continue
                    else:
                        return False, None, 'empty', "Ответ пустой"
                    
            except StaleElementReferenceException:
                if attempt < max_attempts:
                    print(f"  ⚠️ Элемент устарел, попытка {attempt}/{max_attempts}")
                    time.sleep(2)
                    continue
                else:
                    return False, None, 'exception', "Элемент устарел"
                    
            except Exception as e:
                if attempt < max_attempts:
                    print(f"  ⚠️ Ошибка (попытка {attempt}/{max_attempts}): {e}")
                    time.sleep(2)
                else:
                    return False, None, 'exception', str(e)
        
        return False, None, 'empty', "Не удалось прочитать"


# ============================================================
# ПРИМЕР КОНФИГУРАЦИИ HUMANIZATION
# ============================================================

# Добавить в config.py:
"""
# === HUMANIZATION SETTINGS ===

HUMANIZATION_CONFIG = {
    # Интервалы между запросами (секунды)
    'delay_min': 15,
    'delay_max': 45,
    'delay_micro_pauses': True,
    
    # Скорость набора (words per minute)
    'typing_wpm_min': 50,
    'typing_wpm_max': 90,
    
    # Опечатки
    'typo_enabled': True,
    'typo_probability': 0.03,  # 3%
    
    # Случайные действия
    'random_actions_enabled': True,
    'random_actions_probability': 0.25,  # 25%
    
    # Активность во время ожидания
    'simulate_reading': True,
    'reading_activity_interval': (10, 20),
    
    # Клики
    'human_click_enabled': True,
    'click_offset_range': 0.3,
    
    # Расписание (ОПЦИОНАЛЬНО)
    'human_schedule_enabled': False,  # Включить для имитации рабочих часов
    'work_hours': (9, 18),
    'lunch_break': (13, 14),
    'mini_break_probability': 0.15,
    'mini_break_duration': (300, 900),  # 5-15 минут
}
"""