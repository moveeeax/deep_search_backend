#!/usr/bin/env python3
"""
Скрипт для отладки компонентов Research Pro Mode
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def test_imports():
    """Тестирование импортов"""
    print("Тестирование импортов...")
    
    try:
        from backend.agent import WebAgent
        print("✅ WebAgent импортирован успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта WebAgent: {e}")
        traceback.print_exc()
        return False

def test_agent_initialization():
    """Тестирование инициализации агента"""
    print("\nТестирование инициализации агента...")
    
    try:
        from backend.agent import WebAgent
        agent = WebAgent(model_type="openai")
        print("✅ Агент инициализирован успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации агента: {e}")
        traceback.print_exc()
        return False

def test_prompts():
    """Тестирование промптов"""
    print("\nТестирование промптов...")
    
    try:
        from backend.prompts import (
            SIMPLE_PROMPT, 
            REASONING_PROMPT, 
            SOCIAL_PROMPT, 
            ACADEMIC_PROMPT, 
            FINANCE_PROMPT,
            SUMMARIZER_PROMPT
        )
        print("✅ Все промпты импортированы успешно")
        print(f"   SIMPLE_PROMPT длина: {len(SIMPLE_PROMPT)}")
        print(f"   REASONING_PROMPT длина: {len(REASONING_PROMPT)}")
        print(f"   SOCIAL_PROMPT длина: {len(SOCIAL_PROMPT)}")
        print(f"   ACADEMIC_PROMPT длина: {len(ACADEMIC_PROMPT)}")
        print(f"   FINANCE_PROMPT длина: {len(FINANCE_PROMPT)}")
        print(f"   SUMMARIZER_PROMPT длина: {len(SUMMARIZER_PROMPT)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта промптов: {e}")
        traceback.print_exc()
        return False

def test_utils():
    """Тестирование утилит"""
    print("\nТестирование утилит...")
    
    try:
        from backend.utils import tavily_tool_wrapper, aggregate_and_summarize
        print("✅ Утилиты импортированы успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта утилит: {e}")
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Отладка компонентов Research Pro Mode")
    print("=" * 50)
    
    # Тестирование импортов
    imports_ok = test_imports()
    
    # Тестирование инициализации агента
    agent_ok = test_agent_initialization()
    
    # Тестирование промптов
    prompts_ok = test_prompts()
    
    # Тестирование утилит
    utils_ok = test_utils()
    
    print("\n" + "=" * 50)
    if imports_ok and agent_ok and prompts_ok and utils_ok:
        print("🎉 Все компоненты работают корректно!")
        return 0
    else:
        print("❌ Некоторые компоненты не работают")
        return 1

if __name__ == "__main__":
    sys.exit(main())