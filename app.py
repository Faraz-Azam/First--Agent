import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
import operator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# Get API Key from environment
api_key = os.getenv("LLM_API_KEY")

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_request: str
    next_node: str
    final_response: str

# Initialize Gemini Model
llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash",
    temperature=0.7
)

# 2. Sub-Agent Nodes
def rag_agent(state: AgentState):
    prompt = f"Answer this using indexed document context: {state['user_request']}"
    res = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": f"[RAG Agent Response]\n{res.content}"}

def github_agent(state: AgentState):
    prompt = f"Process this GitHub repository request: {state['user_request']}"
    res = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": f"[GitHub MCP Agent Response]\n{res.content}"}

def calendar_agent(state: AgentState):
    prompt = f"Handle this Google Calendar task: {state['user_request']}"
    res = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": f"[Calendar MCP Agent Response]\n{res.content}"}

def email_agent(state: AgentState):
    prompt = f"Draft/Process this email request: {state['user_request']}"
    res = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": f"[Email MCP Agent Response]\n{res.content}"}

# 3. Supervisor Router
def supervisor_node(state: AgentState):
    req = state["user_request"].lower()
    if "pdf" in req or "document" in req or "chapter" in req:
        route = "rag_agent"
    elif "github" in req or "repo" in req or "code" in req:
        route = "github_agent"
    elif "meeting" in req or "calendar" in req or "schedule" in req:
        route = "calendar_agent"
    elif "email" in req or "mail" in req or "draft" in req:
        route = "email_agent"
    else:
        route = "rag_agent"
    return {"next_node": route}

# 4. LangGraph Setup
builder = StateGraph(AgentState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("rag_agent", rag_agent)
builder.add_node("github_agent", github_agent)
builder.add_node("calendar_agent", calendar_agent)
builder.add_node("email_agent", email_agent)

builder.set_entry_point("supervisor")
builder.add_conditional_edges("supervisor", lambda s: s["next_node"])

builder.add_edge("rag_agent", END)
builder.add_edge("github_agent", END)
builder.add_edge("calendar_agent", END)
builder.add_edge("email_agent", END)

graph = builder.compile()

# 5. CLI Assistant Loop
if __name__ == "__main__":
    print("\n==========================================")
    print("   SMIT LangGraph Multi-Agent Assistant   ")
    print("==========================================\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        res = graph.invoke({"user_request": query, "messages": []})
        print(f"\nAssistant:\n{res['final_response']}\n")