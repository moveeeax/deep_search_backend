import logging
import os
import sys
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.ERROR, format="%(message)s")
import json
from contextlib import asynccontextmanager

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.schema import HumanMessage
from langgraph.graph.state import CompiledStateGraph as CompiledGraph
from pydantic import BaseModel

from backend.agent import WebAgent
from backend.prompts import REASONING_PROMPT, SIMPLE_PROMPT, ROUTING_PROMPT
from backend.utils import check_api_key

load_dotenv()

nano = ChatOpenAI(
    model=os.getenv("NANO_MODEL"), 
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

kimik2 = ChatOpenAI(
    model=os.getenv("KIMIK2_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def classify_query(query: str) -> str:
    """
    Classify a query as 'fast' or 'deep' using an LLM.
    
    Args:
        query: The user's query to classify
        
    Returns:
        str: Either 'fast' or 'deep'
    """
    # Use the cheaper/faster model for classification
    routing_llm = nano
    
    # Format the routing prompt with the query
    prompt = ROUTING_PROMPT.format(query=query)
    
    # Get classification from LLM
    response = routing_llm.invoke(prompt)
    classification = response.content.strip().lower()
    
    # Ensure we return a valid classification
    if classification not in ["fast", "deep"]:
        # Default to fast for safety
        classification = "fast"
    
    print(f"Query classified as: {classification}")
    return classification


@asynccontextmanager
async def lifespan(app: FastAPI):

    checkpointer = MemorySaver()
    agent = WebAgent(checkpointer=checkpointer)
    app.state.agent = agent
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def get_agent():
    return {
        "agent": app.state.agent,
    }


class AgentRequest(BaseModel):
    input: str
    thread_id: str = None
    agent_type: str = "auto"  # Default to auto routing


@app.get("/")
async def ping():
    return {"message": "Alive"}

@app.post("/agent")
async def agent_endpoint(
    body: AgentRequest,
    fastapi_request: Request,
    agent: CompiledGraph = Depends(get_agent),
):
    """
    Non-streaming endpoint for agent queries.
    Returns a complete response in a single JSON object.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    
    # Validate request body
    if not body.input:
        print("Missing input field")
        raise HTTPException(status_code=422, detail="Missing required field: input")
    # thread_id is now optional
    if not body.agent_type:
        print("Missing agent_type field")
        raise HTTPException(status_code=422, detail="Missing required field: agent_type")
    
    # Determine agent type - use provided type or classify automatically
    agent_type = body.agent_type
    if agent_type == "auto" or agent_type not in ["fast", "deep"]:
        # Automatically classify the query
        agent_type = classify_query(body.input)
        print(f"Automatically classified query as: {agent_type}")
    else:
        # Validate explicit agent_type
        if agent_type not in ["fast", "deep"]:
            print(f"Invalid agent_type: {agent_type}")
            raise HTTPException(status_code=422, detail="Invalid agent_type. Must be 'fast', 'deep', or 'auto'")
    
    # Get API key from environment variables
    if not api_key:
        print("Missing TAVILY_API_KEY in .env")
        raise HTTPException(status_code=422, detail="Missing TAVILY_API_KEY in .env")
    
    try:
        # Check authorization before proceeding
        check_api_key(api_key=api_key)

    except requests.exceptions.HTTPError as e:
        print(f"API key validation failed: {e}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"API key validation failed: {e.response.json()}"
        )
    except Exception as e:
        print(f"Unexpected error during API key validation: {e}")
        raise HTTPException(status_code=422, detail=f"API key validation failed: {str(e)}")
    if agent_type == "fast":
        agent_runnable = agent["agent"].build_graph(
            api_key=api_key, llm=nano, prompt=SIMPLE_PROMPT, summary_llm=nano, user_message=body.input
        )
        print("Fast agent running")
    elif agent_type == "deep":
        agent_runnable = agent["agent"].build_graph(
            api_key=api_key, llm=kimik2, prompt=REASONING_PROMPT, summary_llm=nano, user_message=body.input
        )
        print("Deep agent running")
    else:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    # Run the agent and collect all events
    config = {"configurable": {"thread_id": body.thread_id}}
    events_with_content = []
    tool_outputs = []  # List to store all tool outputs for aggregation

    async for event in agent_runnable.astream_events(
        input={"messages": [HumanMessage(content=body.input)]},
        config=config,
    ):
        # Collect events with content and their langgraph step
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"]
            if hasattr(content, "content") and content.content:
                # Get langgraph step from metadata
                langgraph_step = event.get("metadata", {}).get("langgraph_step", 0)
                events_with_content.append({
                    "content": content.content,
                    "langgraph_step": langgraph_step,
                    "event_type": "chat_model_stream"
                })

        elif event["event"] == "on_tool_end":
            tool_name = event.get("name", "unknown_tool")
            tool_output = event["data"].get("output")

            # Safely serialize tool output
            try:
                if hasattr(tool_output, "content"):
                    # Handle ToolMessage objects
                    serializable_output = str(tool_output.content)
                elif isinstance(tool_output, dict):
                    serializable_output = {
                        k: str(v) for k, v in tool_output.items()
                    }
                elif isinstance(tool_output, list):
                    serializable_output = [str(item) for item in tool_output]
                else:
                    serializable_output = str(tool_output)
            except:
                serializable_output = "Unable to serialize output"

            # Determine tool type from tool name
            tool_type = "search"
            if tool_name and "extract" in tool_name:
                tool_type = "extract"
            elif tool_name and "crawl" in tool_name:
                tool_type = "crawl"

            # Store tool output for aggregation
            tool_outputs.append({
                "name": tool_name,
                "type": tool_type,
                "output": serializable_output
            })

    # Process the final response
    if tool_outputs:
        # Aggregate all tool outputs
        aggregated_content = ""
        for tool_output in tool_outputs:
            aggregated_content += f"\n\nTool: {tool_output['name']}\nOutput: {tool_output['output']}"
        
        # Use LLM to generate a coherent response from all tool outputs
        aggregation_prompt = f"""
        Based on the following tool outputs, provide a comprehensive and coherent answer to the user's question: "{body.input}"
        
        Tool Outputs:
        {aggregated_content}
        
        Please synthesize all the information above into a clear, organized response that directly answers the user's question.
        Remove redundant information and focus on the most relevant findings.
        Format your response in markdown with appropriate headings and bullet points where applicable.
        """
        
        # Use the appropriate LLM for aggregation based on agent type
        aggregation_llm = nano if agent_type == "fast" else kimik2
        final_response = aggregation_llm.invoke(aggregation_prompt).content
        
        return {"response": final_response, "agent_type": agent_type}
    elif events_with_content:
        # Fallback to original method if no tool outputs were collected
        # Find the maximum langgraph step
        max_step = max(event["langgraph_step"] for event in events_with_content)
        
        # Collect content only from events with the maximum step
        final_content = ""
        for event in events_with_content:
            if event["langgraph_step"] == max_step:
                final_content += event["content"]
        
        # Filter out internal thoughts and only keep the final answer
        # Look for "Final Answer:" section and extract only that
        final_answer = ""
        lines = final_content.split('\n')
        
        # Extract final answer if it exists
        in_final_answer = False
        for line in lines:
            if "Final Answer:" in line:
                in_final_answer = True
                final_answer += line.replace("Final Answer:", "").strip() + "\n"
            elif in_final_answer and line.strip():
                final_answer += line + "\n"
            elif in_final_answer and not line.strip():
                break
        
        # If no "Final Answer:" section found, use the entire response
        # but filter out obvious internal thought patterns
        if not final_answer.strip():
            filtered_response = ""
            lines = final_content.split('\n')
            
            for line in lines:
                # Skip internal thought patterns
                if not any(pattern in line for pattern in ["Thought:", "Action:", "Action Input:", "Observation:"]):
                    filtered_response += line + "\n"
            
            final_answer = filtered_response.strip()
        else:
            final_answer = final_answer.strip()

        return {"response": final_answer, "agent_type": agent_type}
    else:
        return {"response": "No response generated.", "agent_type": agent_type}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
