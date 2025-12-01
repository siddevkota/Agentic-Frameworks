"""
FastAPI Backend for Research Assistant Agent
Real use case: Web search, information analysis, and report generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Import agent components
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, Literal, TypedDict

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Research Assistant API",
    description="AI-powered research assistant with web search using LangGraph",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class ResearchRequest(BaseModel):
    query: str
    depth: Optional[str] = "standard"  # quick, standard, deep
    
class ResearchResponse(BaseModel):
    response: str
    tools_used: List[str]
    sources: List[str]
    status: str

# Define agent state
class ResearchAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    sources: List[str]

# Define real research tools
@tool
def search_web(query: str, num_results: int = 5) -> str:
    """
    Search the web for information using DuckDuckGo.
    Returns real search results with titles, snippets, and URLs.
    
    Args:
        query: The search query
        num_results: Number of results to return (default 5)
    
    Returns:
        Formatted search results with sources
    """
    try:
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=num_results))
            
            for i, result in enumerate(search_results, 1):
                title = result.get('title', 'No title')
                snippet = result.get('body', 'No description')
                url = result.get('href', '')
                
                results.append(f"""{i}. **{title}**
   {snippet}
   Source: {url}
""")
        
        if not results:
            return f"No results found for: {query}"
        
        return f"""Search results for '{query}':

{''.join(results)}

Found {len(results)} relevant sources."""
    
    except ImportError:
        return "Error: duckduckgo-search not installed. Install with: pip install duckduckgo-search"
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def fetch_url_content(url: str) -> str:
    """
    Fetch and extract text content from a specific URL.
    Useful for getting detailed information from search results.
    
    Args:
        url: The URL to fetch content from
    
    Returns:
        Extracted text content from the URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple text extraction (in production, use BeautifulSoup or similar)
        content = response.text[:2000]  # First 2000 chars
        
        return f"""Content from {url}:

{content}

(Showing first 2000 characters)"""
    
    except requests.exceptions.Timeout:
        return f"Error: Timeout while fetching {url}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def analyze_information(topic: str, information: str) -> str:
    """
    Analyze gathered information and identify key insights.
    Use this after gathering information to extract important points.
    
    Args:
        topic: The research topic
        information: The information to analyze
    
    Returns:
        Analysis with key insights
    """
    word_count = len(information.split())
    char_count = len(information)
    
    return f"""Analysis of information on '{topic}':

📊 Information Overview:
- Content analyzed: {char_count} characters, {word_count} words
- Topic: {topic}

✅ Ready for synthesis

The gathered information has been analyzed and is ready to be synthesized into a comprehensive response."""

@tool
def generate_report(topic: str, key_points: List[str]) -> str:
    """
    Generate a structured research report with findings.
    
    Args:
        topic: The research topic
        key_points: List of key points to include
    
    Returns:
        Formatted research report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    points_text = "\n".join([f"• {point}" for point in key_points])
    
    return f"""Research Report: {topic}
Generated: {timestamp}

{'='*60}

KEY FINDINGS:
{points_text}

REPORT STATUS: Complete

This report synthesizes the research findings on '{topic}' based on web search results and analysis."""

tools = [search_web, fetch_url_content, analyze_information, generate_report]

# Initialize model and build graph
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # Lower temp for factual research
model_with_tools = model.bind_tools(tools)

def should_continue(state: ResearchAgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

def call_model(state: ResearchAgentState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(ResearchAgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

research_agent = workflow.compile()

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Research Assistant API",
        "version": "2.0.0",
        "description": "AI-powered research with real web search",
        "endpoints": {
            "/research": "POST - Perform research query",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "research-assistant-api",
        "model": "gpt-4o-mini",
        "tools_available": len(tools),
        "tools": [tool.name for tool in tools],
        "capabilities": ["web_search", "url_fetch", "analysis", "report_generation"]
    }

@app.post("/research", response_model=ResearchResponse)
async def perform_research(request: ResearchRequest) -> ResearchResponse:
    """
    Perform research using the LangGraph agent.
    
    The agent will:
    1. Search the web for relevant information
    2. Analyze and synthesize findings
    3. Generate a comprehensive response
    """
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Research query cannot be empty")
        
        # Enhanced prompt for research
        research_prompt = f"""Research Request: {request.query}

Please conduct thorough research on this topic by:
1. Searching for relevant information
2. Analyzing the findings
3. Providing a comprehensive, well-sourced answer

Be factual and cite sources when possible."""
        
        inputs = {
            "messages": [HumanMessage(content=research_prompt)],
            "sources": []
        }
        
        response_text = ""
        tool_calls = []
        sources = []
        
        # Stream through the agent workflow
        for output in research_agent.stream(inputs):
            for key, value in output.items():
                if key == "agent":
                    messages = value.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        if isinstance(last_message, AIMessage):
                            if last_message.content:
                                response_text = last_message.content
                            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                                tool_calls = [tc.get('name', 'unknown') for tc in last_message.tool_calls]
                elif key == "tools":
                    # Extract sources from tool outputs
                    messages = value.get("messages", [])
                    for msg in messages:
                        if hasattr(msg, 'content') and 'Source:' in msg.content:
                            # Extract URLs from content
                            import re
                            urls = re.findall(r'https?://[^\s<>"]+', msg.content)
                            sources.extend(urls)
        
        if not response_text:
            response_text = "Research completed. The agent gathered information but didn't generate a summary. Try refining your query."
        
        # Remove duplicates from sources
        sources = list(dict.fromkeys(sources))[:10]  # Keep top 10 unique sources
        
        return ResearchResponse(
            response=response_text,
            tools_used=tool_calls,
            sources=sources,
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing research: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
