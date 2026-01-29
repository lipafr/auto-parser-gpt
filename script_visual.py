from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from docx import Document
import time

print("🚀 Запускаем с визуальным браузером...")

# БЕЗ headless - браузер будет виден!
driver = webdriver.Chrome()

try:
    print("📱 Открываем сайт...")
    # ЗАМЕНИТЕ на ваш сайт
    driver.get("https://example.com")
    
    # Пауза, чтобы вы увидели что происходит
    time.sleep(3)
    
    print("✏️ Ищу поле ввода...")
    # Здесь вы УВИДИТЕ где скрипт пытается кликнуть
    input_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    input_field.send_keys("Тестовый текст")
    
    time.sleep(2)
    
    print("🔘 Ищу кнопку...")
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button")
    submit_btn.click()
    
    time.sleep(5)
    
    print("✅ Браузер останется открытым 30 секунд")
    time.sleep(30)
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    time.sleep(30)  # Оставим браузер открытым чтобы посмотреть
    
finally:
    driver.quit()