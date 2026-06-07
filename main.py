"""Mission Control AI — MobilitySat · Ponto de entrada do sistema.

Trilha 4: GNSS e Mobilidade
FIAP · Ciência da Computação · Global Solution 2026.1
Disciplina: Prompt Engineering and Artificial Intelligence

Execução:
    python main.py
"""

from src.ui import run_cli
from src.engine import MissionEngine

if __name__ == "__main__":
    engine = MissionEngine()
    run_cli(engine)
