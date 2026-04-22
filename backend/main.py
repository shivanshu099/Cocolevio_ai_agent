from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import app_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str

@app.post("/api/chat")
async def chat_endpoint(request: TaskRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.task, name="User")],
        "final_output": ""
    }
    
    # Run the graph
    final_state = app_graph.invoke(initial_state)
    
    # Extract communication history to send back to frontend
    history = []
    for msg in final_state["messages"]:
        # Skip the original raw user message if we want, or include it
        name = getattr(msg, 'name', 'Unknown')
        if name in ["User", "FrontendAgent", "BackendAgent"]:
            history.append({
                "agent": name,
                "content": msg.content
            })
            
    return {
        "history": history,
        "final_result": final_state.get("final_output", "")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
