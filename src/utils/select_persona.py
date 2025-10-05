import os
from typing import List


def list_personas(persona_dir: str = "personas_json") -> List[str]:
    """
    Returns a list of persona names (without prefix/suffix) from the folder.
    """
    personas = []
    for filename in os.listdir(persona_dir):
        if filename.startswith("persona_") and filename.endswith(".json"):
            name = filename[len("persona_"):-len(".json")]
            personas.append(name)
    return personas


def choose_persona(persona_dir: str = "personas_json") -> str:
    """
    Lists all personas and allows the user to select one from the terminal.
    """
    personas = list_personas(persona_dir)
    if not personas:
        raise FileNotFoundError(f"No personas found in directory '{persona_dir}'")

    print("Escolha uma persona para conversar:")
    for idx, name in enumerate(personas, 1):
        print(f"{idx}. {name}")

    while True:
        try:
            choice = int(input("Número da persona: "))
            if 1 <= choice <= len(personas):
                return personas[choice - 1]
        except (ValueError, IndexError):
            pass
        print("Escolha inválida. Tente novamente.")
