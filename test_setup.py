#!/usr/bin/env python3
"""
Скрипт для тестирования настройки Research Pro Mode
"""

import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_environment_variables():
    """Тестирование переменных окружения"""
    print("Тестирование переменных окружения...")
    
    required_vars = [
        "TAVILY_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ Отсутствует: {var}")
        else:
            # Показываем только начало и конец ключа для безопасности
            if "KEY" in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n⚠️  Отсутствуют {len(missing_vars)} обязательные переменные окружения")
        return False
    else:
        print("\n✅ Все обязательные переменные окружения присутствуют")
        return True

def test_imports():
    """Тестирование импортов"""
    print("\nТестирование импортов...")
    
    try:
        from backend.agent import WebAgent
        print("✅ WebAgent импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта WebAgent: {e}")
        return False
    
    try:
        from backend.prompts import SIMPLE_PROMPT, REASONING_PROMPT
        print("✅ Промпты импортированы успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта промптов: {e}")
        return False
    
    try:
        from tavily import TavilyClient
        print("✅ TavilyClient импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта TavilyClient: {e}")
        return False
    
    return True

def test_tavily_connection():
    """Тестирование подключения к Tavily"""
    print("\nТестирование подключения к Tavily...")
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Простой тестовый запрос
        response = client.search("Что такое искусственный интеллект?", max_results=1)
        
        if response and 'results' in response:
            print("✅ Подключение к Tavily успешно")
            print(f"✅ Получено {len(response['results'])} результатов")
            return True
        else:
            print("❌ Неожиданный формат ответа от Tavily")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Tavily: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование настройки Research Pro Mode")
    print("=" * 50)
    
    # Тестирование переменных окружения
    env_ok = test_environment_variables()
    
    # Тестирование импортов
    imports_ok = test_imports()
    
    # Тестирование подключения к Tavily
    tavily_ok = test_tavily_connection()
    
    print("\n" + "=" * 50)
    if env_ok and imports_ok and tavily_ok:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ Готово к запуску Research Pro Mode")
        return 0
    else:
        print("❌ Некоторые тесты не пройдены")
        print("Пожалуйста, проверьте конфигурацию и попробуйте снова")
        return 1

if __name__ == "__main__":
    sys.exit(main())