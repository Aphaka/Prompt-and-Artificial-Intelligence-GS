"""
banner_ascii.py — Gerador de banner ASCII para Mission Control AI
Uso:
    python banner_ascii.py                          # Banner padrão
    python banner_ascii.py -fonts                   # Lista fontes disponíveis
    python banner_ascii.py -font slant -text "Texto" # Testa fonte específica
    python banner_ascii.py -demo                    # Demonstra 8 fontes diferentes
"""

import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns

console = Console()


def banner_padrao():
    """Exibe o banner padrão do projeto."""
    linha1 = pyfiglet.figlet_format("Mission Control", font="ansi_shadow")
    linha2 = pyfiglet.figlet_format("MobilitySat", font="ansi_shadow")

    console.print(Align.center(Text(linha1, style="bold #06B6D4")))
    console.print(Align.center(Text(linha2, style="bold #A855F7")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP ──",
             style="italic #8484A0")
    ))


def listar_fontes():
    """Lista todas as fontes disponíveis no PyFiglet."""
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(f"\n[bold #06B6D4]Total de fontes disponíveis: {len(fontes)}[/]\n")
    for i, fonte in enumerate(sorted(fontes)):
        print(f"  {fonte}", end="\t" if (i + 1) % 4 != 0 else "\n")
    print()


def testar_fonte(fonte: str, texto: str = "Mission Control"):
    """Exibe o texto em uma fonte específica."""
    try:
        banner = pyfiglet.figlet_format(texto, font=fonte)
        console.print(Text(banner, style="bold #06B6D4"))
        console.print(f"[#8484A0]Fonte: {fonte}[/]\n")
    except pyfiglet.FontNotFound:
        console.print(f"[red]Fonte '{fonte}' não encontrada. Use -fonts para listar.[/]")


def demo_fontes():
    """Demonstra 8 fontes diferentes lado a lado."""
    fontes_demo = [
        "ansi_shadow", "slant", "banner3-D", "doom",
        "big", "block", "isometric1", "3-d"
    ]
    texto_demo = "GNSS"
    console.print("\n[bold #06B6D4]Demonstração de fontes:[/]\n")

    for fonte in fontes_demo:
        try:
            banner = pyfiglet.figlet_format(texto_demo, font=fonte)
            console.print(Panel(
                Text(banner, style="bold #06B6D4"),
                title=f"[#8484A0]{fonte}[/]",
                border_style="#8484A0",
            ))
        except Exception:
            pass


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        banner_padrao()

    elif "-fonts" in args:
        listar_fontes()

    elif "-demo" in args:
        demo_fontes()

    elif "-font" in args:
        idx = args.index("-font")
        fonte = args[idx + 1] if idx + 1 < len(args) else "ansi_shadow"
        texto = " ".join(args[args.index("-text") + 1:]) if "-text" in args else "Mission Control AI"
        testar_fonte(fonte, texto)

    else:
        banner_padrao()
