"""
Humanization - имитация поведения реального пользователя
Снижает риск детекции автоматизации
"""
import random
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

class HumanBehavior:
    """Класс для имитации человеческого поведения"""
    
    def __init__(self, config=None):
        """
        config: словарь с настройками или None для дефолтных
        """
        self.config = config or self._default_config()
    
    def _default_config(self):
        """Дефолтные настройки humanization"""
        return {
            # Интервалы между запросами
            'delay_min': 15,
            'delay_max': 45,
            'delay_micro_pauses': True,
            
            # Скорость набора
            'typing_wpm_min': 50,
            'typing_wpm_max': 90,
            
            # Опечатки
            'typo_enabled': True,
            'typo_probability': 0.03,
            
            # Случайные действия
            'random_actions_enabled': True,
            'random_actions_probability': 0.25,
            
            # Активность во время ожидания
            'simulate_reading': True,
            'reading_activity_interval': (10, 20),
            
            # Клики
            'human_click_enabled': True,
            'click_offset_range': 0.3,
            
            # Расписание
            'human_schedule_enabled': False,  # По умолчанию выключено
            'work_hours': (9, 18),
            'lunch_break': (13, 14),
            'mini_break_probability': 0.15,
            'mini_break_duration': (300, 900),
        }
    
    # ============================================================
    # ЗАДЕРЖКИ И ПАУЗЫ
    # ============================================================
    
    def get_request_delay(self):
        """
        Возвращает случайную задержку между запросами
        
        Имитирует реальное поведение:
        - Чтение предыдущего ответа: 10-30с
        - Размышление: 5-15с
        - Итого: 15-45с
        """
        delay = random.uniform(
            self.config['delay_min'],
            self.config['delay_max']
        )
        
        # Добавляем микропаузы для большей естественности
        if self.config['delay_micro_pauses']:
            micro_pauses = random.randint(0, 3)
            for _ in range(micro_pauses):
                delay += random.uniform(0.5, 2.0)
        
        return delay
    
    def pause(self, action="thinking"):
        """
        Имитирует человеческие паузы
        
        action:
        - thinking: размышление (2-8с)
        - reading: чтение (5-20с)
        - typing: пауза в наборе (0.5-2с)
        - navigating: навигация (1-3с)
        - verifying: проверка (2-5с)
        """
        pauses = {
            'thinking': (2.0, 8.0),
            'reading': (5.0, 20.0),
            'typing': (0.5, 2.0),
            'navigating': (1.0, 3.0),
            'verifying': (2.0, 5.0),
        }
        
        min_p, max_p = pauses.get(action, (1.0, 3.0))
        duration = random.uniform(min_p, max_p)
        
        print(f"  💭 Пауза ({action}): {duration:.1f}с")
        time.sleep(duration)
    
    # ============================================================
    # НАБОР ТЕКСТА
    # ============================================================
    
    def type_text(self, element, text, with_mistakes=None):
        """
        Печатает текст как человек
        
        element: WebElement поля ввода
        text: текст для ввода
        with_mistakes: включить опечатки (None = из config)
        """
        if with_mistakes is None:
            with_mistakes = self.config['typo_enabled']
        
        if with_mistakes:
            self._type_with_mistakes(element, text)
        else:
            self._type_simple(element, text)
    
    def _type_simple(self, element, text):
        """Простой набор без опечаток"""
        wpm = random.randint(
            self.config['typing_wpm_min'],
            self.config['typing_wpm_max']
        )
        
        chars_per_minute = wpm * 5  # Среднее слово = 5 символов
        base_delay = 60.0 / chars_per_minute
        
        words = text.split(' ')
        
        for i, word in enumerate(words):
            # Печатаем слово посимвольно
            for char in word:
                element.send_keys(char)
                
                # Случайная задержка
                char_delay = base_delay * random.uniform(0.5, 1.5)
                
                # Замедление на знаках препинания
                if char in '.,!?;:':
                    char_delay *= random.uniform(1.2, 2.0)
                
                time.sleep(char_delay)
            
            # Пробел между словами
            if i < len(words) - 1:
                element.send_keys(' ')
                word_delay = base_delay * random.uniform(2.0, 4.0)
                time.sleep(word_delay)
        
        # Финальная пауза (перечитывание)
        time.sleep(random.uniform(1.0, 3.0))
    
    def _type_with_mistakes(self, element, text):
        """Набор с редкими опечатками"""
        wpm = random.randint(
            self.config['typing_wpm_min'],
            self.config['typing_wpm_max']
        )
        
        chars_per_minute = wpm * 5
        base_delay = 60.0 / chars_per_minute
        typo_prob = self.config['typo_probability']
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Случайная опечатка?
            if char.isalnum() and random.random() < typo_prob:
                # Печатаем неправильный символ
                if char.isalpha():
                    wrong_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
                else:
                    wrong_char = str(random.randint(0, 9))
                
                element.send_keys(wrong_char)
                time.sleep(base_delay * random.uniform(0.5, 1.0))
                
                # Пауза (замечает ошибку)
                time.sleep(random.uniform(0.3, 0.8))
                
                # Backspace
                element.send_keys(Keys.BACKSPACE)
                time.sleep(base_delay * random.uniform(0.8, 1.2))
            
            # Печатаем правильный символ
            element.send_keys(char)
            
            char_delay = base_delay * random.uniform(0.5, 1.5)
            if char in '.,!?;:':
                char_delay *= random.uniform(1.2, 2.0)
            
            time.sleep(char_delay)
            i += 1
        
        # Финальная пауза
        time.sleep(random.uniform(1.0, 3.0))
    
    # ============================================================
    # КЛИКИ И ДВИЖЕНИЕ МЫШИ
    # ============================================================
    
    def click(self, driver, element):
        """
        Кликает как человек - со смещением
        
        driver: WebDriver
        element: WebElement для клика
        """
        if not self.config['human_click_enabled']:
            element.click()
            return
        
        try:
            size = element.size
            offset_range = self.config['click_offset_range']
            
            # Генерируем смещение
            offset_x = size['width'] * random.uniform(-offset_range, offset_range)
            offset_y = size['height'] * random.uniform(-offset_range, offset_range)
            
            # Двигаем мышку и кликаем
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            
            # Пауза после клика
            time.sleep(random.uniform(0.2, 0.5))
            
        except Exception as e:
            # Fallback к обычному клику
            print(f"  ⚠️ Human click failed: {e}, using normal click")
            element.click()
    
    def move_mouse_randomly(self, driver, duration=5):
        """
        Случайные движения мышкой
        
        driver: WebDriver
        duration: длительность (секунды)
        """
        start = time.time()
        actions = ActionChains(driver)
        
        movements = random.randint(3, 8)
        interval = duration / movements
        
        for _ in range(movements):
            x = random.randint(-100, 100)
            y = random.randint(-50, 50)
            
            actions.move_by_offset(x, y)
            actions.pause(interval)
        
        try:
            actions.perform()
        except:
            pass  # Игнорируем ошибки движения мыши
    
    # ============================================================
    # АКТИВНОСТЬ ВО ВРЕМЯ ОЖИДАНИЯ
    # ============================================================
    
    def simulate_reading(self, driver, duration=10):
        """
        Имитирует чтение во время ожидания ответа
        
        Действия:
        - Движение мышкой
        - Скролл
        - Паузы
        """
        if not self.config['simulate_reading']:
            time.sleep(duration)
            return
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            activity = random.choice([
                'move_mouse', 
                'small_scroll', 
                'pause', 
                'pause'  # Чаще просто ждем
            ])
            
            if activity == 'move_mouse':
                self.move_mouse_randomly(driver, duration=random.uniform(1, 3))
            
            elif activity == 'small_scroll':
                scroll_amount = random.randint(-100, 100)
                try:
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                except:
                    pass
            
            # Пауза между действиями
            time.sleep(random.uniform(1.0, 3.0))
    
    # ============================================================
    # СЛУЧАЙНЫЕ ДЕЙСТВИЯ
    # ============================================================
    
    def random_action(self, driver):
        """
        Выполняет случайное действие перед запросом
        
        Примеры:
        - Просмотр истории
        - Перечитывание предыдущего ответа
        - Скролл
        - Движение мыши
        """
        if not self.config['random_actions_enabled']:
            return
        
        if random.random() > self.config['random_actions_probability']:
            return
        
        action = random.choice([
            'check_history',
            'read_previous',
            'scroll_chat',
            'move_mouse',
            'long_pause'
        ])
        
        print(f"  🎭 Случайное действие: {action}")
        
        if action == 'check_history':
            print("  📜 Просматриваю историю...")
            try:
                sidebar = driver.find_element(By.TAG_NAME, "nav")
                driver.execute_script("arguments[0].scrollTop += 100", sidebar)
                time.sleep(random.uniform(1, 3))
            except:
                pass
        
        elif action == 'read_previous':
            print("  👀 Перечитываю предыдущий ответ...")
            time.sleep(random.uniform(3, 8))
        
        elif action == 'scroll_chat':
            print("  📜 Скроллю чат...")
            scroll = random.randint(-200, 200)
            try:
                driver.execute_script(f"window.scrollBy(0, {scroll})")
            except:
                pass
            time.sleep(random.uniform(0.5, 2))
        
        elif action == 'move_mouse':
            print("  🖱️  Двигаю мышку...")
            self.move_mouse_randomly(driver, duration=random.uniform(2, 4))
        
        elif action == 'long_pause':
            print("  💭 Долгая пауза для размышления...")
            time.sleep(random.uniform(3, 8))


class HumanSchedule:
    """
    Имитирует человеческое расписание работы
    
    Человек не работает 24/7!
    """
    
    def __init__(self, config=None):
        config = config or {}
        
        self.enabled = config.get('human_schedule_enabled', False)
        
        # Рабочие часы
        work_hours = config.get('work_hours', (9, 18))
        self.work_start = work_hours[0]
        self.work_end = work_hours[1]
        
        # Обеденный перерыв
        lunch = config.get('lunch_break', (13, 14))
        self.lunch_start = lunch[0]
        self.lunch_end = lunch[1]
        
        # Мини-перерывы
        self.break_probability = config.get('mini_break_probability', 0.15)
        self.break_duration = config.get('mini_break_duration', (300, 900))
    
    def should_work_now(self):
        """
        Проверяет можно ли сейчас работать
        
        Возвращает: (bool, str)
        """
        if not self.enabled:
            return True, "Расписание отключено"
        
        now = datetime.now()
        hour = now.hour
        
        # Ночное время
        if hour < self.work_start or hour >= self.work_end:
            return False, f"Нерабочее время ({hour}:00), рабочие часы: {self.work_start}:00-{self.work_end}:00"
        
        # Обеденный перерыв
        if self.lunch_start <= hour < self.lunch_end:
            return False, f"Обеденный перерыв ({self.lunch_start}:00-{self.lunch_end}:00)"
        
        return True, "Рабочее время"
    
    def wait_until_work_hours(self):
        """Ждет начала рабочего времени"""
        if not self.enabled:
            return
        
        while True:
            can_work, reason = self.should_work_now()
            if can_work:
                print(f"  ✅ {reason}")
                return
            
            print(f"  😴 {reason}")
            
            # Вычисляем когда начнется рабочее время
            now = datetime.now()
            hour = now.hour
            
            if hour < self.work_start:
                # До начала работы
                wait_minutes = (self.work_start - hour) * 60
            elif self.lunch_start <= hour < self.lunch_end:
                # Обед
                wait_minutes = (self.lunch_end - hour) * 60
            else:
                # После работы - ждем до завтра
                wait_minutes = (24 - hour + self.work_start) * 60
            
            print(f"  ⏰ Следующая проверка через 5 минут (до работы осталось ~{wait_minutes} мин)")
            time.sleep(300)  # 5 минут
    
    def should_take_break(self):
        """
        Решает нужен ли мини-перерыв
        
        Возвращает: (bool, int) - (нужен ли перерыв, длительность в секундах)
        """
        if not self.enabled:
            return False, 0
        
        if random.random() < self.break_probability:
            duration = random.randint(*self.break_duration)
            return True, duration
        
        return False, 0
    
    def take_break_if_needed(self):
        """Берет перерыв если нужно"""
        if not self.enabled:
            return
        
        should_break, duration = self.should_take_break()
        
        if should_break:
            minutes = duration // 60
            print(f"  ☕ Мини-перерыв на {minutes} минут")
            
            # Разбиваем на интервалы по 60 секунд для возможности прерывания
            intervals = duration // 60
            for i in range(intervals):
                remaining = intervals - i
                print(f"  ⏳ Перерыв: осталось {remaining} минут...")
                time.sleep(60)
            
            # Остаток
            remaining_seconds = duration % 60
            if remaining_seconds > 0:
                time.sleep(remaining_seconds)
            
            print(f"  ✅ Перерыв завершен, продолжаю работу")


# ============================================================
# УТИЛИТЫ
# ============================================================

def get_random_viewport_size():
    """Возвращает случайный размер окна браузера"""
    sizes = [
        (1366, 768),
        (1440, 900),
        (1536, 1024),
        (1920, 1080),
        (1600, 900),
        (1280, 720),
    ]
    return random.choice(sizes)


def set_random_viewport(driver):
    """Устанавливает случайный размер окна"""
    width, height = get_random_viewport_size()
    driver.set_window_size(width, height)
    print(f"  🖥️  Размер окна: {width}x{height}")


# ============================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================

if __name__ == "__main__":
    print("Демонстрация humanization модуля")
    print("=" * 70)
    
    # Создаем объект с дефолтными настройками
    human = HumanBehavior()
    
    print("\n1. Задержка между запросами:")
    delay = human.get_request_delay()
    print(f"   {delay:.2f} секунд")
    
    print("\n2. Различные паузы:")
    actions = ['thinking', 'reading', 'typing', 'verifying']
    for action in actions:
        print(f"   {action}:")
        # human.pause(action)  # Раскомментируйте для реального ожидания
        print(f"   (пропущено в демо)")
    
    print("\n3. Расписание:")
    schedule = HumanSchedule({'human_schedule_enabled': True})
    can_work, reason = schedule.should_work_now()
    print(f"   Можно работать: {can_work}")
    print(f"   Причина: {reason}")
    
    should_break, duration = schedule.should_take_break()
    print(f"   Нужен перерыв: {should_break}")
    if should_break:
        print(f"   Длительность: {duration//60} минут")
    
    print("\n" + "=" * 70)
    print("✅ Модуль готов к использованию!")