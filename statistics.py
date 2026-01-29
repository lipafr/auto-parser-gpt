"""
Расширенная статистика
"""
import time
from datetime import datetime, timedelta
from config import *

class Statistics:
    """Класс для сбора и отображения статистики"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.requests_data = []
        
    def start(self):
        """Начинает отсчет времени"""
        self.start_time = time.time()
    
    def end(self):
        """Заканчивает отсчет времени"""
        self.end_time = time.time()
    
    def add_request(self, row, success, duration, attempts, error_type=None):
        """Добавляет данные об обработанном запросе"""
        self.requests_data.append({
            'row': row,
            'success': success,
            'duration': duration,
            'attempts': attempts,
            'error_type': error_type,
            'timestamp': datetime.now()
        })
    
    def get_total_duration(self):
        """Возвращает общее время работы"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0
    
    def get_success_rate(self):
        """Возвращает процент успешных запросов"""
        if not self.requests_data:
            return 0
        
        success_count = sum(1 for r in self.requests_data if r['success'])
        return (success_count / len(self.requests_data)) * 100
    
    def get_average_duration(self):
        """Возвращает среднее время обработки запроса"""
        if not self.requests_data:
            return 0
        
        total_duration = sum(r['duration'] for r in self.requests_data)
        return total_duration / len(self.requests_data)
    
    def get_average_attempts(self):
        """Возвращает среднее количество попыток"""
        if not self.requests_data:
            return 0
        
        total_attempts = sum(r['attempts'] for r in self.requests_data)
        return total_attempts / len(self.requests_data)
    
    def get_error_breakdown(self):
        """Возвращает разбивку по типам ошибок"""
        error_counts = {}
        for r in self.requests_data:
            if not r['success'] and r['error_type']:
                error_counts[r['error_type']] = error_counts.get(r['error_type'], 0) + 1
        return error_counts
    
    def get_requests_per_minute(self):
        """Возвращает количество запросов в минуту"""
        duration = self.get_total_duration()
        if duration == 0:
            return 0
        return (len(self.requests_data) / duration) * 60
    
    def estimate_remaining_time(self, pending_count):
        """Оценивает оставшееся время"""
        avg_duration = self.get_average_duration()
        if avg_duration == 0:
            return None
        
        return pending_count * avg_duration
    
    def format_duration(self, seconds):
        """Форматирует длительность в читаемый вид"""
        if seconds < 60:
            return f"{seconds:.1f} сек"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} мин"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} ч"
    
    def print_summary(self):
        """Выводит итоговую статистику"""
        print("\n" + "=" * 70)
        print("📊 ПОДРОБНАЯ СТАТИСТИКА")
        print("=" * 70)
        
        # Общее время
        total_duration = self.get_total_duration()
        print(f"\n⏱️  Время работы:")
        print(f"   • Начало: {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
        if self.end_time:
            print(f"   • Конец: {datetime.fromtimestamp(self.end_time).strftime('%H:%M:%S')}")
        print(f"   • Общая длительность: {self.format_duration(total_duration)}")
        
        # Статистика запросов
        success_count = sum(1 for r in self.requests_data if r['success'])
        error_count = len(self.requests_data) - success_count
        
        print(f"\n📝 Обработано запросов:")
        print(f"   • Всего: {len(self.requests_data)}")
        print(f"   • Успешно: {success_count} ({self.get_success_rate():.1f}%)")
        print(f"   • Ошибок: {error_count}")
        
        # Средние показатели
        print(f"\n📈 Средние показатели:")
        print(f"   • Время на запрос: {self.format_duration(self.get_average_duration())}")
        print(f"   • Попыток на запрос: {self.get_average_attempts():.1f}")
        print(f"   • Запросов в минуту: {self.get_requests_per_minute():.1f}")
        
        # Разбивка ошибок
        error_breakdown = self.get_error_breakdown()
        if error_breakdown:
            print(f"\n⚠️  Типы ошибок:")
            for error_type, count in sorted(error_breakdown.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {error_type}: {count}")
        
        # Самые быстрые и медленные запросы
        if self.requests_data:
            fastest = min(self.requests_data, key=lambda x: x['duration'])
            slowest = max(self.requests_data, key=lambda x: x['duration'])
            
            print(f"\n⚡ Экстремумы:")
            print(f"   • Самый быстрый: строка {fastest['row']} ({self.format_duration(fastest['duration'])})")
            print(f"   • Самый медленный: строка {slowest['row']} ({self.format_duration(slowest['duration'])})")
        
        print("=" * 70)
    
    def print_progress(self, current, total):
        """Выводит прогресс выполнения"""
        percent = (current / total) * 100
        
        # Оценка оставшегося времени
        remaining = total - current
        estimated_time = self.estimate_remaining_time(remaining)
        
        print(f"\n📊 Прогресс: {current}/{total} ({percent:.1f}%)")
        
        if estimated_time:
            print(f"⏱️  Осталось примерно: {self.format_duration(estimated_time)}")