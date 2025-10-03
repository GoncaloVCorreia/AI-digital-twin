from typing import Annotated
from typing_extensions import TypedDict
import os
import json
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

def load_persona(name: str):
    path = f"persona/persona_{name}.json"
    with open(path, "r") as f:
        return json.load(f)
    
def build_promt(persona):
    prompt = f"""
    Tu és o digital twin de {persona['name']} ({persona['age']} anos, de {persona['location']}).
    Resumo: {persona['summary']}
    Formação: {', '.join([edu['degree'] + ' em ' + edu['institution'] for edu in persona['education']])}.
    Competências técnicas: {', '.join(persona['skills']['technical'])}.
    Competências interpessoais: {', '.join(persona['skills']['soft'])}.
    Pontos fortes: {', '.join(persona['strengths'])}.
    Pontos fracos: {', '.join(persona['weaknesses'])}.
    Objetivos: {', '.join(persona['goals'])}.

    Responde sempre como se fosses {persona['name']} numa entrevista de emprego. Mas responde de forma concisa e direta, sem divagar.
    Caso o input recebido não faça sentido, pede para reformular a pergunta.
    """
    return prompt

def list_personas():
    persona_dir = "persona"
    personas = []
    for filename in os.listdir(persona_dir):
        if filename.startswith("persona_") and filename.endswith(".json"):
            personas.append(filename[len("persona_"):-len(".json")])
    return personas

def select_persona():
    personas = list_personas()
    print("Escolha uma persona para conversar:")
    for idx, name in enumerate(personas, 1):
        print(f"{idx}. {name}")
    while True:
        try:
            choice = int(input("Número da persona: "))
            if 1 <= choice <= len(personas):
                return personas[choice - 1]
        except Exception:
            pass
        print("Escolha inválida. Tente novamente.")

def stream_graph_updates(user_input: str, persona_name: str):
    #first message in the message history is the system message
    system_message = build_promt(load_persona(persona_name))
    last_ai_message = None

    # ensure the system message is the first message in the conversation
    system_message_obj = {"role": "system", "content": system_message}
    events = graph.stream(
        {"messages": [system_message_obj, {"role": "user", "content": user_input}],
         },
        config,
        stream_mode="values",
    )

    for event in events:
        for msg in event["messages"]:
            if isinstance(msg, AIMessage):
                last_ai_message = msg

    if last_ai_message:
        print("Assistant:", last_ai_message.content)


if __name__ == "__main__":
    persona_name = select_persona()
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input, persona_name)
        except:
            # fallback if input() is not available
            user_input = "??"
            print("User: " + user_input)
            stream_graph_updates(user_input, persona_name)
            break