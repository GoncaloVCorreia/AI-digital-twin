from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket import routes as ws_routes
from src.configs.groq_config import ConfigGroq
from src.llm.llm import GroqLLM
from src.chatbot.chat_graph import ChatGraphRunner


app = FastAPI(
    title="AI-Digital-Twin API",
    version="0.1.0",
    description="API com WebSockets e integração com personas"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    config = ConfigGroq()
    llm = GroqLLM(config)
    graph_runner = ChatGraphRunner(llm)
    app.state.llm = llm
    app.state.graph_runner = graph_runner

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(ws_routes.router)
