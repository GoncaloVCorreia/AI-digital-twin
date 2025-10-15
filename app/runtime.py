from src.configs.groq_config import ConfigGroq
from src.llm.llm import GroqLLM
from src.chatbot.chat_graph import ChatGraphRunner

RUNNER: ChatGraphRunner | None = None

def init_runner():
    global RUNNER
    if RUNNER is None:
        RUNNER = ChatGraphRunner(GroqLLM(ConfigGroq()))
    return RUNNER

def get_runner():
    assert RUNNER is not None
    return RUNNER
