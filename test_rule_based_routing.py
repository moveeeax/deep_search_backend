import os
import sys

# Add the current directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set dummy API keys for testing
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["ANTHROPIC_API_KEY"] = "test-key"

# Mock the TavilyClient to avoid actual API calls
import tavily
tavily.TavilyClient = lambda api_key: None

# Mock LangChain classes
class MockChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass
    
    def bind_tools(self, tools):
        return self

class MockChatAnthropic:
    def __init__(self, *args, **kwargs):
        pass
    
    def bind_tools(self, tools):
        return self

# Replace the actual imports with mocks
import langchain_openai
import langchain_anthropic
langchain_openai.ChatOpenAI = MockChatOpenAI
langchain_anthropic.ChatAnthropic = MockChatAnthropic

from backend.agent import WebAgent

def test_rule_based_routing():
    """Test the rule-based routing functionality"""
    print("Testing rule-based routing functionality...")
    print("=" * 50)
    
    # Create agents for both model types
    openai_agent = WebAgent(model_type="openai")
    anthropic_agent = WebAgent(model_type="anthropic")
    
    # Test queries for different modes
    test_cases = [
        ("Какова столица Франции?", "fast"),
        ("Расскажи мне о фотосинтезе", "fast"),
        ("Что такое 15% от 200?", "fast"),
        ("Проанализируйте влияние искусственного интеллекта на мировую экономику", "deep"),
        ("Сравните различные подходы к машинному обучению", "deep"),
        ("Объясните теорию относительности простыми словами", "deep"),
        ("Какие новости в сообществе разработчиков Python на Reddit?", "social"),
        ("Что обсуждают пользователи VK по поводу новой игры?", "social"),
        ("Тренды в_twitter_ по теме климата", "social"),
        ("Найдите последние исследования по трансформерам в области NLP", "academic"),
        ("Опубликована_ли научная работа о квантовых вычислениях в этом году?", "academic"),
        ("Актуальные публикации в arxiv по компьютерному зрению", "academic"),
        ("Какова текущая цена акций Apple?", "finance"),
        ("Инвестиции в криптовалюту - выгодно ли это сейчас?", "finance"),
        ("Курс доллара к рублю сегодня", "finance")
    ]
    
    print("Testing OpenAI agent:")
    passed_openai = 0
    total = len(test_cases)
    
    for query, expected_mode in test_cases:
        selected_mode = openai_agent.route_query(query)
        result = "✓ PASS" if selected_mode == expected_mode else "✗ FAIL"
        print(f"  {query[:50]:<50} -> {selected_mode:<8} (expected: {expected_mode:<8}) {result}")
        if selected_mode == expected_mode:
            passed_openai += 1
    
    print(f"\nOpenAI Agent Success Rate: {passed_openai}/{total} ({passed_openai/total*100:.1f}%)")
    
    print("\nTesting Anthropic agent:")
    passed_anthropic = 0
    
    for query, expected_mode in test_cases:
        selected_mode = anthropic_agent.route_query(query)
        result = "✓ PASS" if selected_mode == expected_mode else "✗ FAIL"
        print(f"  {query[:50]:<50} -> {selected_mode:<8} (expected: {expected_mode:<8}) {result}")
        if selected_mode == expected_mode:
            passed_anthropic += 1
    
    print(f"\nAnthropic Agent Success Rate: {passed_anthropic}/{total} ({passed_anthropic/total*100:.1f}%)")
    
    print(f"\n=== OVERALL RESULTS ===")
    avg_success = (passed_openai + passed_anthropic) / (total * 2)
    print(f"Average Success Rate: {avg_success*100:.1f}%")

if __name__ == "__main__":
    test_rule_based_routing()