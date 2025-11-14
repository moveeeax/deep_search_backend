#!/usr/bin/env python3
"""
Минимальный тест Flask приложения
"""

import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_flask_imports():
    """Тестирование импортов Flask"""
    print("Тестирование импортов Flask...")
    
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        print("✅ Flask импорты успешны")
        return True
    except Exception as e:
        print(f"❌ Ошибка импортов Flask: {e}")
        return False

def test_app_creation():
    """Тестирование создания приложения"""
    print("\nТестирование создания приложения...")
    
    try:
        from flask import Flask, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/test')
        def test():
            return jsonify({"status": "ok"})
        
        print("✅ Приложение создано успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        return False

def test_backend_imports():
    """Тестирование импортов бэкенда"""
    print("\nТестирование импортов бэкенда...")
    
    try:
        # Попробуем импортировать компоненты по одному
        from backend import agent
        print("✅ backend.agent импортирован")
        
        from backend import prompts
        print("✅ backend.prompts импортирован")
        
        from backend import utils
        print("✅ backend.utils импортирован")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка импортов бэкенда: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование Flask приложения")
    print("=" * 40)
    
    # Тестирование импортов Flask
    flask_imports_ok = test_flask_imports()
    
    # Тестирование создания приложения
    app_creation_ok = test_app_creation()
    
    # Тестирование импортов бэкенда
    backend_imports_ok = test_backend_imports()
    
    print("\n" + "=" * 40)
    if flask_imports_ok and app_creation_ok and backend_imports_ok:
        print("🎉 Все тесты Flask пройдены успешно!")
        return 0
    else:
        print("❌ Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())