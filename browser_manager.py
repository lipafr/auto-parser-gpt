"""
Управление браузером
"""
import undetected_chromedriver as uc
import os
from config import *

class BrowserManager:
    """Класс для управления браузером"""
    
    def __init__(self):
        self.driver = None
    
    def start(self):
        """Запускает браузер"""
        try:
            print("🌐 Настраиваю браузер...")
            
            options = uc.ChromeOptions()
            options.binary_location = BRAVE_PATH
            
            # Создаем директорию профиля
            os.makedirs(PROFILE_DIR, exist_ok=True)
            options.add_argument(f"--user-data-dir={PROFILE_DIR}")
            
            print("🚀 Запускаю браузер...")
            
            # ВАЖНО: Указываем версию 144 явно!
            self.driver = uc.Chrome(
                options=options,
                version_main=144,  # ✨ Явно указываем версию!
                use_subprocess=False
            )
            
            print("✅ Браузер запущен!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при запуске: {e}")
            
            # Попытка 2: Вообще без указания версии, пусть сам определит
            try:
                print("\n💡 Пробую автоматическое определение версии...")
                options2 = uc.ChromeOptions()
                options2.binary_location = BRAVE_PATH
                options2.add_argument(f"--user-data-dir={PROFILE_DIR}")
                
                self.driver = uc.Chrome(
                    options=options2,
                    driver_executable_path=None,  # Пусть сам скачает
                    use_subprocess=False
                )
                
                print("✅ Браузер запущен!")
                return True
                
            except Exception as e2:
                print(f"❌ Не получилось: {e2}")
                return False
    
    def open_chatgpt(self):
        """Открывает ChatGPT"""
        try:
            print(f"📱 Открываю {CHATGPT_URL}...")
            self.driver.get(CHATGPT_URL)
            return True
        except Exception as e:
            print(f"❌ Ошибка при открытии ChatGPT: {e}")
            return False
    
    def close(self):
        """Закрывает браузер"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except:
                pass
    
    def get_driver(self):
        """Возвращает драйвер"""
        return self.driver