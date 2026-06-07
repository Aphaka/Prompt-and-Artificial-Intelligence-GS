"""
src/ui.py — Interface CLI estilo Claude Code
Trilha 4: MobilitySat (GNSS e Mobilidade)

Usa Rich + prompt-toolkit para terminal estruturado e interativo.
Inspirado nas CLIs modernas: Claude Code, OpenAI Codex CLI.
"""

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from datetime import datetime
import time

console = Console()

session = PromptSession(
    style=Style.from_dict({
        "prompt": "#06B6D4 bold",
    })
)


def show_banner():
    """Exibe banner ASCII colorido no início — identidade visual do sistema."""
    console.clear()

    # Linha 1 — Global Solution
    linha1 = pyfiglet.figlet_format("Mission Control", font="ansi_shadow")
    linha2 = pyfiglet.figlet_format("MobilitySat", font="ansi_shadow")

    console.print(Align.center(Text(linha1, style="bold #06B6D4")))
    console.print(Align.center(Text(linha2, style="bold #A855F7")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP · Trilha 4: GNSS e Mobilidade ──",
             style="italic #8484A0")
    ))
    console.print()

    # Card de informações
    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="#8484A0")
    info_table.add_column(style="#06B6D4")
    info_table.add_row("Satélite simulado:", "GNSS MEO — estilo GPS/Galileo/GLONASS")
    info_table.add_row("Modelo de IA:",      "gpt-oss:120b via Ollama Cloud")
    info_table.add_row("Setor de impacto:",  "Mobilidade, Logística e Agricultura de Precisão")
    info_table.add_row("Comandos:",          "/help  /status  /modo  /about  /clear  /exit")

    console.print(Panel(
        info_table,
        title="◆ MISSION CONTROL AI",
        border_style="#06B6D4",
        padding=(1, 2),
    ))
    console.print()


def show_help():
    """Exibe tabela de ajuda com todos os comandos disponíveis."""
    table = Table(
        title="Comandos disponíveis",
        border_style="#06B6D4",
        header_style="bold #A855F7",
        show_lines=True,
    )
    table.add_column("Comando", style="#06B6D4", min_width=28)
    table.add_column("Descrição", style="white")

    table.add_row("/help",                    "Exibe esta tabela de comandos")
    table.add_row("/status",                  "Mostra snapshot completo da telemetria atual")
    table.add_row("/modo <modo>",             "Altera modo de simulação: normal | alerta | critico | aleatorio")
    table.add_row("/about",                   "Informações sobre a missão e a trilha")
    table.add_row("/clear",                   "Limpa o terminal e exibe o banner novamente")
    table.add_row("/exit  ou  Ctrl+C",        "Encerra o sistema")
    table.add_row("",                         "")
    table.add_row("[qualquer pergunta]",      "Analisa a telemetria atual e responde via IA")

    console.print(table)
    console.print()
    console.print(
        Panel(
            "[#8484A0]Exemplos de perguntas:[/]\n"
            "[#06B6D4]❯[/] Como está a missão?\n"
            "[#06B6D4]❯[/] O que está causando a degradação do sinal?\n"
            "[#06B6D4]❯[/] Frotas em campo podem continuar operando?\n"
            "[#06B6D4]❯[/] Quais ações devo tomar agora?\n"
            "[#06B6D4]❯[/] Qual o impacto para a agricultura de precisão?",
            border_style="#8484A0",
            title="Exemplos",
        )
    )
    console.print()


def show_about():
    """Exibe informações sobre a missão MobilitySat."""
    about_text = (
        "[bold #06B6D4]MobilitySat[/] — Satélite GNSS de navegação em órbita MEO (~20.200 km)\n\n"
        "[bold]Parâmetros monitorados:[/]\n"
        "  • Drift do oscilador atômico (ns/s)\n"
        "  • Sincronização com a constelação (%)\n"
        "  • Integridade do sinal L1 e L5 (dB-Hz)\n"
        "  • Precisão da efeméride (metros)\n"
        "  • Margem de potência disponível (%)\n"
        "  • Temperatura do payload (°C)\n\n"
        "[bold]Personas atendidas:[/]\n"
        "  🛰️  Engenheiro de segmento espacial\n"
        "  🚛  Gestor de frota logística (3.200 veículos)\n"
        "  🌱  Operador de agricultura de precisão (180.000 ha)\n\n"
        "[bold]Impacto terrestre:[/]\n"
        "  Cada degradação em órbita afeta diretamente sistemas de navegação,\n"
        "  rotas de veículos autônomos e plantadeiras de precisão no campo."
    )
    console.print(Panel(
        about_text,
        title="◆ Sobre a Missão MobilitySat",
        border_style="#A855F7",
        padding=(1, 2),
    ))
    console.print()


def show_response(text: str, nivel: str = None):
    """Renderiza resposta da IA em painel com timestamp e cor por severidade."""
    now = datetime.now().strftime("%H:%M:%S")

    # Cor da borda por nível de severidade
    cor_borda = "#06B6D4"  # padrão ciano
    if nivel == "CRÍTICO":
        cor_borda = "red"
    elif nivel == "ATENÇÃO":
        cor_borda = "yellow"
    elif nivel == "OK":
        cor_borda = "green"

    console.print(Panel(
        text,
        title="◆ Mission Control AI",
        subtitle=f"[#8484A0]{now}[/]",
        border_style=cor_borda,
        padding=(1, 2),
    ))
    console.print()


def show_thinking():
    """Exibe spinner enquanto a IA processa."""
    return Live(
        Panel(
            Spinner("dots", text="[#06B6D4] Consultando IA e analisando telemetria...[/]"),
            border_style="#8484A0",
        ),
        refresh_per_second=10,
        transient=True,
    )


def show_engine_pending():
    """Aviso de engine não implementado (stub)."""
    console.print(
        Panel(
            "[yellow]⚠  Engine status: AGUARDANDO IMPLEMENTAÇÃO ✗[/]\n\n"
            "A interface CLI está funcionando, mas a lógica de análise\n"
            "ainda não foi conectada. O grupo precisa:\n\n"
            "  1. Completar [bold]src/telemetria.py[/]\n"
            "  2. Completar [bold]src/alertas.py[/]\n"
            "  3. Escrever o system prompt em [bold]prompts/system_prompt.md[/]\n"
            "  4. Sobrescrever [bold]analyze()[/] em [bold]src/engine.py[/]",
            border_style="yellow",
            title="◆ Setup pendente",
        )
    )
    console.print()


def _inferir_nivel(resposta: str) -> str:
    """Tenta inferir o nível de severidade a partir do texto da resposta."""
    upper = resposta.upper()
    if "CRÍTICO" in upper or "CRITICO" in upper or "🔴" in resposta:
        return "CRÍTICO"
    if "ATENÇÃO" in upper or "ATENCAO" in upper or "🟡" in resposta:
        return "ATENÇÃO"
    if "NOMINAL" in upper or "✅" in resposta:
        return "OK"
    return None


def run_cli(engine):
    """Loop principal da CLI — recebe o motor e gerencia toda a interação."""
    show_banner()

    if not engine.is_ready():
        show_engine_pending()

    while True:
        try:
            user_input = session.prompt("❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[#8484A0]Encerrando Mission Control AI... Até a próxima missão. 🛰️[/]\n")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # ── Comandos built-in ───────────────────────────────────────────
        if cmd in ("/exit", "/quit", "exit", "quit"):
            console.print("[#8484A0]Encerrando Mission Control AI... Até a próxima missão. 🛰️[/]\n")
            break

        if cmd == "/help":
            show_help()
            continue

        if cmd == "/about":
            show_about()
            continue

        if cmd == "/clear":
            show_banner()
            continue

        if cmd == "/status":
            with show_thinking():
                snapshot = engine.status_snapshot()
            show_response(snapshot)
            continue

        # ── Comando /modo (aceita tanto via engine quanto direto na UI) ─
        if cmd.startswith("/modo"):
            resposta = engine.analyze(user_input)
            show_response(resposta)
            continue

        # ── Qualquer pergunta → motor de análise ─────────────────────
        if not engine.is_ready():
            show_response(engine.analyze(user_input))
            continue

        with show_thinking():
            resposta = engine.analyze(user_input)

        nivel = _inferir_nivel(resposta)
        show_response(resposta, nivel=nivel)
