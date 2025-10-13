# src/chatbot/chat_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from typing import Annotated, TypedDict, List, Dict
from typing_extensions import NotRequired
import os

DATABASE_URL = "postgresql://correia:postgres@localhost/ai_project_db?options=-c%20client_encoding%3DUTF8"

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]
    last_ai_message: NotRequired[str]
    
def make_checkpointer():
    if os.getenv("USE_MEMORY_CHECKPOINTER") == "1":
        return MemorySaver()
    url = DATABASE_URL
    return PostgresSaver.from_conn_string(url)
    
class ChatGraphRunner:
    def __init__(self, llm):
        self._memory_cm = make_checkpointer()
        self.memory = self._memory_cm.__enter__()
        self.memory.setup()

        builder = StateGraph(ChatState)
        def chatbot(state: ChatState) -> Dict[str, List]:
            return {"messages": [llm.invoke(state["messages"])]}
        builder.add_node("chatbot", chatbot)
        builder.add_edge(START, "chatbot")
        builder.add_edge("chatbot", END)
        self.graph = builder.compile(checkpointer=self.memory)

    def stream_response(self, user_input: str, system_message: str, session_id: str):
        config = {"configurable": {"thread_id": session_id}}

        # <-- NEW: check if this thread already has messages
        snapshot = self.graph.get_state(config)
        has_history = bool(snapshot and snapshot.values.get("messages"))

        msgs = []
        if not has_history and system_message:
            msgs.append({"role": "system", "content": system_message})
        msgs.append({"role": "user", "content": user_input})

        events = self.graph.stream({"messages": msgs}, config, stream_mode="values")

        last_ai_message = None
        for event in events:
            for msg in event["messages"]:
                if isinstance(msg, AIMessage):
                    last_ai_message = msg
        return last_ai_message.content if last_ai_message else None
