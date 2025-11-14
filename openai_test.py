#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к OpenAI API
"""

import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_openai_connection():
    """Тестирование подключения к OpenAI API"""
    print("Тестирование подключения к OpenAI API...")
    
    try:
        from openai import OpenAI
        
        # Получение параметров из переменных окружения
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("NANO_MODEL", "gpt-3.5-turbo")
        
        print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
        print(f"Base URL: {base_url}")
        print(f"Model: {model}")
        
        # Создание клиента
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Тестовый запрос
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Вы полезный помощник."},
                {"role": "user", "content": "Привет, как дела?"}
            ],
            max_tokens=50
        )
        
        print("✅ Подключение к OpenAI API успешно")
        print(f"Ответ: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к OpenAI API: {e}")
        return False

def test_langchain_openai():
    """Тестирование LangChain OpenAI"""
    print("\nТестирование LangChain OpenAI...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # Получение параметров из переменных окружения
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("NANO_MODEL", "gpt-3.5-turbo")
        
        print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
        print(f"Base URL: {base_url}")
        print(f"Model: {model}")
        
        # Создание модели
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=50,
            api_key=api_key,
            base_url=base_url
        )
        
        # Тестовый запрос
        response = llm.invoke("Привет, как дела?")
        
        print("✅ LangChain OpenAI работает успешно")
        print(f"Ответ: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка LangChain OpenAI: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование подключения к OpenAI")
    print("=" * 40)
    
    # Тестирование подключения к OpenAI API
    openai_ok = test_openai_connection()
    
    # Тестирование LangChain OpenAI
    langchain_ok = test_langchain_openai()
    
    print("\n" + "=" * 40)
    if openai_ok and langchain_ok:
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("❌ Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())