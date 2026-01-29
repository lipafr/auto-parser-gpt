"""
Работа с ChatGPT
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
        """
        Проверяет что мы находимся на странице проекта
        
        Возвращает: True если на странице проекта
        """
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
        """
        Создает новый чат
        
        Возвращает: True если успешно
        """
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
    
    def send_request(self, prompt, project=None, model=None, use_new_chat=True):
        """
        Отправляет запрос в ChatGPT
        
        Возвращает: (success, response_text, error_type, error_message)
        """
        try:
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
            
            error_type, error_msg = self.error_handler.check_for_errors()
            if error_type:
                print(f"    ⚠️ Ошибка: {error_msg}")
                if self.error_handler.handle_error(error_type):
                    print("    ✅ Обработана")
                else:
                    return False, None, error_type, error_msg
            
            print(f"  ✏️ Ищу поле ввода...")
            input_box = self.find_input_field()
            
            if not input_box:
                return False, None, 'not_found', "Поле ввода не найдено"
            
            print(f"  ✅ Поле найдено")
            
            print(f"  📝 Отправляю запрос...")
            input_box.click()
            time.sleep(1)
            
            self.driver.execute_script("arguments[0].value = '';", input_box)
            time.sleep(0.5)
            
            input_box.send_keys(prompt)
            time.sleep(1)
            
            input_box.send_keys(Keys.RETURN)
            
            return self.wait_for_response()
            
        except Exception as e:
            return False, None, 'exception', str(e)
    
    def wait_for_response(self):
        """Ожидает и получает ответ от ChatGPT"""
        try:
            print(f"  ⏳ Жду ответ ChatGPT...")
            time.sleep(10)
            
            try:
                WebDriverWait(self.driver, RESPONSE_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-message-author-role='assistant']"))
                )
            except TimeoutException:
                error_type, error_msg = self.error_handler.check_for_errors()
                if error_type:
                    return False, None, error_type, error_msg
                return False, None, 'timeout', "Ответ не появился"
            
            print(f"  ⏳ Жду завершения генерации...")
            elapsed = 0
            
            while elapsed < GENERATION_MAX_WAIT:
                error_type, error_msg = self.error_handler.check_for_errors()
                if error_type:
                    print(f"    ⚠️ Ошибка: {error_msg}")
                    if self.error_handler.handle_error(error_type):
                        continue
                    else:
                        return False, None, error_type, error_msg
                
                try:
                    stop_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Stop')] | //button[contains(text(), 'Остановить')]")
                    if not stop_buttons:
                        print(f"  ✅ Генерация завершена")
                        break
                except:
                    break
                
                time.sleep(2)
                elapsed += 2
            
            time.sleep(5)
            
            print(f"  📖 Читаю ответ...")
            
            max_read_attempts = 3
            for attempt in range(max_read_attempts):
                try:
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-message-author-role='assistant']")
                    
                    if messages:
                        last_message = messages[-1]
                        
                        # Используем textContent напрямую
                        response_text = self.driver.execute_script("""
                            return arguments[0].textContent;
                        """, last_message)
                        
                        if response_text and len(response_text.strip()) > 0:
                            print(f"  ✅ Ответ получен ({len(response_text)} символов)")
                            return True, response_text, None, None
                        else:
                            print(f"  ⚠️ Ответ пустой, попытка {attempt + 1}/{max_read_attempts}")
                            time.sleep(2)
                    else:
                        print(f"  ⚠️ Сообщения не найдены, попытка {attempt + 1}/{max_read_attempts}")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"  ⚠️ Ошибка чтения (попытка {attempt + 1}/{max_read_attempts}): {e}")
                    if attempt < max_read_attempts - 1:
                        time.sleep(2)
                    else:
                        return False, None, 'exception', str(e)
            
            return False, None, 'empty', "Не удалось прочитать ответ"
                
        except Exception as e:
            return False, None, 'exception', str(e)