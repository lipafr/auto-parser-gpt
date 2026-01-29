"""
Работа с ChatGPT - УЛУЧШЕННАЯ ВЕРСИЯ
Основное изменение: проверка готовности поля ввода вместо таймеров
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

class ChatGPTHandler:
    """Класс для работы с ChatGPT"""
    
    def __init__(self, driver):
        self.driver = driver
        self.error_handler = ChatGPTErrorHandler(driver)
        self.project_manager = ProjectManager(driver)
        self.in_project = False
    
    def verify_in_project(self, project_name):
        """Проверяет что мы находимся на странице проекта"""
        try:
            current_url = self.driver.current_url
            
            if '/project' in current_url:
                print(f"  ✅ В проекте (URL: /project)")
                self.in_project = True
                return True
            
            try:
                header = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{project_name}')]")
                if header and header.is_displayed():
                    print(f"  ✅ В проекте (заголовок найден)")
                    self.in_project = True
                    return True
            except:
                pass
            
            try:
                placeholder = self.driver.find_element(By.XPATH, f"//input[contains(@placeholder, '{project_name}')] | //textarea[contains(@placeholder, '{project_name}')]")
                if placeholder:
                    print(f"  ✅ В проекте (placeholder найден)")
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
                print(f"  ℹ️  В проекте уже открыт новый чат")
                return True
            
            print(f"  🆕 Создаю новый чат...")
            
            new_chat_selectors = [
                (By.XPATH, "//button[contains(., 'Новый чат')]"),
                (By.XPATH, "//a[contains(., 'Новый чат')]"),
                (By.XPATH, "//button[contains(., 'New chat')]"),
                (By.XPATH, "//a[contains(., 'New chat')]"),
            ]
            
            for by, selector in new_chat_selectors:
                try:
                    button = self.driver.find_element(by, selector)
                    if button and button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        print(f"  ✅ Новый чат создан")
                        return True
                except:
                    continue
            
            print(f"  ⚠️ Кнопка 'Новый чат' не найдена, продолжаю")
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
    
    def is_input_field_enabled(self, input_field=None):
        """
        ✨ НОВАЯ ФУНКЦИЯ: Проверяет доступно ли поле ввода
        
        Это КЛЮЧЕВАЯ функция для определения готовности ChatGPT.
        Поле ввода блокируется во время генерации и разблокируется после.
        
        Возвращает: (is_enabled, reason)
        """
        try:
            if input_field is None:
                input_field = self.find_input_field()
            
            if not input_field:
                return False, "Поле ввода не найдено"
            
            # Проверка 1: Элемент существует и видим
            if not input_field.is_displayed():
                return False, "Поле ввода не отображается"
            
            # Проверка 2: Поле не disabled
            is_disabled = input_field.get_attribute("disabled")
            if is_disabled:
                return False, "Поле ввода заблокировано (disabled)"
            
            # Проверка 3: Поле не readonly
            is_readonly = input_field.get_attribute("readonly")
            if is_readonly:
                return False, "Поле ввода только для чтения (readonly)"
            
            # Проверка 4: Проверяем placeholder (если там "ChatGPT is typing..." = генерация идет)
            placeholder = input_field.get_attribute("placeholder")
            if placeholder and ("typing" in placeholder.lower() or "печатает" in placeholder.lower()):
                return False, "ChatGPT печатает"
            
            # Проверка 5: Можно ли кликнуть на элемент
            try:
                # Пытаемся кликнуть (но не кликаем реально, просто проверяем)
                self.driver.execute_script("return arguments[0].offsetParent !== null", input_field)
            except:
                return False, "Поле ввода недоступно для взаимодействия"
            
            # Проверка 6: Нет ли кнопки "Stop generating"
            stop_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Stop')] | //button[contains(text(), 'Остановить')]")
            if stop_buttons and any(btn.is_displayed() for btn in stop_buttons):
                return False, "Кнопка Stop активна - генерация идет"
            
            # ✅ Все проверки пройдены - поле готово
            return True, "Поле ввода готово"
            
        except StaleElementReferenceException:
            return False, "Элемент устарел (страница обновилась)"
        except Exception as e:
            return False, f"Ошибка проверки: {str(e)}"
    
    def wait_for_input_field_ready(self, max_wait=GENERATION_MAX_WAIT, check_interval=2):
        """
        ✨ НОВАЯ ФУНКЦИЯ: Ждет пока поле ввода станет готовым
        
        Это ПРАВИЛЬНЫЙ способ ожидания завершения генерации.
        Вместо фиксированных таймеров мы проверяем реальное состояние интерфейса.
        
        Возвращает: (success, message)
        """
        print(f"  ⏳ Жду готовности поля ввода (макс {max_wait}с)...")
        
        start_time = time.time()
        last_reason = ""
        checks_count = 0
        
        while time.time() - start_time < max_wait:
            checks_count += 1
            
            # Проверяем состояние поля
            is_ready, reason = self.is_input_field_enabled()
            
            if is_ready:
                elapsed = time.time() - start_time
                print(f"  ✅ Поле ввода готово за {elapsed:.1f}с (проверок: {checks_count})")
                return True, "Поле ввода готово"
            
            # Логируем изменения статуса
            if reason != last_reason:
                print(f"  ⏳ {reason}...")
                last_reason = reason
            
            # Проверяем ошибки ChatGPT
            error_type, error_msg = self.error_handler.check_for_errors()
            if error_type:
                return False, f"Ошибка ChatGPT: {error_msg}"
            
            # Пауза перед следующей проверкой
            time.sleep(check_interval)
        
        # Таймаут
        elapsed = time.time() - start_time
        return False, f"Таймаут: поле не стало готовым за {elapsed:.1f}с"
    
    def wait_for_response_to_appear(self, timeout=30):
        """
        ✨ УЛУЧШЕННАЯ ФУНКЦИЯ: Ждет появления ответа (первых слов)
        
        Возвращает: (success, message)
        """
        print(f"  ⏳ Жду появления ответа (макс {timeout}с)...")
        
        try:
            # Ждем появления хотя бы одного сообщения ассистента
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-message-author-role='assistant']"))
            )
            print(f"  ✅ Ответ начал появляться")
            return True, "Ответ появился"
            
        except TimeoutException:
            # Проверяем ошибки
            error_type, error_msg = self.error_handler.check_for_errors()
            if error_type:
                return False, f"Ошибка: {error_msg}"
            return False, f"Ответ не появился за {timeout}с"
    
    def send_request(self, prompt, project=None, model=None, use_new_chat=True):
        """
        ✨ УЛУЧШЕННАЯ ФУНКЦИЯ: Отправляет запрос в ChatGPT
        
        КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Вместо фиксированных time.sleep() используем
        wait_for_input_field_ready() для определения завершения генерации.
        
        Возвращает: (success, response_text, error_type, error_message)
        """
        try:
            # Настройка контекста (проект/модель)
            if project:
                print(f"  📁 Перехожу в проект '{project}'...")
                
                if not self.project_manager.switch_to_project(project):
                    print(f"  ⚠️ Не удалось перейти в проект")
                    self.in_project = False
                else:
                    time.sleep(3)
                    
                    if self.verify_in_project(project):
                        print(f"  ✅ Успешно зашли в проект '{project}'")
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
            
            # Проверка ошибок перед отправкой
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
            
            # Проверяем что поле готово к вводу
            is_ready, reason = self.is_input_field_enabled(input_box)
            if not is_ready:
                print(f"  ⚠️ Поле не готово: {reason}")
                print(f"  ⏳ Жду готовности...")
                success, msg = self.wait_for_input_field_ready(max_wait=30)
                if not success:
                    return False, None, 'timeout', msg
            
            # Отправляем запрос
            print(f"  📝 Отправляю запрос...")
            input_box.click()
            time.sleep(1)
            
            # Очищаем поле
            self.driver.execute_script("arguments[0].value = '';", input_box)
            time.sleep(0.5)
            
            # Вводим текст
            input_box.send_keys(prompt)
            time.sleep(1)
            
            # Отправляем
            input_box.send_keys(Keys.RETURN)
            
            # ✨ НОВАЯ ЛОГИКА: Ждем ответа правильно
            return self.wait_for_response_smart()
            
        except Exception as e:
            return False, None, 'exception', str(e)
    
    def wait_for_response_smart(self):
        """
        ✨ НОВАЯ УМНАЯ ФУНКЦИЯ: Ожидание и получение ответа
        
        АЛГОРИТМ:
        1. Ждем появления первых слов ответа (макс 90с)
        2. Ждем когда поле ввода разблокируется (макс 120с)
        3. Читаем финальный ответ
        
        Это НАМНОГО надежнее чем фиксированные time.sleep()!
        """
        try:
            # ШАГ 1: Ждем появления ответа
            success, msg = self.wait_for_response_to_appear(timeout=RESPONSE_WAIT_TIMEOUT)
            if not success:
                error_type, error_msg = self.error_handler.check_for_errors()
                if error_type:
                    return False, None, error_type, error_msg
                return False, None, 'timeout', msg
            
            # ШАГ 2: Ждем завершения генерации (поле ввода разблокируется)
            print(f"  ⏳ Жду завершения генерации...")
            success, msg = self.wait_for_input_field_ready(
                max_wait=GENERATION_MAX_WAIT,
                check_interval=2
            )
            
            if not success:
                # Даже если таймаут - попробуем прочитать что есть
                print(f"  ⚠️ {msg}")
                print(f"  💡 Пробую прочитать частичный ответ...")
            else:
                print(f"  ✅ Генерация завершена")
            
            # Небольшая пауза для стабилизации DOM
            time.sleep(2)
            
            # ШАГ 3: Читаем ответ
            return self.read_final_response()
                
        except Exception as e:
            return False, None, 'exception', str(e)
    
    def read_final_response(self, max_attempts=3):
        """
        ✨ УЛУЧШЕННАЯ ФУНКЦИЯ: Читает финальный ответ с несколькими попытками
        
        Возвращает: (success, response_text, error_type, error_message)
        """
        print(f"  📖 Читаю ответ...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Находим все сообщения ассистента
                messages = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[data-message-author-role='assistant']")
                
                if not messages:
                    if attempt < max_attempts:
                        print(f"  ⚠️ Сообщения не найдены, попытка {attempt}/{max_attempts}")
                        time.sleep(2)
                        continue
                    else:
                        return False, None, 'empty', "Сообщения ассистента не найдены"
                
                # Берем последнее сообщение
                last_message = messages[-1]
                
                # Читаем текст через JavaScript (надежнее)
                response_text = self.driver.execute_script(
                    "return arguments[0].textContent;", 
                    last_message
                )
                
                if response_text and len(response_text.strip()) > 0:
                    print(f"  ✅ Ответ получен ({len(response_text)} символов)")
                    
                    # Дополнительная проверка: ответ не обрезан
                    if self.is_response_complete(last_message):
                        return True, response_text, None, None
                    else:
                        print(f"  ⚠️ Ответ может быть неполным, попытка {attempt}/{max_attempts}")
                        if attempt < max_attempts:
                            time.sleep(3)
                            continue
                        else:
                            # Возвращаем что есть
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
                    return False, None, 'exception', "Элемент устарел (StaleElementReference)"
                    
            except Exception as e:
                if attempt < max_attempts:
                    print(f"  ⚠️ Ошибка чтения (попытка {attempt}/{max_attempts}): {e}")
                    time.sleep(2)
                else:
                    return False, None, 'exception', str(e)
        
        return False, None, 'empty', "Не удалось прочитать ответ"
    
    def is_response_complete(self, message_element):
        """
        ✨ НОВАЯ ФУНКЦИЯ: Проверяет что ответ полностью сгенерирован
        
        Признаки неполного ответа:
        - Есть индикатор загрузки внутри сообщения
        - Есть "..." в конце
        - Сообщение слишком короткое (меньше 10 символов)
        """
        try:
            # Проверка 1: Индикатор загрузки
            loading_indicators = message_element.find_elements(By.CSS_SELECTOR, 
                ".animate-pulse, .loading, .spinner")
            if loading_indicators:
                return False
            
            # Проверка 2: Текст
            text = message_element.text.strip()
            
            # Слишком короткий
            if len(text) < 10:
                return False
            
            # Заканчивается на многоточие (может быть обрезан)
            if text.endswith("..."):
                return False
            
            return True
            
        except:
            return True  # В случае ошибки считаем что ответ полный