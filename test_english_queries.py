#!/usr/bin/env python3
"""
Test script to verify English query routing functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.agent import WebAgent

def test_english_routing():
    """Test English query routing"""
    agent = WebAgent()
    
    # Test cases with English queries
    test_cases = [
        # Fast queries
        ("What is the capital of France?", "fast"),
        ("Who is the president of USA?", "fast"),
        ("How tall is Mount Everest?", "fast"),
        
        # Deep analysis queries
        ("Analyze the impact of artificial intelligence on society", "deep"),
        ("Compare different approaches to machine learning", "deep"),
        ("What are the pros and cons of renewable energy?", "deep"),  # Balanced deep analysis
        
        # Social queries
        ("What are people saying about Python on Reddit?", "social"),
        ("Trending topics on Twitter about climate change", "social"),
        ("Latest posts on LinkedIn about remote work", "social"),
        
        # Academic queries
        ("Find recent research papers on transformers in NLP", "academic"),
        ("Is there a published study on quantum computing?", "academic"),
        ("Latest publications in arxiv on computer vision", "academic"),
        ("Explain quantum computing in simple terms", "academic"),  # Contains academic terms
        ("Provide a detailed analysis of climate change effects", "academic"),  # Climate change is academic
        ("How does photosynthesis work?", "academic"),  # Scientific concept
        
        # Finance queries
        ("What is the current price of Apple stock?", "finance"),
        ("Is investing in cryptocurrency profitable now?", "finance"),
        ("Exchange rate of USD to EUR today", "finance"),
    ]
    
    print("Testing English query routing functionality...")
    print("=" * 50)
    
    passed = 0
    total = len(test_cases)
    
    for query, expected_mode in test_cases:
        predicted_mode = agent.route_query(query)
        status = "✓ PASS" if predicted_mode == expected_mode else "✗ FAIL"
        print(f"  {query:<50} -> {predicted_mode:<8} (expected: {expected_mode:<8}) {status}")
        
        if predicted_mode == expected_mode:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"=== SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! The routing logic is working correctly with English queries.")
    else:
        print(f"\n❌ {total-passed} tests failed. Please review the routing logic.")

if __name__ == "__main__":
    test_english_routing()