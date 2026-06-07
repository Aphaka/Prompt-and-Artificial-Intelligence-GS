"""
src/alertas.py — Lógica de alertas e tomada de decisão em Python
Trilha 4: MobilitySat (GNSS e Mobilidade)

Regras de threshold implementadas em código Python (não no prompt).
A IA serve para contextualizar e explicar — a decisão de criticidade é feita aqui.
"""

from src.telemetria import LIMITES

# ── Níveis de severidade ────────────────────────────────────────────────────
NIVEL_OK       = "OK"
NIVEL_ATENCAO  = "ATENÇÃO"
NIVEL_CRITICO  = "CRÍTICO"


def _avaliar_parametro(nome: str, valor: float) -> dict:
    """
    Avalia um único parâmetro contra os thresholds definidos em LIMITES.
    Retorna dict com nivel, nome, valor, unidade e mensagem.
    """
    meta = LIMITES.get(nome, {})
    unidade = meta.get("unidade", "")
    descricao = meta.get("descricao", nome)

    nivel   = NIVEL_OK
    mensagem = f"{descricao} dentro do nominal."

    # Verifica threshold de máximo (ex: drift alto é ruim)
    if "critico_max" in meta and valor > meta["critico_max"]:
        nivel    = NIVEL_CRITICO
        mensagem = f"{descricao} ACIMA do limite crítico ({meta['critico_max']} {unidade})!"
    elif "nominal_max" in meta and valor > meta["nominal_max"]:
        nivel    = NIVEL_ATENCAO
        mensagem = f"{descricao} acima do nominal ({meta['nominal_max']} {unidade}) — monitorar."

    # Verifica threshold de mínimo (ex: sincronização baixa é ruim)
    elif "critico_min" in meta and valor < meta["critico_min"]:
        nivel    = NIVEL_CRITICO
        mensagem = f"{descricao} ABAIXO do limite crítico ({meta['critico_min']} {unidade})!"
    elif "nominal_min" in meta and valor < meta["nominal_min"]:
        nivel    = NIVEL_ATENCAO
        mensagem = f"{descricao} abaixo do nominal ({meta['nominal_min']} {unidade}) — monitorar."

    return {
        "nome":      nome,
        "descricao": descricao,
        "valor":     valor,
        "unidade":   unidade,
        "nivel":     nivel,
        "mensagem":  mensagem,
    }


def avaliar(dados: dict) -> dict:
    """
    Avalia todos os parâmetros de telemetria e retorna estrutura completa
    com alertas individuais, nível geral e respostas automatizadas.
    """
    alertas_individuais = []
    respostas_automatizadas = []

    for nome in LIMITES:
        valor = dados.get(nome)
        if valor is None:
            continue
        resultado = _avaliar_parametro(nome, valor)
        alertas_individuais.append(resultado)

    # ── Nível geral da missão ────────────────────────────────────────────
    criticos  = [a for a in alertas_individuais if a["nivel"] == NIVEL_CRITICO]
    atencoes  = [a for a in alertas_individuais if a["nivel"] == NIVEL_ATENCAO]

    if criticos:
        nivel_geral = NIVEL_CRITICO
    elif atencoes:
        nivel_geral = NIVEL_ATENCAO
    else:
        nivel_geral = NIVEL_OK

    # ── Respostas automatizadas (lógica em Python, não no prompt) ────────

    # 1. Margem de potência crítica → modo economia
    margem = dados.get("margem_potencia", 100.0)
    if margem < 20.0:
        respostas_automatizadas.append({
            "acao": "MODO_ECONOMIA_ATIVADO",
            "descricao": "Potência crítica ({:.1f}%). Transmissores auxiliares desligados. "
                         "Apenas sinal L1 ativo. Antenas redundantes em standby.".format(margem),
            "severidade": NIVEL_CRITICO,
        })

    # 2. Drift do oscilador crítico → correção de frequência
    drift = dados.get("drift_oscilador", 0.0)
    if drift > 5.0:
        respostas_automatizadas.append({
            "acao": "CORRECAO_OSCILADOR_INICIADA",
            "descricao": "Drift de {:.3f} ns/s detectado. Protocolo de re-sincronização "
                         "com relógio mestre da constelação iniciado automaticamente.".format(drift),
            "severidade": NIVEL_CRITICO,
        })

    # 3. Sincronização baixa → solicitação de uplink de correção
    sync = dados.get("sincronizacao_constelacao", 100.0)
    if sync < 70.0:
        respostas_automatizadas.append({
            "acao": "UPLINK_CORRECAO_SOLICITADO",
            "descricao": "Sincronização em {:.1f}%. Solicitação de pacote de correção "
                         "de efemérides ao segmento terrestre enviada.".format(sync),
            "severidade": NIVEL_CRITICO,
        })

    # 4. Temperatura payload crítica → redução de carga térmica
    temp = dados.get("temperatura_payload", 25.0)
    if temp > 65.0:
        respostas_automatizadas.append({
            "acao": "REDUCAO_CARGA_TERMICA",
            "descricao": "Temperatura em {:.1f}°C. Ciclo de dutycycle do payload reduzido "
                         "para 40%. Painéis de dissipação reorientados.".format(temp),
            "severidade": NIVEL_CRITICO,
        })

    # 5. Precisão de efeméride crítica → alerta para usuários terrestres
    efem = dados.get("precisao_efemeride", 0.0)
    if efem > 3.0:
        respostas_automatizadas.append({
            "acao": "ALERTA_DEGRADACAO_PRECISAO",
            "descricao": "Erro de efeméride em {:.3f} m. Frotas logísticas e sistemas "
                         "de precisão notificados: precisão do posicionamento degradada.".format(efem),
            "severidade": NIVEL_CRITICO,
        })

    # 6. Sinais L1/L5 críticos (ambos degradados) → failover
    l1 = dados.get("integridade_sinal_l1", 40.0)
    l5 = dados.get("integridade_sinal_l5", 38.0)
    if l1 < 25.0 and l5 < 22.0:
        respostas_automatizadas.append({
            "acao": "FAILOVER_SINAL_ATIVADO",
            "descricao": "Sinais L1 ({:.1f} dB-Hz) e L5 ({:.1f} dB-Hz) abaixo do crítico. "
                         "Roteamento para satélite de backup da constelação ativado.".format(l1, l5),
            "severidade": NIVEL_CRITICO,
        })

    return {
        "nivel_geral":            nivel_geral,
        "alertas":                alertas_individuais,
        "criticos":               criticos,
        "atencoes":               atencoes,
        "respostas_automatizadas": respostas_automatizadas,
        "timestamp":              dados.get("_timestamp", "N/A"),
        "ciclo":                  dados.get("_ciclo", 0),
    }


def resumo_alertas(resultado: dict) -> str:
    """
    Retorna string compacta com os alertas para injeção no prompt.
    """
    linhas = [f"NÍVEL GERAL: {resultado['nivel_geral']}"]

    if resultado["criticos"]:
        linhas.append("\n🔴 PARÂMETROS CRÍTICOS:")
        for a in resultado["criticos"]:
            linhas.append(f"  [{a['nivel']}] {a['mensagem']}")

    if resultado["atencoes"]:
        linhas.append("\n🟡 PARÂMETROS EM ATENÇÃO:")
        for a in resultado["atencoes"]:
            linhas.append(f"  [{a['nivel']}] {a['mensagem']}")

    if resultado["respostas_automatizadas"]:
        linhas.append("\n⚡ RESPOSTAS AUTOMATIZADAS ACIONADAS:")
        for r in resultado["respostas_automatizadas"]:
            linhas.append(f"  [{r['acao']}] {r['descricao']}")

    if not resultado["criticos"] and not resultado["atencoes"]:
        linhas.append("  ✅ Todos os parâmetros dentro dos limites nominais.")

    return "\n".join(linhas)
