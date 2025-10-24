# src/chatbot/chat_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import AIMessage
from typing import Annotated, TypedDict, List, Dict
from typing_extensions import NotRequired
import os
import logging, time, sys
from langgraph.prebuilt import create_react_agent
from src.tools import get_user_repo_summary, get_date, calories_burned, average_calories_per_day, max_daily_calories, longest_run, average_steps_per_day, max_steps_day, query_knowledge_base_thesis
from langsmith import Client

log = logging.getLogger("chat")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = True

client = Client()

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


        # Main agent with existing tools
        self.agent = create_react_agent(llm.llm, tools=[get_user_repo_summary, get_date, calories_burned, average_calories_per_day, max_daily_calories, longest_run, average_steps_per_day, max_steps_day])
        # RAG agent for thesis/report/dissertation
        self.rag_agent =create_react_agent(llm.llm,  tools=[query_knowledge_base_thesis])
        # Router agent to decide which agent to use
        self.router_agent = create_react_agent(
            llm.llm,
            tools=[],  # Router doesn't need tools, just decides routing
        )

        log.info("ChatGraphRunner.__init__: building graph")
        builder = StateGraph(ChatState)

        def router_node(state: ChatState) -> Dict[str, str]:
            """Router agent decides which agent to use based on the user message."""
            user_msg = state["messages"][-1].content

            # Use the router_agent to make the decision
            router_prompt = f"""Based on the following user message, decide which agent should handle it:
                            - Reply 'main' if it's about fitness data, repositories, or general queries
                            - Reply 'rag' if it's about thesis, report, or dissertation content

                            User message: {user_msg}

                            Reply with only 'main' or 'rag':"""

            result = self.router_agent.invoke({"messages": [{"role": "user", "content": router_prompt}]})
            decision = result["messages"][-1].content.strip().lower()

            # Fallback to keyword detection if router doesn't give clear answer
            if "rag" not in decision and "main" not in decision:
                if any(keyword in user_msg.lower() for keyword in ["tese", "relatório", "dissertação", "thesis", "report", "dissertation"]):
                    decision = "rag"
                else:
                    decision = "main"

            route = "rag" if "rag" in decision else "main"
            log.info(f"Router decision: {route}")
            return {"route": route}

        def chatbot(state: ChatState) -> Dict[str, List]:
            """Main agent node."""
            out = self.agent.invoke({"messages": state["messages"]})
            new_msgs = out["messages"][len(state["messages"]):]
            if not new_msgs and out["messages"]:
                new_msgs = [out["messages"][-1]]
            return {"messages": new_msgs}

        def rag_agent_node(state: ChatState) -> Dict[str, List]:
            """RAG agent node."""
            out = self.rag_agent.invoke({"messages": state["messages"]})
            new_msgs = out["messages"][len(state["messages"]):]
            if not new_msgs and out["messages"]:
                new_msgs = [out["messages"][-1]]
            return {"messages": new_msgs}

        # Add nodes
        builder.add_node("router", router_node)
        builder.add_node("chatbot", chatbot)
        builder.add_node("rag_agent", rag_agent_node)

        # Connect nodes
        builder.add_edge(START, "router")
        builder.add_conditional_edges(
            "router",
            lambda s: s.get("route", "main"),
            {"main": "chatbot", "rag": "rag_agent"}
        )
        builder.add_edge("chatbot", END)
        builder.add_edge("rag_agent", END)

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

 