import os
import sys

# Add the current directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set dummy API keys for testing
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"

# Mock the TavilyClient to avoid actual API calls
import tavily
tavily.TavilyClient = lambda api_key: None

# Mock LangChain classes
class MockChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass
    
    def bind_tools(self, tools):
        return self
        
    def invoke(self, messages):
        class MockResponse:
            def __init__(self):
                # For testing, we'll simulate different responses based on the query
                query = messages[0]["content"].split("Запрос пользователя:")[-1].strip()
                if "Reddit" in query:
                    self.content = "social"
                elif "исследования" in query or "трансформерам" in query:
                    self.content = "academic"
                elif "акций" in query or "Apple" in query:
                    self.content = "finance"
                elif "анализировать" in query or "влияние" in query:
                    self.content = "deep"
                else:
                    self.content = "fast"
        return MockResponse()

# Replace the actual imports with mocks
import langchain_openai
langchain_openai.ChatOpenAI = MockChatOpenAI

from backend.agent import WebAgent

def test_routing():
    """Test the routing functionality"""
    print("Testing improved routing functionality...")
    
    # Create an agent (using default openai)
    agent = WebAgent(model_type="openai")
    
    # Test queries for different modes
    test_cases = [
        ("Какова столица Франции?", "fast"),
        ("Проанализируйте влияние искусственного интеллекта на мировую экономику", "deep"),
        ("Какие новости в сообществе разработчиков Python на Reddit?", "social"),
        ("Найдите последние исследования по трансформерам в области NLP", "academic"),
        ("Какова текущая цена акций Apple?", "finance")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for query, expected_mode in test_cases:
        print(f"\nQuery: {query}")
        print(f"Expected mode: {expected_mode}")
        
        try:
            selected_mode = agent.route_query(query)
            print(f"Selected mode: {selected_mode}")
            result = "✓ PASS" if selected_mode == expected_mode else "✗ FAIL"
            print(f"Result: {result}")
            if selected_mode == expected_mode:
                passed += 1
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")

if __name__ == "__main__":
    test_routing()