from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

print("🚀 Запускаю Chrome...")
print("⏳ Скачиваю ChromeDriver (только в первый раз, может занять 2-5 минут)...")

# Добавим больше информации
service = Service(ChromeDriverManager().install())
print("✅ ChromeDriver готов!")

print("🌐 Открываю браузер...")
driver = webdriver.Chrome(service=service)

try:
    print("📱 Открываю Google...")
    driver.get("https://www.google.com")
    
    print("✅ Браузер открыт! Смотрите на экран")
    time.sleep(10)
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    
finally:
    driver.quit()
    print("🔚 Готово!")