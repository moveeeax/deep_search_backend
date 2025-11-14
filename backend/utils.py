import os
import json
from typing import Callable, Dict, Any, List
from functools import wraps
from requests.exceptions import RequestException

def tavily_tool_wrapper(func: Callable, name: str) -> Callable:
    """
    Обертка для инструментов Tavily с обработкой ошибок
    
    Args:
        func: Функция инструмента Tavily
        name: Имя инструмента
        
    Returns:
        Обернутая функция с обработкой ошибок
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Вызов оригинальной функции
            result = func(*args, **kwargs)
            
            # Преобразование результата в JSON-сериализуемый формат
            if hasattr(result, '__dict__'):
                return json.dumps(result.__dict__, default=str, ensure_ascii=False)
            elif isinstance(result, (dict, list, str, int, float, bool)) or result is None:
                return result
            else:
                return str(result)
                
        except json.JSONDecodeError:
            # Если не удалось сериализовать в JSON, возвращаем строковое представление
            return str(result) if 'result' in locals() else "Ошибка обработки результата"
        except RequestException:
            # Передаем ошибки запросов дальше
            raise
        except Exception as e:
            # Логируем неожиданные ошибки и возвращаем информативное сообщение
            print(f"Неожиданная ошибка в инструменте {name}: {str(e)}")
            return f"Ошибка выполнения инструмента {name}: {str(e)}"
    
    # Установка атрибутов для LangChain
    wrapper.name = name
    wrapper.description = f"Инструмент {name} для веб-поиска"
    wrapper.args_schema = None  # Можно добавить Pydantic модель для валидации аргументов
    
    return wrapper

def aggregate_and_summarize(query: str, contents: List[str], tavily_client) -> str:
    """
    Агрегация и суммирование контента с помощью Tavily
    
    Args:
        query: Исходный запрос пользователя
        contents: Список контента для суммирования
        tavily_client: Клиент Tavily для выполнения запросов
        
    Returns:
        Суммированный ответ
    """
    try:
        # Объединяем контент в один текст
        combined_content = "\n\n".join(contents[:5])  # Ограничиваем 5 источниками
        
        # Создаем промпт для суммирования
        summarize_prompt = f"""
        Пожалуйста, предоставьте краткое и точное резюме следующего контента в ответ на вопрос: "{query}"
        
        Контент:
        {combined_content}
        
        Требования к ответу:
        1. Ответ должен быть на русском языке
        2. Ответ должен быть структурированным и легко читаемым
        3. Включите ключевые моменты из контента
        4. Укажите противоречия, если они есть между источниками
        5. Добавьте оценку достоверности информации
        """
        
        # Используем Tavily для суммирования
        response = tavily_client.search(
            summarize_prompt,
            search_depth="advanced",
            max_results=1
        )
        
        # Извлекаем ответ
        if response and 'results' in response and len(response['results']) > 0:
            return response['results'][0].get('content', 'Не удалось создать резюме')
        else:
            # Альтернативный подход - возвращаем объединенный контент
            return combined_content[:2000] + "..." if len(combined_content) > 2000 else combined_content
            
    except Exception as e:
        print(f"Ошибка агрегации и суммирования: {str(e)}")
        # В случае ошибки возвращаем первый контент
        return contents[0][:1000] + "..." if contents else "Не удалось создать резюме"

# Экспортируем функции
__all__ = ['tavily_tool_wrapper', 'aggregate_and_summarize']
