"""
FastAPI Backend for Email Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import os
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
    title="Email Agent API",
    description="AI-powered email assistant using LangGraph",
    version="1.0.0"
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
class EmailRequest(BaseModel):
    message: str
    
class EmailResponse(BaseModel):
    response: str
    tools_used: List[str]
    status: str

# Define agent state
class EmailAgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Define tools
@tool
def compose_email(recipient: str, subject: str, tone: str = "professional") -> str:
    """Compose a professional email."""
    return f"Email composed for {recipient} about '{subject}' in {tone} tone."

@tool
def categorize_email(email_content: str) -> str:
    """Categorize an email."""
    email_lower = email_content.lower()
    if any(word in email_lower for word in ["urgent", "asap", "immediately"]):
        return "urgent"
    elif any(word in email_lower for word in ["meeting", "project", "report"]):
        return "work"
    return "personal"

@tool
def extract_action_items(email_content: str) -> str:
    """Extract action items from email."""
    return f"Action items extracted from {len(email_content)} characters of content."

@tool
def draft_reply(original_email: str, reply_type: str = "acknowledge") -> str:
    """Draft a reply to an email."""
    return f"Reply drafted ({reply_type}) to the original email."

tools = [compose_email, categorize_email, extract_action_items, draft_reply]

# Initialize model and build graph
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
model_with_tools = model.bind_tools(tools)

def should_continue(state: EmailAgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

def call_model(state: EmailAgentState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(EmailAgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

email_agent = workflow.compile()

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Email Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/process": "POST - Process email request",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "email-agent-api"}

@app.post("/process", response_model=EmailResponse)
async def process_email(request: EmailRequest) -> EmailResponse:
    """
    Process an email request using the LangGraph agent
    """
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        response_text = ""
        tool_calls = []
        
        for output in email_agent.stream(inputs):
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
        
        return EmailResponse(
            response=response_text,
            tools_used=tool_calls,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
