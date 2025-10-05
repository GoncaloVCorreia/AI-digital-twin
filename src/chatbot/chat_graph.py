from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage
from typing import Annotated, TypedDict, List, Dict
from typing_extensions import NotRequired

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]
    last_ai_message: NotRequired[str]

class ChatGraphRunner:
    """Handles message streaming via LangGraph using an LLM node."""

    def __init__(self, llm):
        self.config = {"configurable": {"thread_id": "1"}}
        self.memory = InMemorySaver()
        self.graph_builder = StateGraph(ChatState)

        # Register LLM node
        def chatbot(state: ChatState) -> Dict[str, List]:
            return {"messages": [llm.invoke(state["messages"])]}
        
        #Build the graph
        self.graph_builder.add_node("chatbot", chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

        self.graph = self.graph_builder.compile(checkpointer=self.memory)

    def stream_response(self, user_input: str, system_message: str):
        """Streams updates from the LangGraph."""
        events = self.graph.stream(
            {"messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ]},
            self.config,
            stream_mode="values",
        )

        last_ai_message = None
        #Get the last AI message from the events
        for event in events:
            for msg in event["messages"]:
                if isinstance(msg, AIMessage):
                    last_ai_message = msg
        return last_ai_message.content if last_ai_message else None
