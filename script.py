from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from docx import Document
import time

print("🚀 Запускаем автоматизацию...")

# Настройки браузера
chrome_options = Options()
chrome_options.add_argument('--headless')  # Без окна браузера
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.binary_location = '/usr/bin/chromium'

driver = webdriver.Chrome(options=chrome_options)

try:
    print("📱 Открываем сайт...")
    # TODO: ЗАМЕНИТЕ на ваш сайт
    driver.get("https://example.com")
    
    print("✏️ Вставляем текст...")
    # TODO: ЗАМЕНИТЕ селектор на правильный
    input_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    input_field.send_keys("Привет! Это тестовый текст")
    
    print("🔘 Нажимаем кнопку...")
    # TODO: ЗАМЕНИТЕ селектор на правильный
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()
    
    print("⏳ Ждем ответ (макс 60 сек)...")
    # TODO: ЗАМЕНИТЕ селектор на правильный
    wait = WebDriverWait(driver, 60)
    response = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".response"))
    )
    
    result_text = response.text
    print(f"✅ Получен ответ ({len(result_text)} символов)")
    
    print("💾 Сохраняем в Word...")
    doc = Document()
    doc.add_paragraph(result_text)
    doc.save('/app/output/result.docx')
    
    print("🎉 Готово! Файл сохранен в папке output")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    
finally:
    driver.quit()