"""
Сохранение результатов в отдельные JSON файлы
Каждый запрос = отдельный JSON файл
"""
import json
import os
import re
from datetime import datetime
from config import *

class JSONHandlerV2:
    """Класс для сохранения каждого запроса в отдельный JSON"""
    
    def __init__(self, output_dir="json_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _transliterate(self, text):
        """Транслитерация кириллицы в латиницу"""
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
            'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
            'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
            'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
            'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch',
            'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
            'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        result = []
        for char in text:
            result.append(translit_dict.get(char, char))
        
        return ''.join(result)
    
    def _sanitize_filename(self, text, max_length=60):
        """
        Очищает текст для использования в имени файла
        
        1. Транслитерирует кириллицу
        2. Убирает запрещенные символы
        3. Ограничивает длину до 60 символов
        4. Приводит к нижнему регистру
        """
        if not text:
            return "untitled"
        
        # Транслитерация кириллицы
        text = self._transliterate(text)
        
        # Убираем запрещенные символы Windows: < > : " / \ | ? *
        forbidden = r'[<>:"/\\|?*\x00-\x1f]'
        text = re.sub(forbidden, '', text)
        
        # Заменяем пробелы, переносы, табы на подчеркивания
        text = re.sub(r'[\s\n\r\t]+', '_', text)
        
        # Убираем множественные подчеркивания
        text = re.sub(r'_{2,}', '_', text)
        
        # Убираем спецсимволы (оставляем только буквы, цифры, подчеркивания, дефисы)
        text = re.sub(r'[^\w\-]', '', text)
        
        # Ограничиваем длину
        text = text[:max_length]
        
        # Убираем подчеркивания в начале и конце
        text = text.strip('_-')
        
        # Приводим к нижнему регистру
        text = text.lower()
        
        return text or "untitled"
    
    def save_request(self, row, request, response, status, 
                    error_message=None, project=None, model=None, 
                    attempts=1, duration=0):
        """
        Сохраняет запрос в отдельный JSON файл
        
        Формат имени: {sanitized_request}_{timestamp}.json
        Пример: napishy_stikh_pro_kota_20260129_170533_123.json
        """
        try:
            # Генерируем timestamp с миллисекундами для уникальности
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # YYYYMMDD_HHMMSS_mmm
            
            # Очищаем запрос для имени файла
            sanitized_request = self._sanitize_filename(request, max_length=60)
            
            # Формируем имя файла
            filename = f"{sanitized_request}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Формируем данные
            data = {
                "metadata": {
                    "row": row,
                    "timestamp": datetime.now().isoformat(),
                    "project": project,
                    "model": model,
                    "attempts": attempts,
                    "duration_seconds": round(duration, 2)
                },
                "request": request,
                "response": response,
                "status": status,
                "success": status == STATUS_SUCCESS,
                "error": error_message,
                "stats": {
                    "request_length": len(request) if request else 0,
                    "response_length": len(response) if response else 0
                }
            }
            
            # Сохраняем с форматированием
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  📄 JSON: {filename}")
            return filepath
            
        except Exception as e:
            print(f"  ❌ Ошибка сохранения JSON: {e}")
            return None