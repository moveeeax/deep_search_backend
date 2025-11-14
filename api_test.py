#!/usr/bin/env python3
"""
Скрипт для тестирования всех API endpoint'ов приложения
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_endpoint(endpoint, query, expected_status=200):
    """Тестирование конкретного endpoint'а"""
    print(f"Тестирование endpoint {endpoint}...")
    
    try:
        # Подготовка данных запроса
        data = {"query": query}
        
        # Отправка POST запроса
        response = requests.post(
            f"http://localhost:8000{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Проверка статуса ответа
        if response.status_code == expected_status:
            print(f"✅ Endpoint {endpoint} вернул статус {response.status_code}")
            
            # Попытка парсинга JSON
            try:
                result = response.json()
                print(f"   Ответ содержит {len(result.get('sources', []))} источников")
                if 'response' in result:
                    # Показываем первые 200 символов ответа
                    preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                    print(f"   Превью ответа: {preview}")
                return True
            except json.JSONDecodeError:
                print(f"   ❌ Не удалось распарсить JSON ответ")
                return False
        else:
            print(f"❌ Endpoint {endpoint} вернул статус {response.status_code}, ожидался {expected_status}")
            print(f"   Тело ответа: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удалось подключиться к серверу. Убедитесь, что приложение запущено.")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании endpoint {endpoint}: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование API endpoint'ов приложения")
    print("=" * 50)
    
    # Тестовые запросы для каждого режима
    test_cases = [
        ("/search/fast", "Что такое искусственный интеллект?", "Быстрый поиск"),
        ("/search/deep", "Как работают нейронные сети?", "Глубокий анализ"),
        ("/search/social", "Мнения пользователей о ChatGPT", "Социальный анализ"),
        ("/search/academic", "Исследования по машинному обучению 2024", "Академический поиск"),
        ("/search/finance", "Курс доллара к рублю сегодня", "Финансовый анализ")
    ]
    
    results = []
    
    # Тестирование всех endpoint'ов
    for endpoint, query, description in test_cases:
        print(f"\n📝 {description}: {query}")
        success = test_endpoint(endpoint, query)
        results.append((description, success))
    
    # Вывод результатов
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    print("=" * 50)
    
    passed = 0
    for description, success in results:
        status = "✅ Пройден" if success else "❌ Провален"
        print(f"{status}: {description}")
        if success:
            passed += 1
    
    print(f"\n🏁 Всего пройдено: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())