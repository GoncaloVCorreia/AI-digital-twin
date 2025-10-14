"""from configs.groq_config import ConfigGroq
from llm.llm import GroqLLM
from chatbot.chat_graph import ChatGraphRunner
from personas.persona import  load_persona
from utils.select_persona import choose_persona

def main():
    # === 1. Initialize model ===
    config = ConfigGroq()
    llm = GroqLLM(config)
    graph_runner = ChatGraphRunner(llm)

  

    # === 3. Chat loop ===
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        response = graph_runner.stream_response(user_input, system_prompt)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()"""
from configs.groq_config import ConfigGroq
from llm.llm import GroqLLM
from chatbot.chat_graph import ChatGraphRunner
from personas.persona import  load_persona
from utils.select_persona import choose_persona
import uuid

def main():
    config = ConfigGroq()
    llm = GroqLLM(config)
    runner = ChatGraphRunner(llm)
    
     # === 2. Select and load persona ===
    persona_name = choose_persona("personas_json")
    persona = load_persona(persona_name, persona_dir="personas_json")  
    system_prompt = persona.build_prompt()

    print(f"\nPersona carregada: {persona.name}\n")
    print("Digite 'quit' para sair.\n")

    session_id = str(uuid.uuid4())
    print(f"Session started: {session_id}")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        response = runner.stream_response(user_input, system_prompt, session_id)
        print(f"Assistant: {response}")



