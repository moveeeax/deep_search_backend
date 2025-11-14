import os
import sys

# Add the current directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set a dummy API key for testing (this won't actually work but will allow the agent to initialize)
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"

from backend.agent import WebAgent

def test_routing():
    """Test the routing functionality"""
    print("Testing routing functionality...")
    
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
    
    for query, expected_mode in test_cases:
        print(f"\nQuery: {query}")
        print(f"Expected mode: {expected_mode}")
        
        try:
            selected_mode = agent.route_query(query)
            print(f"Selected mode: {selected_mode}")
            print(f"Result: {'✓ PASS' if selected_mode == expected_mode else '✗ FAIL'}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_routing()