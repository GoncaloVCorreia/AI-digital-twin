from typing import Annotated
from typing_extensions import TypedDict
import os
from langgraph.checkpoint.memory import InMemorySaver


from dotenv import load_dotenv  # Add this import

from langchain_groq import ChatGroq


from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage


class State(TypedDict):
   
    messages: Annotated[list, add_messages]

def init_chat_model(model_name: str = "openai/gpt-oss-20b"):
    load_dotenv()  # Load environment variables from .env
    groq_api_key = os.environ.get("GROQ_API_KEY")  # Fetch the key
    return ChatGroq(
        groq_api_key=groq_api_key,  # Use the fetched key
        model_name=model_name
    )

config = {"configurable": {"thread_id": "1"}}
graph_builder = StateGraph(State)

llm = init_chat_model()
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)



def stream_graph_updates(user_input: str):
    last_ai_message = None

    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in events:
        for msg in event["messages"]:
            if isinstance(msg, AIMessage):
                last_ai_message = msg

    if last_ai_message:
        print("Assistant:", last_ai_message.content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break