import requests
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# URL API (по умолчанию localhost:8000)
API_URL = os.getenv("API_URL", "http://localhost:8000")

def test_auto_routing():
    """Тестирование функции авто-маршрутизации"""
    
    # Тестовые запросы для разных режимов
    test_queries = [
        {
            "query": "Какова столица Франции?",
            "expected_mode": "fast",
            "description": "Простой фактический вопрос"
        },
        {
            "query": "Проанализируйте влияние искусственного интеллекта на мировую экономику",
            "expected_mode": "deep",
            "description": "Сложный аналитический вопрос"
        },
        {
            "query": "Какие новости в сообществе разработчиков Python на Reddit?",
            "expected_mode": "social",
            "description": "Запрос на анализ социальных сетей"
        },
        {
            "query": "Найдите последние исследования по трансформерам в области NLP",
            "expected_mode": "academic",
            "description": "Академический поиск"
        },
        {
            "query": "Какова текущая цена акций Apple?",
            "expected_mode": "finance",
            "description": "Финансовый вопрос"
        }
    ]
    
    print("Тестирование авто-маршрутизации...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\nТест {i}: {test_case['description']}")
        print(f"Запрос: {test_case['query']}")
        
        try:
            # Отправка запроса на авто-маршрутизацию
            response = requests.post(
                f"{API_URL}/search/auto",
                json={"query": test_case["query"]},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                selected_mode = result.get("mode_selected", "unknown")
                print(f"Выбранный режим: {selected_mode}")
                print(f"Ожидаемый режим: {test_case['expected_mode']}")
                print(f"Статус: {'✓ УСПЕХ' if selected_mode == test_case['expected_mode'] else '✗ ОШИБКА'}")
                
                # Показать начало ответа (первые 100 символов)
                response_text = result.get("response", "")
                print(f"Ответ (первые 100 символов): {response_text[:100]}...")
                
                # Показать количество источников
                sources = result.get("sources", [])
                print(f"Источников найдено: {len(sources)}")
            else:
                print(f"Ошибка HTTP: {response.status_code}")
                print(f"Сообщение: {response.text}")
                
        except Exception as e:
            print(f"Ошибка при выполнении теста: {str(e)}")
        
        print("-" * 50)
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    test_auto_routing()