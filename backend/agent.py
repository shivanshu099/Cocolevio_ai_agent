import os
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load .env from parent dir
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    final_output: str

# Define LLMs
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

def frontend_agent(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    # If the backend agent asked a question, we answer it autonomously
    if last_message and getattr(last_message, 'name', None) == "BackendAgent":
        sys_msg = SystemMessage(content="You are the Frontend Agent acting on behalf of a user. The Backend Agent has asked a clarification question about the user's task. Provide a brief, reasonable, and direct answer (e.g., choose a tone, length, or topic if asked). Do not explain yourself, just provide the choice.")
        response = llm.invoke([sys_msg] + messages)
        return {"messages": [HumanMessage(content=response.content, name="FrontendAgent")]}
    
    # First turn: passing the user's original task to the backend agent
    if last_message and getattr(last_message, 'name', None) == "User":
        return {"messages": [HumanMessage(content=f"Please process this task from the user: {last_message.content}", name="FrontendAgent")]}
    
    return {}

def backend_agent(state: AgentState):
    messages = state["messages"]
    
    sys_msg = SystemMessage(content="""You are the Backend Agent. You must complete the task given by the FrontendAgent. 
If the task is to write a blog or article, and the tone or length is not explicitly specified in the conversation, you MUST ask the FrontendAgent for clarification (e.g. "What tone should I use?").
Keep your clarification questions very brief. Do not generate the content until you have clarified.
If you have all the information you need, complete the task and return the final content.
CRITICAL: When you are returning the final content, you MUST prefix your entire response with "FINAL_RESULT:".""")
    
    response = llm.invoke([sys_msg] + messages)
    
    if response.content.strip().startswith("FINAL_RESULT:"):
        final_text = response.content.replace("FINAL_RESULT:", "").strip()
        return {"messages": [AIMessage(content="Here is the final result. Enjoy!", name="BackendAgent")], "final_output": final_text}
    else:
        return {"messages": [AIMessage(content=response.content, name="BackendAgent")]}

def router(state: AgentState) -> Literal["frontend_agent", "backend_agent", "__end__"]:
    if state.get("final_output"):
        return END
        
    messages = state["messages"]
    last_message = messages[-1]
    
    if getattr(last_message, 'name', None) == "BackendAgent":
        return "frontend_agent"
    else:
        return "backend_agent"

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("frontend_agent", frontend_agent)
workflow.add_node("backend_agent", backend_agent)

workflow.add_edge(START, "frontend_agent")
workflow.add_conditional_edges("frontend_agent", router)
workflow.add_conditional_edges("backend_agent", router)

app_graph = workflow.compile()
