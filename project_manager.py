"""
Управление проектами и моделями ChatGPT
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from config import *

class ProjectManager:
    """Класс для работы с проектами и моделями ChatGPT"""
    
    def __init__(self, driver):
        self.driver = driver
        self.current_project = None
        self.current_model = None
    
    def switch_model(self, model_name):
        """
        Переключает модель ChatGPT
        
        Возвращает: True если успешно
        """
        if not model_name or model_name.lower() in ['none', 'default']:
            return True
        
        try:
            print(f"  🤖 Переключаю модель на: '{model_name}'...")
            
            # Маппинг моделей
            # Модели из основного меню (это режимы GPT-5.2)
            main_menu_models = {
                'auto': ['Auto'],
                'instant': ['Instant'],
                'thinking': ['Thinking'],
            }

            # Модели из "Устаревшие модели"
            legacy_models = {
                'gpt-5.2': ['GPT-5.2'],  # Если вдруг понадобится
                'gpt-5.1': ['GPT-5.1 Instant', 'GPT-5.1 Thinking'],
                'gpt-5': ['GPT-5 Instant', 'GPT-5 Thinking mini', 'GPT-5 Thinking'],
                'gpt-4o': ['GPT-4o'],
                'gpt-4': ['GPT-4.1'],
                'o3': ['o3'],
                'o4-mini': ['o4-mini'],
            }

            model_key = model_name.lower().strip()

            # ВСЕ модели кроме режимов 5.2 — в устаревших!
            is_legacy = model_key in legacy_models
            
            # Определяем где искать модель
            is_legacy = model_key in legacy_models
            search_variants = legacy_models.get(model_key) or main_menu_models.get(model_key, [model_name])
            
            print(f"  🔍 Модель в {'устаревших' if is_legacy else 'основном меню'}")
            print(f"  🔍 Ищу варианты: {search_variants}")
            
            # ШАГ 1: Открываем основное меню
            print(f"  🖱️  Открываю меню моделей...")
            
            model_button = None
            selectors = [
                (By.CSS_SELECTOR, "button[data-testid='model-switcher-dropdown-button']"),
                (By.XPATH, "//button[contains(., 'ChatGPT')]"),
            ]
            
            for by, selector in selectors:
                try:
                    model_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if model_button:
                        break
                except:
                    continue
            
            if not model_button:
                print(f"  ❌ Кнопка не найдена")
                return False
            
            model_button.click()
            time.sleep(2)
            
            # ШАГ 2: Если модель в устаревших - открываем подменю
            if is_legacy:
                print(f"  📂 Открываю 'Устаревшие модели'...")
                
                # Ищем кнопку "Устаревшие модели"
                legacy_selectors = [
                    (By.XPATH, "//div[text()='Устаревшие модели']"),
                    (By.XPATH, "//*[contains(text(), 'Устаревшие модели')]"),
                    (By.XPATH, "//div[contains(text(), 'Legacy')]"),
                ]
                
                legacy_found = False
                for by, selector in legacy_selectors:
                    try:
                        legacy_elem = self.driver.find_element(by, selector)
                        if legacy_elem and legacy_elem.is_displayed():
                            print(f"  ✅ Нашел 'Устаревшие модели'")
                            # Кликаем через JavaScript (надежнее)
                            self.driver.execute_script("arguments[0].click();", legacy_elem)
                            time.sleep(2)
                            legacy_found = True
                            break
                    except:
                        continue
                
                if not legacy_found:
                    print(f"  ⚠️ 'Устаревшие модели' не найдены")
                    return False
            
            # ШАГ 3: Ищем модель в открытом меню
            print(f"  🔍 Ищу модель в меню...")
            
            for variant in search_variants:
                # Ищем точное совпадение текста
                xpath_selectors = [
                    f"//div[text()='{variant}' and not(contains(text(), 'Думает') or contains(text(), 'Отвечает'))]",
                    f"//*[text()='{variant}']",
                ]
                
                for xpath in xpath_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for elem in elements:
                            if elem.is_displayed():
                                # Проверяем что это не подзаголовок
                                if len(elem.text.strip()) < 50:
                                    print(f"  ✅ Нашел: {variant}")
                                    # Кликаем через JavaScript
                                    self.driver.execute_script("arguments[0].click();", elem)
                                    time.sleep(MODEL_SWITCH_DELAY)
                                    self.current_model = model_key
                                    print(f"  ✅ Модель переключена!")
                                    return True
                    except:
                        continue
            
            print(f"  ⚠️ Модель '{model_name}' не найдена")
            
            # Закрываем меню
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def switch_to_project(self, project_name):
        """
        Переключается на проект
        
        Возвращает: True если успешно
        """
        if not project_name or project_name.lower() in ['none', 'default', 'main']:
            return self._go_to_main_page()
        
        try:
            print(f"  📁 Переключаюсь на проект: '{project_name}'...")
            
            success = self._find_and_click_project(project_name)
            
            if success:
                self.current_project = project_name
                print(f"  ✅ Переключен на проект!")
                time.sleep(PROJECT_SWITCH_DELAY)
                return True
            else:
                print(f"  ⚠️ Проект не найден")
                return False
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def _go_to_main_page(self):
        """Переход на главную"""
        try:
            if self.current_project:
                print(f"  🏠 Возвращаюсь на главную...")
                self.driver.get(CHATGPT_URL)
                time.sleep(PROJECT_SWITCH_DELAY)
                self.current_project = None
                print(f"  ✅ На главной")
            return True
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def _find_and_click_project(self, project_name):
        """Ищет и кликает на проект"""
        try:
            print(f"  🔍 Ищу проект...")
            
            # Через ссылки с href="/g/g-p-.../project"
            project_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/project']")
            
            for link in project_links:
                try:
                    text_divs = link.find_elements(By.CSS_SELECTOR, "div.truncate")
                    for text_div in text_divs:
                        text = text_div.text.strip()
                        
                        if text.lower() == project_name.lower():
                            print(f"  ✅ Нашел проект: '{text}'")
                            
                            # JavaScript клик
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", link)
                            
                            print(f"  🖱️  Кликнул")
                            return True
                except:
                    continue
            
            # JavaScript поиск
            print(f"  🔍 Пробую через JavaScript...")
            script = f"""
                let links = document.querySelectorAll('a[href*="/project"]');
                for (let link of links) {{
                    let textDivs = link.querySelectorAll('div.truncate');
                    for (let div of textDivs) {{
                        if (div.textContent.trim().toLowerCase() === '{project_name.lower()}') {{
                            link.scrollIntoView({{block: 'center'}});
                            setTimeout(() => link.click(), 100);
                            return true;
                        }}
                    }}
                }}
                return false;
            """
            result = self.driver.execute_script(script)
            
            if result:
                print(f"  ✅ Проект найден через JavaScript")
                return True
            
            return False
            
        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
            return False
    
    def get_current_context(self):
        """Возвращает текущий контекст"""
        return {
            'project': self.current_project,
            'model': self.current_model
        }
    
    def setup_context(self, project_name=None, model_name=None):
        """
        Настраивает контекст: проект + модель
        
        Возвращает: True если успешно
        """
        success = True
        
        if project_name and project_name != self.current_project:
            if not self.switch_to_project(project_name):
                success = False
                print(f"  ⚠️ Продолжаю без проекта")
        
        if model_name and model_name != self.current_model:
            if not self.switch_model(model_name):
                print(f"  ⚠️ Продолжаю с текущей моделью")
        
        return success