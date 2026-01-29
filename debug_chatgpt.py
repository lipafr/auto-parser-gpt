"""
Отладочный скрипт для поиска элементов проектов и моделей
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

print("🔍 Debug ChatGPT - Поиск элементов интерфейса")
print("=" * 70)

# Настройка браузера
options = uc.ChromeOptions()
options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

profile_dir = os.path.abspath(os.path.join(os.getcwd(), "chatgpt_profile"))
options.add_argument(f"--user-data-dir={profile_dir}")

driver = uc.Chrome(options=options, version_main=None)

try:
    print("\n📱 Открываю ChatGPT...")
    driver.get("https://chat.openai.com/")
    
    print("\n⏳ Залогиньтесь и откройте главную страницу ChatGPT")
    input("Нажмите ENTER когда будете на главной странице >>> ")
    
    print("\n" + "=" * 70)
    print("🔍 ШАГ 1: Поиск селектора модели")
    print("=" * 70)
    
    # Сохраняем HTML страницы
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✅ HTML страницы сохранен в page_source.html")
    
    # Ищем все кнопки
    print("\n🔍 Ищу все кнопки на странице...")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"   Найдено кнопок: {len(buttons)}")
    
    print("\n🔍 Кнопки с текстом 'GPT' или 'Model':")
    for idx, btn in enumerate(buttons):
        try:
            text = btn.text
            if text and ('gpt' in text.lower() or 'model' in text.lower() or '4' in text):
                print(f"   [{idx}] Текст: '{text[:50]}' | Visible: {btn.is_displayed()}")
                print(f"       HTML: {btn.get_attribute('outerHTML')[:150]}")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("🔍 ШАГ 2: Поиск навигации/меню")
    print("=" * 70)
    
    # Ищем nav элементы
    navs = driver.find_elements(By.TAG_NAME, "nav")
    print(f"   Найдено nav элементов: {len(navs)}")
    
    for idx, nav in enumerate(navs):
        print(f"\n   [NAV {idx}]:")
        links = nav.find_elements(By.TAG_NAME, "a")
        print(f"   Найдено ссылок: {len(links)}")
        for link in links[:10]:  # Первые 10
            try:
                text = link.text
                href = link.get_attribute('href')
                if text:
                    print(f"      • '{text}' -> {href}")
            except:
                pass
    
    print("\n" + "=" * 70)
    print("🔍 ШАГ 3: Поиск проектов")
    print("=" * 70)
    
    # Ищем ваш проект
    print(f"\n🔍 Ищу 'MyProject'...")
    
    # Попытка 1: По тексту
    all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'MyProject')]")
    print(f"   Найдено элементов с текстом 'MyProject': {len(all_elements)}")
    
    for idx, elem in enumerate(all_elements[:5]):
        try:
            print(f"   [{idx}] Tag: {elem.tag_name} | Text: '{elem.text[:50]}' | Visible: {elem.is_displayed()}")
            print(f"       HTML: {elem.get_attribute('outerHTML')[:200]}")
        except:
            pass
    
    # Попытка 2: Все ссылки
    all_links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\n🔍 Все ссылки на странице: {len(all_links)}")
    print("   Первые 20 ссылок:")
    for idx, link in enumerate(all_links[:20]):
        try:
            text = link.text
            href = link.get_attribute('href')
            if text or 'chat.openai.com' in (href or ''):
                print(f"   [{idx}] '{text[:30]}' -> {href}")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("💡 ИНСТРУКЦИИ")
    print("=" * 70)
    print("1. Откройте файл page_source.html в браузере")
    print("2. Найдите селектор модели (GPT-4, GPT-4o и т.д.) в HTML")
    print("3. Найдите ссылку на ваш проект 'MyProject'")
    print("4. Скопируйте селекторы и пришлите мне")
    print("\nИЛИ:")
    print("5. Нажмите F12 в этом окне браузера")
    print("6. Используйте инспектор (стрелка в левом верхнем углу)")
    print("7. Кликните на кнопку выбора модели")
    print("8. Скопируйте HTML элемента")
    print("9. Кликните на ваш проект в боковом меню")
    print("10. Скопируйте HTML элемента")
    
    print("\n⏸️  Браузер останется открытым...")
    input("Нажмите ENTER когда закончите изучение >>> ")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    input("Нажмите ENTER...")
    
finally:
    driver.quit()
    print("\n✅ Готово")