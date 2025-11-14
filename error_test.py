#!/usr/bin/env python3
"""
Скрипт для тестирования и отладки ошибок Flask приложения
"""

import os
import sys
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_fast_search_endpoint():
    """Тестирование endpoint /search/fast"""
    print("Тестирование endpoint /search/fast...")
    
    try:
        # Импортируем необходимые компоненты
        from backend.agent import WebAgent
        from tavily import TavilyClient
        
        # Создаем тестовое приложение Flask
        app = Flask(__name__)
        CORS(app)
        
        # Инициализация Tavily клиента
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        @app.route('/search/fast', methods=['POST'])
        def fast_search():
            """
            Быстрый поиск - базовый поиск с минимальной обработкой
            """
            try:
                data = request.get_json()
                query = data.get('query')
                
                if not query:
                    return jsonify({"error": "Query is required"}), 400
                
                # Использование агента для быстрого поиска
                agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
                result = agent.run(query, mode="fast")
                
                # Получение источников через Tavily search
                search_results = tavily_client.search(query, max_results=3)
                sources = []
                if 'results' in search_results:
                    sources = [
                        {"title": r.get('title', ''), "url": r.get('url', '')} 
                        for r in search_results['results']
                    ]
                
                return jsonify({
                    "response": result["response"],
                    "sources": sources
                })
            except Exception as e:
                print(f"Ошибка в fast_search: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
        
        # Тестовый запрос
        with app.test_client() as client:
            response = client.post('/search/fast', 
                                 json={'query': 'Что такое искусственный интеллект?'})
            print(f"Статус ответа: {response.status_code}")
            print(f"Тело ответа: {response.get_json()}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования endpoint: {e}")
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование ошибок Flask приложения")
    print("=" * 50)
    
    # Тестирование endpoint
    endpoint_ok = test_fast_search_endpoint()
    
    print("\n" + "=" * 50)
    if endpoint_ok:
        print("🎉 Тест endpoint пройден успешно!")
        return 0
    else:
        print("❌ Тест endpoint не пройден")
        return 1

if __name__ == "__main__":
    sys.exit(main())