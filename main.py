"""
Главный файл - точка входа в программу v4.0
Production Ready - Full Version with Projects & Models Support + JSON Export
"""
import time
import os
from config import *
from excel_handler import ExcelHandler
from browser_manager import BrowserManager
from chatgpt_handler import ChatGPTHandler
from logger import Logger
from retry_handler import RetryHandler
from validator import Validator
from backup_manager import BackupManager
from statistics import Statistics
from json_handler_v2 import JSONHandlerV2
from humanization import HumanBehavior, HumanSchedule

def print_header():
    """Печатает заголовок программы"""
    print("=" * 70)
    print("🚀 ChatGPT Batch Parser - Production Ready v4.0")
    print("   С поддержкой проектов, моделей и JSON экспорта")
    print("=" * 70)

def print_statistics(stats):
    """Печатает статистику Excel"""
    print(f"\n📊 Статистика Excel:")
    print(f"   • Всего запросов: {stats['total']}")
    print(f"   • Выполнено: {stats['success']}")
    print(f"   • Ошибок: {stats['errors']}")
    print(f"   • Ожидают: {stats['pending']}")

def manual_login():
    """Ручная авторизация"""
    print("\n" + "=" * 70)
    print("📋 ШАГ 1: АВТОРИЗАЦИЯ (РУЧНОЙ РЕЖИМ)")
    print("=" * 70)
    print("✋ Залогиньтесь в ChatGPT:")
    print("   1. Введите логин/пароль (если нужно)")
    print("   2. Введите код из email (если попросит)")
    print("   3. Дождитесь загрузки главной страницы")
    print("   4. Убедитесь что видите поле ввода внизу")
    print("\n💡 Совет: если используете проекты - убедитесь что у вас к ним есть доступ")
    print("\n👉 Нажмите ENTER когда будете готовы")
    print("=" * 70)
    
    input("\n⏸️  >>> ")
    print("\n✅ Отлично! Даю странице 5 секунд...")
    time.sleep(5)

def process_requests(excel_handler, chatgpt_handler, logger, retry_handler, stats):
    """Обрабатывает все запросы (главная функция маршрутизации)"""
    
    if USE_NEW_CHAT_FOR_EACH_REQUEST:
        process_requests_separate_chats(excel_handler, chatgpt_handler, logger, retry_handler, stats)
    else:
        process_requests_single_chat(excel_handler, chatgpt_handler, logger, retry_handler, stats)

def process_requests_separate_chats(excel_handler, chatgpt_handler, logger, retry_handler, stats):
    """Обрабатывает запросы - каждый в новом чате"""
    pending = excel_handler.get_pending_requests()
    
    if not pending:
        print("\n✅ Все запросы уже выполнены!")
        if logger:
            logger.info("Нет невыполненных запросов")
        return
    
    print("\n" + "=" * 70)
    print("📋 ШАГ 2: АВТОМАТИЧЕСКАЯ ОБРАБОТКА")
    print("=" * 70)
    print(f"🆕 Режим: НОВЫЙ ЧАТ ДЛЯ КАЖДОГО ЗАПРОСА")
    print(f"🔄 Начинаю обрабатывать {len(pending)} запросов...")
    if logger:
        logger.info(f"Начало обработки {len(pending)} запросов (режим: новый чат для каждого)")
    print("=" * 70)
    
    # Создаем JSON handler V2 (отдельный файл для каждого запроса)
    json_handler = JSONHandlerV2(JSON_OUTPUT_DIR) if JSON_ENABLED else None
    if json_handler:
        print(f"📄 JSON экспорт включен: каждый запрос → отдельный файл")
    
    stats.start()
    success_count = 0
    error_count = 0
    
    for idx, item in enumerate(pending, 1):
        row = item['row']
        request = item['request']
        project = item.get('project')
        model = item.get('model')
        chat_mode = item.get('chat_mode', CHAT_MODE_NEW)
        
        print(f"\n{'='*70}")
        print(f"📝 Запрос {idx}/{len(pending)} (строка Excel: {row})")
        print(f"💬 '{request[:70]}{'...' if len(request) > 70 else ''}'")
        if project:
            print(f"📁 Проект: {project}")
        if model:
            print(f"🤖 Модель: {model}")
        if chat_mode != CHAT_MODE_NEW:
            print(f"💭 Режим чата: {chat_mode}")
        print(f"{'='*70}")
        
        if logger:
            logger.request_start(row, request)
            if project:
                logger.info(f"[ROW {row}] Проект: {project}")
            if model:
                logger.info(f"[ROW {row}] Модель: {model}")
        
        excel_handler.update_status(row, STATUS_IN_PROGRESS)
        
        request_start_time = time.time()
        
        use_new_chat = (chat_mode == CHAT_MODE_NEW)
        
        success, response, error_type, error_message, attempts = retry_handler.execute_with_retry(
            chatgpt_handler.send_request,
            request,
            use_new_chat=use_new_chat,
            project=project,
            model=model,
            logger=logger,
            row=row
        )
        
        request_duration = time.time() - request_start_time
        
        if success:
            excel_handler.update_status(row, STATUS_SUCCESS, response=response)
            success_count += 1
            if logger:
                logger.request_success(row, len(response))
            stats.add_request(row, True, request_duration, attempts)
            
            # Сохраняем в отдельный JSON файл
            if json_handler:
                json_handler.save_request(
                    row=row,
                    request=request,
                    response=response,
                    status=STATUS_SUCCESS,
                    project=project,
                    model=model,
                    attempts=attempts,
                    duration=request_duration
                )
            
            print(f"  🎉 Запрос выполнен успешно!")
            print(f"  📄 Начало ответа: {response[:150]}...")
            print(f"  ⏱️  Время выполнения: {stats.format_duration(request_duration)}")
            print(f"  🔄 Попыток: {attempts}")
        else:
            status = STATUS_ERROR
            if error_type == 'rate_limit':
                status = STATUS_RATE_LIMIT
            elif error_type == 'network':
                status = STATUS_NETWORK_ERROR
            elif error_type == 'timeout':
                status = STATUS_TIMEOUT
            
            excel_handler.update_status(row, status, error_message=error_message)
            error_count += 1
            if logger:
                logger.request_error(row, error_type, error_message)
            stats.add_request(row, False, request_duration, attempts, error_type)
            
            # Сохраняем ошибку в JSON
            if json_handler:
                json_handler.save_request(
                    row=row,
                    request=request,
                    response=None,
                    status=status,
                    error_message=error_message,
                    project=project,
                    model=model,
                    attempts=attempts,
                    duration=request_duration
                )
            
            print(f"  ⚠️ Ошибка: {error_message}")
            print(f"  🔄 Попыток: {attempts}")
            
            if error_type in ['rate_limit', 'auth']:
                choice = input("\n  Продолжить обработку остальных запросов (y/n)? >>> ").lower()
                if choice != 'y':
                    if logger:
                        logger.warning("Обработка остановлена пользователем")
                    print("  ⏸️  Обработка остановлена")
                    break
        
        stats.print_progress(idx, len(pending))
        
        if idx < len(pending):
            # ✨ HUMANIZATION: Случайная задержка
            delay = chatgpt_handler.human.get_request_delay()
            print(f"\n  ⏸️  Пауза {delay:.1f} сек (как человек)...")
            time.sleep(delay)
            
            # ✨ HUMANIZATION: Мини-перерыв если нужно
            chatgpt_handler.schedule.take_break_if_needed()
    
    stats.end()
    
    print("\n" + "=" * 70)
    print("📋 ШАГ 3: ОБРАБОТКА ЗАВЕРШЕНА!")
    print("=" * 70)
    print(f"✅ Выполнено успешно: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    print(f"📂 Результаты Excel: {os.path.abspath(EXCEL_FILE)}")
    print(f"📂 Результаты JSON: {os.path.abspath(JSON_OUTPUT_DIR)}/")
    if logger:
        print(f"📋 Лог файл: {logger.get_log_file()}")
    print("=" * 70)
    
    if logger:
        logger.info(f"Обработка завершена. Успешно: {success_count}, Ошибок: {error_count}")
    
    stats.print_summary()

def process_requests_single_chat(excel_handler, chatgpt_handler, logger, retry_handler, stats):
    """Обрабатывает все запросы в ОДНОМ чате (альтернативный режим)"""
    pending = excel_handler.get_pending_requests()
    
    if not pending:
        print("\n✅ Все запросы уже выполнены!")
        if logger:
            logger.info("Нет невыполненных запросов")
        return
    
    print("\n" + "=" * 70)
    print("📋 ШАГ 2: АВТОМАТИЧЕСКАЯ ОБРАБОТКА")
    print("=" * 70)
    print(f"🔗 Режим: ВСЕ ЗАПРОСЫ В ОДНОМ ЧАТЕ")
    print(f"⚠️  Внимание: контекст предыдущих запросов будет влиять на ответы!")
    print(f"🔄 Начинаю обрабатывать {len(pending)} запросов...")
    if logger:
        logger.info(f"Начало обработки {len(pending)} запросов (режим: один чат)")
    print("=" * 70)
    
    json_handler = JSONHandlerV2(JSON_OUTPUT_DIR) if JSON_ENABLED else None
    
    first_item = pending[0]
    if first_item.get('project') or first_item.get('model'):
        print(f"\n⚙️  Настраиваю контекст для всей серии...")
        if first_item.get('project'):
            print(f"   📁 Проект: {first_item['project']}")
        if first_item.get('model'):
            print(f"   🤖 Модель: {first_item['model']}")
        
        chatgpt_handler.project_manager.setup_context(
            project=first_item.get('project'),
            model=first_item.get('model')
        )
    
    print(f"\n🆕 Создаю один общий чат для всех запросов...")
    chatgpt_handler.create_new_chat()
    
    stats.start()
    success_count = 0
    error_count = 0
    
    for idx, item in enumerate(pending, 1):
        row = item['row']
        request = item['request']
        
        print(f"\n{'='*70}")
        print(f"📝 Запрос {idx}/{len(pending)} (строка Excel: {row})")
        print(f"💬 '{request[:70]}{'...' if len(request) > 70 else ''}'")
        print(f"{'='*70}")
        
        if logger:
            logger.request_start(row, request)
        
        excel_handler.update_status(row, STATUS_IN_PROGRESS)
        
        request_start_time = time.time()
        
        success, response, error_type, error_message, attempts = retry_handler.execute_with_retry(
            chatgpt_handler.send_request,
            request,
            use_new_chat=False,
            project=None,
            model=None,
            logger=logger,
            row=row
        )
        
        request_duration = time.time() - request_start_time
        
        if success:
            excel_handler.update_status(row, STATUS_SUCCESS, response=response)
            success_count += 1
            if logger:
                logger.request_success(row, len(response))
            stats.add_request(row, True, request_duration, attempts)
            
            if json_handler:
                json_handler.save_request(
                    row=row,
                    request=request,
                    response=response,
                    status=STATUS_SUCCESS,
                    project=first_item.get('project'),
                    model=first_item.get('model'),
                    attempts=attempts,
                    duration=request_duration
                )
            
            print(f"  🎉 Запрос выполнен успешно!")
            print(f"  📄 Начало ответа: {response[:150]}...")
            print(f"  ⏱️  Время выполнения: {stats.format_duration(request_duration)}")
            print(f"  🔄 Попыток: {attempts}")
        else:
            status = STATUS_ERROR
            if error_type == 'rate_limit':
                status = STATUS_RATE_LIMIT
            elif error_type == 'network':
                status = STATUS_NETWORK_ERROR
            elif error_type == 'timeout':
                status = STATUS_TIMEOUT
            
            excel_handler.update_status(row, status, error_message=error_message)
            error_count += 1
            if logger:
                logger.request_error(row, error_type, error_message)
            stats.add_request(row, False, request_duration, attempts, error_type)
            
            if json_handler:
                json_handler.save_request(
                    row=row,
                    request=request,
                    response=None,
                    status=status,
                    error_message=error_message,
                    project=first_item.get('project'),
                    model=first_item.get('model'),
                    attempts=attempts,
                    duration=request_duration
                )
            
            print(f"  ⚠️ Ошибка: {error_message}")
            print(f"  🔄 Попыток: {attempts}")
            
            if error_type in ['rate_limit', 'auth']:
                choice = input("\n  Продолжить обработку (y/n)? >>> ").lower()
                if choice != 'y':
                    if logger:
                        logger.warning("Обработка остановлена пользователем")
                    print("  ⏸️  Обработка остановлена")
                    break
        
        stats.print_progress(idx, len(pending))
        
        if idx < len(pending):
            print(f"\n  ⏸️  Пауза {DELAY_BETWEEN_REQUESTS} сек...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    stats.end()
    
    print("\n" + "=" * 70)
    print("📋 ШАГ 3: ОБРАБОТКА ЗАВЕРШЕНА!")
    print("=" * 70)
    print(f"✅ Выполнено успешно: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    print(f"📂 Результаты Excel: {os.path.abspath(EXCEL_FILE)}")
    print(f"📂 Результаты JSON: {os.path.abspath(JSON_OUTPUT_DIR)}/")
    if logger:
        print(f"📋 Лог файл: {logger.get_log_file()}")
    print("=" * 70)
    
    if logger:
        logger.info(f"Обработка завершена. Успешно: {success_count}, Ошибок: {error_count}")
    
    stats.print_summary()

def manual_close():
    """Ручное закрытие"""
    print("\n" + "=" * 70)
    print("📋 ШАГ 4: ЗАВЕРШЕНИЕ")
    print("=" * 70)
    print("✋ Браузер останется открытым")
    print("   • Можете проверить результаты")
    print("   • Можете посмотреть историю чатов")
    print("   • Можете вручную отправить еще запросы")
    print("   • Можете проверить что запросы попали в нужные проекты")
    print("\n👉 Нажмите ENTER для закрытия браузера")
    print("=" * 70)
    
    input("\n⏸️  >>> ")

def main():
    """Главная функция"""
    print_header()
    
    logger = Logger(LOG_DIR) if LOG_ENABLED else None
    validator = Validator()
    backup_manager = BackupManager() if BACKUP_ENABLED else None
    excel_handler = ExcelHandler()
    browser_manager = BrowserManager()
    retry_handler = RetryHandler(
        max_attempts=MAX_RETRY_ATTEMPTS,
        base_delay=RETRY_BASE_DELAY,
        exponential_backoff=RETRY_EXPONENTIAL_BACKOFF
    )
    stats = Statistics()
    
    try:
        if not validator.validate_all():
            if logger:
                logger.error("Валидация не пройдена")
            input("\n❌ Исправьте ошибки и запустите снова. Нажмите ENTER...")
            return
        
        if logger:
            logger.info("Валидация пройдена успешно")
        
        if backup_manager:
            print("\n💾 Создаю резервную копию Excel...")
            backup_path = backup_manager.create_backup(EXCEL_FILE)
            if backup_path and logger:
                logger.info(f"Создан backup: {backup_path}")
            
            backup_manager.cleanup_old_backups(KEEP_LAST_BACKUPS)
        
        if not excel_handler.load():
            if logger:
                logger.error("Не удалось загрузить Excel")
            input("\nНажмите ENTER для выхода...")
            return
        
        if logger:
            logger.info(f"Excel файл загружен: {EXCEL_FILE}")
        
        excel_stats = excel_handler.get_statistics()
        print_statistics(excel_stats)
        
        pending = excel_handler.get_pending_requests()
        uses_projects = any(item.get('project') for item in pending)
        uses_models = any(item.get('model') for item in pending)
        
        if uses_projects:
            print(f"   📁 Обнаружены запросы с проектами")
        if uses_models:
            print(f"   🤖 Обнаружены запросы с выбором модели")
        
        print("-" * 70)
        
        if not browser_manager.start():
            if logger:
                logger.error("Не удалось запустить браузер")
            input("\nНажмите ENTER для выхода...")
            return
        
        if logger:
            logger.info("Браузер запущен")
        
        if not browser_manager.open_chatgpt():
            if logger:
                logger.error("Не удалось открыть ChatGPT")
            input("\nНажмите ENTER для выхода...")
            return
        
        if logger:
            logger.info("ChatGPT открыт")
        
        manual_login()
        if logger:
            logger.info("Авторизация выполнена")
        
        driver = browser_manager.get_driver()
        chatgpt_handler = ChatGPTHandler(driver, HUMANIZATION_CONFIG)
        
        process_requests(excel_handler, chatgpt_handler, logger, retry_handler, stats)
        
        manual_close()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана (Ctrl+C)")
        print("💾 Весь прогресс сохранен")
        if logger:
            logger.warning("Программа прервана пользователем")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if logger:
            logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите ENTER...")
        
    finally:
        browser_manager.close()
        if logger:
            logger.close()
        
        print("\n" + "=" * 70)
        print("✅ Программа завершена")
        print("=" * 70)
        input("\nНажмите ENTER для выхода...")

if __name__ == "__main__":
    main()