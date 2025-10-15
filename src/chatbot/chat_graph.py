# src/chatbot/chat_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import AIMessage
from typing import Annotated, TypedDict, List, Dict
from typing_extensions import NotRequired
import os
import logging, time, sys

log = logging.getLogger("chat")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = True

CHECKPOINT_URL = os.getenv(
    "CHECKPOINT_URL",
    "postgresql://correia:postgres@localhost:5432/ai_project_db?options=-c%20client_encoding%3DUTF8"
)

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]
    last_ai_message: NotRequired[str]
    
class ChatGraphRunner:
    def __init__(self, llm):
        log.info("ChatGraphRunner.__init__: creating PostgresSaver")
        self._memory_cm = PostgresSaver.from_conn_string(CHECKPOINT_URL)
        log.info("ChatGraphRunner.__init__: entering saver context")
        self.memory = self._memory_cm.__enter__()
        log.info("ChatGraphRunner.__init__: calling memory.setup()")
        self.memory.setup()
        log.info("ChatGraphRunner.__init__: building graph")
        builder = StateGraph(ChatState)
        
        def chatbot(state: ChatState) -> Dict[str, List]:
            return {"messages": [llm.invoke(state["messages"])]}
        builder.add_node("chatbot", chatbot)
        builder.add_edge(START, "chatbot")
        builder.add_edge("chatbot", END)
        self.graph = builder.compile(checkpointer=self.memory)
        log.info("ChatGraphRunner.__init__: graph compiled ✅")
    def stream_response(self, user_input: str, system_message: str, session_id: str):
        config = {"configurable": {"thread_id": session_id}}

        log.info("➡️  get_state() start")
        t0 = time.time()    
        # <-- NEW: check if this thread already has messages
        snapshot = self.graph.get_state(config)
        log.info("✅ get_state() done in %.2fs", time.time()-t0)
        has_history = bool(snapshot and snapshot.values.get("messages"))

        msgs = []
        if not has_history and system_message:
            msgs.append({"role": "system", "content": system_message})
        msgs.append({"role": "user", "content": user_input})

        log.info("➡️  stream() start")
        t1 = time.time()
        events = self.graph.stream({"messages": msgs}, config, stream_mode="values")
        log.info("✅ stream() done in %.2fs", time.time()-t1)

        last_ai_message = None
        for event in events:
            for msg in event["messages"]:
                if isinstance(msg, AIMessage):
                    last_ai_message = msg
        return last_ai_message.content if last_ai_message else None
