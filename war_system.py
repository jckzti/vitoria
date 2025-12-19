import random

# Constantes de Balanceamento
DEFENDER_BONUS_MULTIPLIER = 1.25  # +25% de eficiência defensiva (trincheiras, etc)
BASE_ATTRITION = 0.05  # 5% de perdas base por turno
GDP_QUALITY_FACTOR = 0.000001  # Fator de qualidade por PIB (ajustar conforme escala do PIB)
MIN_TROOPS_FOR_WAR = 100

def iniciar_guerra(atacante, defensor):
    """Inicia uma guerra entre dois paises."""
    guerra = {
        "atacante": atacante["name"],
        "defensor": defensor["name"],
        # Força inicial para referência
        "forca_inicial_atacante": atacante["militar"],
        "forca_inicial_defensora": defensor["militar"],
        "data_inicio": None, # Será preenchido pelo map.py com a data atual
        "dias_de_guerra": 0,
        "log_guerra": [],
        "em_andamento": True
    }

    guerra["log_guerra"].append(f"Guerra iniciada: {atacante['name']} vs {defensor['name']}")
    return guerra


def processar_dia_guerra(guerra, paises):
    """
    Processa um dia de combate.
    Retorna (mensagem_log, guerra_acabou, mudanca_de_cor)
    """
    if not guerra["em_andamento"]:
        return None, False, False

    atacante = None
    defensor = None

    # Encontra os paises atualizados
    for nome, propriedades in paises.items():
        if propriedades["name"] == guerra["atacante"]:
            atacante = propriedades
        elif propriedades["name"] == guerra["defensor"]:
            defensor = propriedades

    if not atacante or not defensor:
        guerra["em_andamento"] = False
        return "Erro: País não encontrado", True, False

    # 1. Cálculo de Eficiência Militar baseada no PIB (Qualidade do Equipamento)
    # Quanto maior o PIB per capita (ou total simplificado), menor a perda de tropas
    qualidade_atacante = 1.0 + (atacante.get("pib", 0) * GDP_QUALITY_FACTOR)
    qualidade_defensor = 1.0 + (defensor.get("pib", 0) * GDP_QUALITY_FACTOR)

    # 2. Fatores de Batalha (Random + Tamanho do Exército)
    # A força efetiva é a quantidade de soldados * qualidade
    forca_efetiva_atk = atacante["militar"] * qualidade_atacante
    forca_efetiva_def = defensor["militar"] * qualidade_defensor * DEFENDER_BONUS_MULTIPLIER
    
    # 3. Cálculo de Baixas (Attrition)
    # O dano causado é proporcional à força do inimigo
    # Random factor 0.8 a 1.2
    fator_sorte_atk = random.uniform(0.8, 1.2)
    fator_sorte_def = random.uniform(0.9, 1.3) # Defensor tem leve vantagem na sorte (terreno conhecido)

    # Perdas baseadas na força inimiga
    baixas_atacante = int((forca_efetiva_def * 0.002) * fator_sorte_def) # 0.2% da força inimiga mata suas tropas
    baixas_defensor = int((forca_efetiva_atk * 0.002) * fator_sorte_atk)

    # Aplica baixas (garantindo que não fique negativo)
    atacante["militar"] = max(0, atacante["militar"] - baixas_atacante)
    defensor["militar"] = max(0, defensor["militar"] - baixas_defensor)
    
    guerra["dias_de_guerra"] += 1
    
    # 4. Verificação de Aniquilação / Anexação
    # Se o defensor for aniquilado (ou cair abaixo de um limiar crítico irrelevante)
    if defensor["militar"] <= MIN_TROOPS_FOR_WAR:
        guerra["em_andamento"] = False
        
        # Lógica de Anexação:
        # "trazendo uma parte do seu pib, e 99% da sua população, contando que 1% vai fugir"
        
        pib_anexado = defensor["pib"] * 0.5 # Exemplo: 50% do PIB é capturado (infraestrutura, recursos)
        pop_anexada = int(defensor["pop_est"] * 0.99)
        pop_fugitiva = defensor["pop_est"] - pop_anexada
        
        atacante["pib"] += pib_anexado
        atacante["pop_est"] += pop_anexada
        atacante["territorios"] += defensor["territorios"]
        
        # O defensor deixa de existir como entidade soberana
        defensor["pib"] = 0
        defensor["pop_est"] = 0
        defensor["territorios"] = 0
        defensor["militar"] = 0
        defensor["color"] = atacante["color"]
        
        msg = f"{defensor['name']} foi completamente ANEXADO por {atacante['name']}! Exército aniquilado."
        guerra["log_guerra"].append(msg)
        return msg, True, True

    # Se o atacante for aniquilado
    elif atacante["militar"] <= MIN_TROOPS_FOR_WAR:
        guerra["em_andamento"] = False
        msg = f"A invasão de {atacante['name']} FALHOU! Seu exército foi destruído."
        guerra["log_guerra"].append(msg)
        return msg, True, False

    # Log diário (opcional, pode ser muito spam se for todo dia)
    # Vamos retornar log apenas a cada 7 dias ou se houver grandes perdas
    if guerra["dias_de_guerra"] % 7 == 0:
        return f"Dia {guerra['dias_de_guerra']}: Baixas - {atacante['name']}: {baixas_atacante}, {defensor['name']}: {baixas_defensor}", False, False
    
    return None, False, False
