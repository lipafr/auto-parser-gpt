"""
Управление резервными копиями
"""
import shutil
import os
from datetime import datetime
from config import *

class BackupManager:
    """Класс для создания и управления резервными копиями"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, filename):
        """
        Создает резервную копию файла
        Возвращает путь к резервной копии или None при ошибке
        """
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден, backup не создан")
            return None
        
        try:
            # Генерируем имя backup файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.basename(filename)
            name, ext = os.path.splitext(base_name)
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Копируем файл
            shutil.copy2(filename, backup_path)
            
            file_size = os.path.getsize(backup_path)
            print(f"✅ Резервная копия создана: {backup_filename} ({file_size} bytes)")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Ошибка при создании backup: {e}")
            return None
    
    def cleanup_old_backups(self, keep_last=5):
        """
        Удаляет старые backup файлы, оставляя только последние N
        """
        try:
            # Получаем список всех backup файлов
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backups.append((filepath, mtime, filename))
            
            # Сортируем по времени (новые первые)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Удаляем старые
            if len(backups) > keep_last:
                print(f"\n🧹 Очистка старых backup файлов (оставляю последние {keep_last})...")
                for filepath, _, filename in backups[keep_last:]:
                    try:
                        os.remove(filepath)
                        print(f"   ✅ Удален: {filename}")
                    except Exception as e:
                        print(f"   ⚠️ Не удалось удалить {filename}: {e}")
            
        except Exception as e:
            print(f"⚠️ Ошибка при очистке backup: {e}")
    
    def restore_backup(self, backup_path, target_path):
        """Восстанавливает файл из резервной копии"""
        try:
            if not os.path.exists(backup_path):
                print(f"❌ Backup файл {backup_path} не найден")
                return False
            
            shutil.copy2(backup_path, target_path)
            print(f"✅ Файл восстановлен из backup: {os.path.basename(backup_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при восстановлении backup: {e}")
            return False
    
    def list_backups(self):
        """Возвращает список всех backup файлов"""
        backups = []
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)
                    backups.append({
                        'filename': filename,
                        'path': filepath,
                        'date': datetime.fromtimestamp(mtime),
                        'size': size
                    })
            
            # Сортируем по дате (новые первые)
            backups.sort(key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Ошибка при получении списка backup: {e}")
        
        return backups
    
    def print_backups(self):
        """Выводит список backup файлов"""
        backups = self.list_backups()
        
        if not backups:
            print("📦 Backup файлов нет")
            return
        
        print(f"\n📦 Найдено backup файлов: {len(backups)}")
        print("-" * 70)
        for i, backup in enumerate(backups, 1):
            date_str = backup['date'].strftime("%Y-%m-%d %H:%M:%S")
            size_kb = backup['size'] / 1024
            print(f"{i}. {backup['filename']}")
            print(f"   Дата: {date_str} | Размер: {size_kb:.1f} KB")
        print("-" * 70)