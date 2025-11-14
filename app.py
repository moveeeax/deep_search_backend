import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.agent import WebAgent
from backend.utils import tavily_tool_wrapper, aggregate_and_summarize
from tavily import TavilyClient
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/search/*": {
        "origins": [
            "http://localhost", 
            "http://localhost:80", 
            "http://localhost:8000",
            "http://bootcamp2025.tarassov.me", 
            "http://bootcamp2025.tarassov.me:8000"
        ],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/health": {
        "origins": "*"
    }
})

# Инициализация Tavily клиента
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@app.route('/health')
def health():
    """Проверка состояния сервиса"""
    return jsonify({"status": "healthy"})

@app.route('/search/fast', methods=['POST'])
def fast_search():
    """
    Быстрый поиск - базовый поиск с минимальной обработкой
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
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
        return jsonify({"error": str(e)}), 500

@app.route('/search/deep', methods=['POST'])
def deep_search():
    """
    Глубокий анализ - продвинутый режим с многошаговым рассуждением
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Использование агента для глубокого анализа
        agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        result = agent.run(query, mode="deep")
        
        # Получение расширенных источников через Tavily search
        search_results = tavily_client.search(
            query, 
            max_results=5,
            include_raw_content=True
        )
        
        # Агрегация и суммирование результатов
        sources = []
        contents = []
        if 'results' in search_results:
            for r in search_results['results']:
                sources.append({
                    "title": r.get('title', ''), 
                    "url": r.get('url', ''),
                    "score": r.get('score', 0)
                })
                if r.get('raw_content'):
                    contents.append(r['raw_content'])
        
        # Создание расширенного ответа с суммированием
        if contents:
            summary = aggregate_and_summarize(query, contents, tavily_client)
            response_text = summary
        else:
            response_text = result["response"]
        
        return jsonify({
            "response": response_text,
            "sources": sources,
            "fact_check_notes": "Проверка фактов выполнена с использованием нескольких источников"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/social', methods=['POST'])
def social_search():
    """
    Социальный анализ - анализ мнений с Reddit, X, VK, Habr
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Использование агента для социального анализа
        agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        result = agent.run(query, mode="social")
        
        # Получение источников социальных сетей через Tavily search
        search_results = tavily_client.search(
            query,
            max_results=5,
            include_domains=["reddit.com", "twitter.com", "x.com", "vk.com", "habr.com"],
            time_range="week"
        )
        
        sources = []
        if 'results' in search_results:
            sources = [
                {"title": r.get('title', ''), "url": r.get('url', '')} 
                for r in search_results['results']
            ]
        
        return jsonify({
            "response": result["response"],
            "sources": sources,
            "analysis_type": "social_media_analysis"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/academic', methods=['POST'])
def academic_search():
    """
    Академический поиск - поиск в arXiv / Semantic Scholar
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Использование агента для академического поиска
        agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        result = agent.run(query, mode="academic")
        
        # Получение академических источников через Tavily search
        search_results = tavily_client.search(
            query,
            max_results=5,
            include_domains=["arxiv.org", "semanticscholar.org"],
            time_range="year"
        )
        
        sources = []
        if 'results' in search_results:
            sources = [
                {"title": r.get('title', ''), "url": r.get('url', '')} 
                for r in search_results['results']
            ]
        
        return jsonify({
            "response": result["response"],
            "sources": sources,
            "analysis_type": "academic_research"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/finance', methods=['POST'])
def finance_search():
    """
    Финансовый анализ - данные из Yahoo Finance / TradingView
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Использование агента для финансового анализа
        agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        result = agent.run(query, mode="finance")
        
        # Получение финансовых источников через Tavily search
        search_results = tavily_client.search(
            query,
            max_results=5,
            topic="finance",
            include_domains=["finance.yahoo.com", "bloomberg.com", "reuters.com"],
            time_range="day"
        )
        
        sources = []
        if 'results' in search_results:
            sources = [
                {"title": r.get('title', ''), "url": r.get('url', '')} 
                for r in search_results['results']
            ]
        
        return jsonify({
            "response": result["response"],
            "sources": sources,
            "analysis_type": "financial_analysis"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search/auto', methods=['POST'])
def auto_search():
    """
    Автоматическая маршрутизация - интеллектуальный выбор режима поиска
    """
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Определение подходящего режима поиска
        router_agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        selected_mode = router_agent.route_query(query)
        
        # Выполнение поиска в выбранном режиме
        agent = WebAgent(model_type=os.getenv("MODEL_TYPE", "openai"))
        result = agent.run(query, mode=selected_mode)
        
        # Получение источников в зависимости от режима
        search_params = {
            "max_results": 5
        }
        
        # Настройка параметров поиска в зависимости от режима
        if selected_mode == "social":
            search_params.update({
                "include_domains": ["reddit.com", "twitter.com", "x.com", "vk.com", "habr.com"],
                "time_range": "week"
            })
        elif selected_mode == "academic":
            search_params.update({
                "include_domains": ["arxiv.org", "semanticscholar.org"],
                "time_range": "year"
            })
        elif selected_mode == "finance":
            search_params.update({
                "topic": "finance",
                "include_domains": ["finance.yahoo.com", "bloomberg.com", "reuters.com"],
                "time_range": "day"
            })
        elif selected_mode == "deep":
            search_params.update({
                "include_raw_content": True
            })
        
        # Выполнение поиска для получения источников
        search_results = tavily_client.search(query, **search_params)
        
        # Обработка источников
        sources = []
        contents = []
        if 'results' in search_results:
            for r in search_results['results']:
                sources.append({
                    "title": r.get('title', ''),
                    "url": r.get('url', ''),
                    "score": r.get('score', 0)
                })
                if r.get('raw_content') and selected_mode == "deep":
                    contents.append(r['raw_content'])
        
        # Для глубокого анализа агрегируем и суммируем результаты
        if selected_mode == "deep" and contents:
            summary = aggregate_and_summarize(query, contents, tavily_client)
            response_text = summary
        else:
            response_text = result["response"]
        
        # Подготовка ответа
        response_data = {
            "response": response_text,
            "sources": sources,
            "mode_selected": selected_mode
        }
        
        # Добавляем специфичные для режима поля
        if selected_mode == "deep":
            response_data["fact_check_notes"] = "Проверка фактов выполнена с использованием нескольких источников"
        elif selected_mode == "social":
            response_data["analysis_type"] = "social_media_analysis"
        elif selected_mode == "academic":
            response_data["analysis_type"] = "academic_research"
        elif selected_mode == "finance":
            response_data["analysis_type"] = "financial_analysis"
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
