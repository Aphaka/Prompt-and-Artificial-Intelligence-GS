"""
src/engine.py — Motor de análise da Mission Control AI
Trilha 4: MobilitySat (GNSS e Mobilidade)

Este arquivo combina:
  - Função llm() para integração com Ollama Cloud
  - Classe MissionEngine que une telemetria + alertas + IA
"""

import os
from ollama import Client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from src.telemetria import coletar, formatar_snapshot, LIMITES
from src.alertas import avaliar, resumo_alertas, NIVEL_CRITICO, NIVEL_ATENCAO

load_dotenv()

# Identificação da trilha
TRILHA = "mobilitysat"

# ── Cliente Ollama Cloud ──────────────────────────────────────────────────
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + os.environ.get("OLLAMA_API_KEY", "")}
)


def llm(prompt: str, system: str = None, max_tokens: int = 900, temperature: float = 0.3) -> str:
    """
    Envia prompt ao gpt-oss:120b via Ollama Cloud e retorna texto.
    Ponto único de contato do projeto com o modelo de linguagem.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resposta = client.chat(
            model="gpt-oss:120b",
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False,
        )
        return resposta["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Erro ao consultar IA: {e}"


def load_system_prompt() -> str:
    """Lê o system prompt do arquivo prompts/system_prompt.md."""
    path = Path("prompts/system_prompt.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Fallback compacto caso o arquivo não exista
    return (
        "Você é o Mission Control AI — MobilitySat, sistema de análise de satélites GNSS. "
        "Analise dados de telemetria e articule o impacto terrestre de cada anomalia para "
        "frotas logísticas, agricultores de precisão e operadores portuários. "
        "Responda em português brasileiro. Seja direto e técnico."
    )


# ── Histórico de contexto (diferencial: memória de ciclos) ───────────────
_historico: list[dict] = []
_MAX_HISTORICO = 5  # mantém os últimos 5 snapshots no contexto


class MissionEngine:
    """Motor de análise — integra telemetria, alertas e IA generativa."""

    def __init__(self):
        self.trilha        = TRILHA
        self.system_prompt = load_system_prompt()
        self._modo_sim     = "aleatorio"  # padrão: simula cenários variados
        self._ultimo_dados  = None
        self._ultimo_result = None

    # ── Configuração ────────────────────────────────────────────────────
    def set_modo(self, modo: str):
        """Define o modo de simulação: normal | alerta | critico | aleatorio."""
        modos_validos = {"normal", "alerta", "critico", "aleatorio"}
        if modo in modos_validos:
            self._modo_sim = modo

    def is_ready(self) -> bool:
        """Retorna True — engine está implementado."""
        return True

    # ── Status snapshot (comando /status) ───────────────────────────────
    def status_snapshot(self) -> str:
        """Retorna painel textual com o estado atual da telemetria."""
        dados   = coletar(self._modo_sim)
        result  = avaliar(dados)
        self._ultimo_dados  = dados
        self._ultimo_result = result

        nivel = result["nivel_geral"]
        emoji_nivel = {"OK": "✅", "ATENÇÃO": "🟡", "CRÍTICO": "🔴"}.get(nivel, "⚪")

        linhas = [
            f"🛰️  MobilitySat — GNSS Navegação | Ciclo #{dados['_ciclo']} | {dados['_timestamp']}",
            f"{'─' * 60}",
            f"Status Geral: {emoji_nivel} {nivel}",
            f"{'─' * 60}",
            "",
            "📡 TELEMETRIA ATUAL:",
        ]

        for alerta in result["alertas"]:
            emoji = {"OK": "✅", "ATENÇÃO": "🟡", "CRÍTICO": "🔴"}.get(alerta["nivel"], "⚪")
            linhas.append(
                f"  {emoji} {alerta['descricao']:<35} {alerta['valor']:>8} {alerta['unidade']}"
            )

        if result["respostas_automatizadas"]:
            linhas += ["", "⚡ AÇÕES AUTOMATIZADAS:"]
            for r in result["respostas_automatizadas"]:
                linhas.append(f"  [{r['acao']}]")
                linhas.append(f"  → {r['descricao']}")

        linhas += [
            "",
            f"Modo de simulação: {self._modo_sim} | Trilha: {self.trilha.upper()}",
            "Use /modo <normal|alerta|critico|aleatorio> para trocar o cenário.",
        ]

        return "\n".join(linhas)

    # ── Análise principal (loop da CLI) ─────────────────────────────────
    def analyze(self, pergunta_usuario: str) -> str:
        """
        Pipeline completo:
          1. Coleta telemetria
          2. Avalia alertas em Python
          3. Monta prompt com dados + alertas + histórico + pergunta
          4. Chama LLM via Ollama Cloud
          5. Atualiza histórico de contexto
          6. Retorna resposta da IA
        """
        # ── Comando especial: trocar modo de simulação ──────────────────
        if pergunta_usuario.startswith("/modo"):
            partes = pergunta_usuario.strip().split()
            if len(partes) == 2:
                self.set_modo(partes[1])
                return (
                    f"✅ Modo de simulação alterado para: **{self._modo_sim}**\n"
                    f"A próxima consulta usará dados no modo '{self._modo_sim}'."
                )

        # 1. Coletar dados de telemetria
        dados  = coletar(self._modo_sim)
        result = avaliar(dados)
        self._ultimo_dados  = dados
        self._ultimo_result = result

        # 2. Construir contexto de histórico (diferencial: memória temporal)
        ctx_historico = ""
        if _historico:
            ctx_historico = "\n\nHISTÓRICO DOS ÚLTIMOS CICLOS (para análise de tendência):\n"
            for h in _historico[-_MAX_HISTORICO:]:
                ctx_historico += (
                    f"  Ciclo #{h['ciclo']} [{h['timestamp']}] — "
                    f"Nível: {h['nivel_geral']} | "
                    f"Drift: {h['drift']:.2f} ns/s | "
                    f"Sync: {h['sync']:.1f}% | "
                    f"Potência: {h['potencia']:.1f}%\n"
                )

        # 3. Montar prompt com injeção dinâmica de dados
        prompt = f"""
SNAPSHOT DE TELEMETRIA — MobilitySat GNSS
Timestamp: {dados['_timestamp']} | Ciclo: {dados['_ciclo']}

PARÂMETROS ATUAIS:
{formatar_snapshot(dados)}

AVALIAÇÃO AUTOMÁTICA DE ALERTAS:
{resumo_alertas(result)}
{ctx_historico}

PERGUNTA DO OPERADOR:
{pergunta_usuario}

Responda com base nos dados acima. Articule o impacto terrestre de qualquer anomalia 
para frotas logísticas, agricultura de precisão e operações portuárias automatizadas.
""".strip()

        # 4. Chamar LLM
        resposta_ia = llm(prompt, system=self.system_prompt)

        # 5. Atualizar histórico
        _historico.append({
            "ciclo":       dados["_ciclo"],
            "timestamp":   dados["_timestamp"],
            "nivel_geral": result["nivel_geral"],
            "drift":       dados.get("drift_oscilador", 0),
            "sync":        dados.get("sincronizacao_constelacao", 100),
            "potencia":    dados.get("margem_potencia", 100),
        })
        if len(_historico) > _MAX_HISTORICO * 2:
            del _historico[:-_MAX_HISTORICO]

        return resposta_ia
