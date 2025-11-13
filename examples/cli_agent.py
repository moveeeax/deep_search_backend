#!/usr/bin/env python3
import json
import requests
import sys
import uuid
import os
import argparse
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_ENDPOINT = "http://localhost:8080/stream_agent"

def get_user_input() -> str:
    """Get input from user."""
    try:
        return input("\n> ").strip()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)

def send_query(
    query: str, 
    endpoint: str = DEFAULT_ENDPOINT, 
    thread_id: Optional[str] = None,
    agent_type: str = "deep"
) -> None:
    """
    Send query to the agent endpoint and stream the response.
    
    Args:
        query: User's question
        endpoint: API endpoint URL
        thread_id: Thread ID for conversation history
        agent_type: Type of agent ("fast" or "deep")
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TAVILY_API_KEY')}"
    }
    
    payload = {
        "input": query,
        "thread_id": thread_id,
        "agent_type": agent_type
    }
    
    try:
        print(f"Sending request to {endpoint}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        with requests.post(endpoint, json=payload, headers=headers, stream=True) as response:
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response text: {response.text}")
            response.raise_for_status()
            
            # Track tool operations for better UX
            current_operation = None
            operation_stack = []
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        event_type = data.get("type")
                        
                        if event_type == "chatbot":
                            # Stream the chatbot response character by character
                            content = data.get("content", "")
                            print(content, end="", flush=True)
                            
                        elif event_type == "tool_start":
                            # Show tool start information
                            tool_name = data.get("tool_name", "Unknown")
                            tool_type = data.get("tool_type", "tool")
                            operation_index = data.get("operation_index", 0)
                            
                            if tool_type == "search":
                                print(f"\n[Searching web...]", end="", flush=True)
                            elif tool_type == "extract":
                                print(f"\n[Extracting content...]", end="", flush=True)
                            elif tool_type == "crawl":
                                print(f"\n[Crawling website...]", end="", flush=True)
                            else:
                                print(f"\n[Running {tool_name}...]", end="", flush=True)
                                
                            current_operation = {
                                "index": operation_index,
                                "name": tool_name,
                                "type": tool_type
                            }
                            operation_stack.append(current_operation)
                            
                        elif event_type == "tool_end":
                            # Show tool completion
                            operation_index = data.get("operation_index", 0)
                            if operation_stack and operation_stack[-1]["index"] == operation_index:
                                operation_stack.pop()
                                
                            # If we've completed all operations, prepare for answer
                            if not operation_stack:
                                print(f"\n[Generating response...]", end="", flush=True)
                                
                    except json.JSONDecodeError:
                        # Handle non-JSON lines if any
                        print(line.decode('utf-8'), end="", flush=True)
                        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the agent service at {endpoint}")
        print("Please make sure the service is running.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="CLI Agent Interface")
    parser.add_argument("--json", help="JSON input with input, thread_id, and agent_type")
    parser.add_argument("--input", help="Query input")
    parser.add_argument("--thread-id", help="Thread ID for conversation history")
    parser.add_argument("--agent-type", choices=["fast", "deep"], default="deep", help="Type of agent")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="API endpoint URL")
    
    args = parser.parse_args()
    
    # Handle JSON input
    if args.json:
        try:
            data = json.loads(args.json)
            query = data.get("input")
            thread_id = data.get("thread_id")
            agent_type = data.get("agent_type", "deep")
            endpoint = args.endpoint
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    else:
        # Handle individual arguments or interactive mode
        if args.input:
            query = args.input
            thread_id = args.thread_id
            agent_type = args.agent_type
            endpoint = args.endpoint
        else:
            # Interactive mode
            print("CLI Agent Interface")
            print("Connects to:", DEFAULT_ENDPOINT)
            print("Type 'exit' or 'quit' to exit\n")
            
            thread_id = str(uuid.uuid4())  # Maintain conversation context
            
            while True:
                query = get_user_input()
                
                if query.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    return
                    
                if not query:
                    continue
                
                print("\nResponse:")
                send_query(query, endpoint=endpoint, thread_id=thread_id, agent_type=agent_type)
                print("\n")  # Add spacing after response
            return
    
    # Execute single query
    if not query:
        print("Error: No input provided")
        sys.exit(1)
        
    print("\nResponse:")
    send_query(query, endpoint=endpoint, thread_id=thread_id, agent_type=agent_type)
    print("\n")  # Add spacing after response

if __name__ == "__main__":
    main()