"""
Сохранение результатов в JSON
"""
import json
import os
import re
from datetime import datetime
from config import *

class JSONHandler:
    """Класс для сохранения результатов в JSON"""
    
    def __init__(self, output_dir="json_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Создаем имя файла с текущей датой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_file = os.path.join(output_dir, f"results_{timestamp}.json")
        
        # Инициализируем пустой массив результатов
        self.results = []
    
    def clean_text(self, text):
        """
        Очищает текст от изображений и специальных символов
        
        Убирает:
        - Markdown изображения: ![alt](url)
        - HTML изображения: <img src="...">
        - Base64 изображения
        - Ссылки на изображения
        
        НО СОХРАНЯЕТ ПЕРЕНОСЫ СТРОК!
        """
        if not text:
            return ""
        
        # Убираем markdown изображения
        text = re.sub(r'!\[.*?\]\(.*?\)', '[IMAGE REMOVED]', text)
        
        # Убираем HTML изображения
        text = re.sub(r'<img[^>]*>', '[IMAGE REMOVED]', text)
        
        # Убираем base64 изображения (data:image/...)
        text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMAGE REMOVED]', text)
        
        # Убираем прямые ссылки на изображения
        text = re.sub(r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp|svg)', '[IMAGE URL REMOVED]', text, flags=re.IGNORECASE)
        
        # Убираем множественные пробелы НО СОХРАНЯЕМ ПЕРЕНОСЫ СТРОК!
        text = re.sub(r'[ \t]+', ' ', text)  # ✅ Удаляет только пробелы и табы, НЕ \n
        
        # Убираем пробелы в начале и конце каждой строки
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        # Убираем пустые строки в начале и конце
        text = text.strip()
        
        return text
    
    def add_result(self, row, request, response, status, error_message=None, 
                   project=None, model=None, attempts=1, duration=0):
        """
        Добавляет результат в список
        
        row: номер строки в Excel
        request: текст запроса
        response: текст ответа
        status: статус (Выполнен/Ошибка и т.д.)
        error_message: сообщение об ошибке (если есть)
        project: название проекта
        model: название модели
        attempts: количество попыток
        duration: длительность выполнения в секундах
        """
        # Очищаем текст от изображений
        clean_request = self.clean_text(request)
        clean_response = self.clean_text(response) if response else None
        
        result = {
            "row": row,
            "timestamp": datetime.now().isoformat(),
            "request": clean_request,
            "response": clean_response,
            "status": status,
            "success": status == STATUS_SUCCESS,
            "metadata": {
                "project": project,
                "model": model,
                "attempts": attempts,
                "duration_seconds": round(duration, 2),
                "error": error_message
            },
            "stats": {
                "request_length": len(clean_request) if clean_request else 0,
                "response_length": len(clean_response) if clean_response else 0
            }
        }
        
        self.results.append(result)
    
    def save(self):
        """
        Сохраняет результаты в JSON файл с форматированием
        """
        try:
            # Добавляем метаданные сессии
            output_data = {
                "session": {
                    "start_time": datetime.now().isoformat(),
                    "excel_file": EXCEL_FILE,
                    "total_requests": len(self.results),
                    "successful": sum(1 for r in self.results if r["success"]),
                    "failed": sum(1 for r in self.results if not r["success"])
                },
                "results": self.results
            }
            
            # Сохраняем с красивым форматированием (indent=2)
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 JSON сохранен: {self.json_file}")
            return True
            
        except Exception as e:
            print(f"\n❌ Ошибка сохранения JSON: {e}")
            return False
    
    def get_file_path(self):
        """Возвращает путь к JSON файлу"""
        return self.json_file
    
    def save_incremental(self):
        """
        Сохраняет результаты после каждого запроса
        (для надежности - если программа прервется)
        """
        return self.save()