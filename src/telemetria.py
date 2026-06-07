"""
src/telemetria.py — Geração de dados simulados de telemetria
Trilha 4: MobilitySat (GNSS e Mobilidade)

Parâmetros monitorados:
  - drift_oscilador: desvio do oscilador atômico (ns/s)
  - sincronizacao_constelacao: qualidade de sync com a constelação (%)
  - integridade_sinal_l1: qualidade do sinal L1 (dB-Hz)
  - integridade_sinal_l5: qualidade do sinal L5 (dB-Hz)
  - precisao_efemeride: erro de efeméride (metros)
  - margem_potencia: margem de energia disponível (%)
  - temperatura_payload: temperatura do payload (°C)
"""

import random
import time
from datetime import datetime

# ── Limites nominais e críticos por parâmetro ──────────────────────────────
LIMITES = {
    "drift_oscilador": {
        "nominal_min": 0.0,
        "nominal_max": 2.0,
        "critico_max": 5.0,
        "unidade": "ns/s",
        "descricao": "Drift do oscilador atômico"
    },
    "sincronizacao_constelacao": {
        "nominal_min": 85.0,
        "nominal_max": 100.0,
        "critico_min": 70.0,
        "unidade": "%",
        "descricao": "Sincronização com a constelação"
    },
    "integridade_sinal_l1": {
        "nominal_min": 35.0,
        "nominal_max": 55.0,
        "critico_min": 25.0,
        "unidade": "dB-Hz",
        "descricao": "Integridade do sinal L1"
    },
    "integridade_sinal_l5": {
        "nominal_min": 33.0,
        "nominal_max": 52.0,
        "critico_min": 22.0,
        "unidade": "dB-Hz",
        "descricao": "Integridade do sinal L5"
    },
    "precisao_efemeride": {
        "nominal_min": 0.0,
        "nominal_max": 1.5,
        "critico_max": 3.0,
        "unidade": "m",
        "descricao": "Precisão da efeméride"
    },
    "margem_potencia": {
        "nominal_min": 30.0,
        "nominal_max": 100.0,
        "critico_min": 20.0,
        "unidade": "%",
        "descricao": "Margem de potência disponível"
    },
    "temperatura_payload": {
        "nominal_min": -10.0,
        "nominal_max": 45.0,
        "critico_max": 65.0,
        "unidade": "°C",
        "descricao": "Temperatura do payload"
    },
}

# Ciclo interno para simular série temporal realista
_ciclo = 0


def _variacao_senoidal(base: float, amplitude: float, ciclo: int) -> float:
    """Simula variação realista usando seno + ruído gaussiano."""
    import math
    seno = math.sin(ciclo * 0.3) * amplitude
    ruido = random.gauss(0, amplitude * 0.15)
    return round(base + seno + ruido, 3)


def coletar(modo: str = "normal") -> dict:
    """
    Retorna um snapshot da telemetria do satélite MobilitySat.

    Modos disponíveis:
      "normal"   — operação saudável dentro dos limites nominais
      "alerta"   — parâmetros em zona de atenção (perto dos limites)
      "critico"  — situação de crise com múltiplos parâmetros fora do range
      "aleatorio"— varia entre os três modos de forma probabilística
    """
    global _ciclo
    _ciclo += 1

    if modo == "aleatorio":
        roll = random.random()
        if roll < 0.70:
            modo = "normal"
        elif roll < 0.90:
            modo = "alerta"
        else:
            modo = "critico"

    if modo == "normal":
        dados = {
            "drift_oscilador":          _variacao_senoidal(0.8, 0.4, _ciclo),
            "sincronizacao_constelacao": _variacao_senoidal(95.0, 3.0, _ciclo),
            "integridade_sinal_l1":     _variacao_senoidal(44.0, 3.0, _ciclo),
            "integridade_sinal_l5":     _variacao_senoidal(42.0, 3.0, _ciclo),
            "precisao_efemeride":       _variacao_senoidal(0.6, 0.2, _ciclo),
            "margem_potencia":          _variacao_senoidal(75.0, 8.0, _ciclo),
            "temperatura_payload":      _variacao_senoidal(22.0, 5.0, _ciclo),
        }

    elif modo == "alerta":
        dados = {
            "drift_oscilador":          _variacao_senoidal(3.5, 0.5, _ciclo),
            "sincronizacao_constelacao": _variacao_senoidal(78.0, 3.0, _ciclo),
            "integridade_sinal_l1":     _variacao_senoidal(30.0, 2.0, _ciclo),
            "integridade_sinal_l5":     _variacao_senoidal(28.0, 2.0, _ciclo),
            "precisao_efemeride":       _variacao_senoidal(2.0, 0.3, _ciclo),
            "margem_potencia":          _variacao_senoidal(28.0, 3.0, _ciclo),
            "temperatura_payload":      _variacao_senoidal(50.0, 4.0, _ciclo),
        }

    else:  # critico
        dados = {
            "drift_oscilador":          round(random.uniform(5.5, 9.0), 3),
            "sincronizacao_constelacao": round(random.uniform(40.0, 68.0), 2),
            "integridade_sinal_l1":     round(random.uniform(15.0, 24.0), 2),
            "integridade_sinal_l5":     round(random.uniform(12.0, 21.0), 2),
            "precisao_efemeride":       round(random.uniform(3.5, 8.0), 3),
            "margem_potencia":          round(random.uniform(8.0, 18.0), 2),
            "temperatura_payload":      round(random.uniform(66.0, 90.0), 2),
        }

    # Garante que valores aleatórios não violem fisicamente o domínio
    dados["drift_oscilador"]           = max(0.0, dados["drift_oscilador"])
    dados["sincronizacao_constelacao"] = min(100.0, max(0.0, dados["sincronizacao_constelacao"]))
    dados["margem_potencia"]           = min(100.0, max(0.0, dados["margem_potencia"]))

    # Metadados do snapshot
    dados["_timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    dados["_ciclo"]     = _ciclo
    dados["_modo_sim"]  = modo

    return dados


def formatar_snapshot(dados: dict) -> str:
    """
    Retorna string formatada do snapshot para injeção no prompt.
    Remove metadados internos antes de formatar.
    """
    linhas = []
    for chave, valor in dados.items():
        if chave.startswith("_"):
            continue
        meta = LIMITES.get(chave, {})
        unidade = meta.get("unidade", "")
        descricao = meta.get("descricao", chave)
        linhas.append(f"  {descricao}: {valor} {unidade}")
    return "\n".join(linhas)
