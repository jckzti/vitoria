import random

def iniciar_guerra(atacante, defensor):
    """Inicia uma guerra entre dois paises que dura vários turnos."""
    # Cria um objeto de guerra que será armazenado e atualizado
    guerra = {
        "atacante": atacante["name"],
        "defensor": defensor["name"],
        "forca_atacante": atacante["militar"],
        "forca_defensora": defensor["militar"],
        "turno_atual": 1,
        "max_turnos": 5,  # Limite de turnos para a guerra
        "log_guerra": [],
        "em_andamento": True
    }

    # Adiciona log inicial
    guerra["log_guerra"].append(f"Guerra iniciada: {atacante['name']} vs {defensor['name']}")
    return guerra


def calcular_turno_guerra(guerra, paises):
    """Calcula um turno da guerra."""
    if not guerra["em_andamento"]:
        return

    atacante = None
    defensor = None

    # Encontra os paises pelos nomes
    for nome, propriedades in paises.items():
        if propriedades["name"] == guerra["atacante"]:
            atacante = propriedades
        elif propriedades["name"] == guerra["defensor"]:
            defensor = propriedades

    if not atacante or not defensor:
        guerra["em_andamento"] = False
        guerra["log_guerra"].append("Guerra encerrada: país não encontrado")
        return

    # Calcular forcas com um pouco de aleatoriedade
    forca_ataque = guerra["forca_atacante"] * (0.8 + random.random() * 0.4)  # 80-120%
    forca_defesa = guerra["forca_defensora"] * (1.0 + random.random() * 0.5)  # 100-150%, defensor tem vantagem

    # Calcular prejuizos
    prejuizo_atacante = max(5, int(guerra["forca_defensora"] * 0.1 * random.random()))
    prejuizo_defensor = max(5, int(guerra["forca_atacante"] * 0.15 * random.random()))

    # Vantagem para o atacante se tiver muito mais forca
    if guerra["forca_atacante"] > guerra["forca_defensora"] * 2:
        prejuizo_defensor *= 1.5

    # Atualizar forcas
    guerra["forca_atacante"] -= prejuizo_atacante
    guerra["forca_defensora"] -= prejuizo_defensor

    # Atualizar paises
    atacante["militar"] = max(0, int(guerra["forca_atacante"]))
    defensor["militar"] = max(0, int(guerra["forca_defensora"]))

    # Verificar se alguém se rendeu
    if guerra["forca_defensora"] < guerra["forca_atacante"] * 0.3:
        guerra["em_andamento"] = False
        guerra["log_guerra"].append(f"Turno {guerra['turno_atual']}: {defensor['name']} se rendeu!")

        # Transferir recursos
        pib_transferido = defensor["pib"] * 0.4
        territorios_transferidos = defensor["territorios"]

        atacante["pib"] += pib_transferido
        atacante["territorios"] += territorios_transferidos
        atacante['militar'] += defensor["militar"] * 0.2

        defensor["pib"] -= pib_transferido
        defensor["territorios"] = 0
        defensor["color"] = atacante["color"]  # País conquistado

        return f"{defensor['name']} se rendeu para {atacante['name']}! Território anexado."

    # Verificar se o atacante desistiu
    if guerra["forca_atacante"] < guerra["forca_defensora"] * 0.2:
        guerra["em_andamento"] = False
        guerra["log_guerra"].append(f"Turno {guerra['turno_atual']}: {atacante['name']} recuou!")

        # Penalidade para o atacante
        atacante["pib"] -= atacante["pib"] * 0.1
        atacante["militar"] -= atacante["militar"] * 0.1

        return f"{atacante['name']} recuou da invasão a {defensor['name']}!"

    # Avançar turno
    guerra["turno_atual"] += 1

    # Verificar se a guerra chegou ao limite de turnos
    if guerra["turno_atual"] > guerra["max_turnos"]:
        guerra["em_andamento"] = False
        guerra["log_guerra"].append(f"A guerra terminou após {guerra['max_turnos']} turnos")

        # Determinar vencedor pelo poder militar restante
        if guerra["forca_atacante"] > guerra["forca_defensora"]:
            # Ganhos parciais para o atacante
            pib_transferido = defensor["pib"] * 0.2
            territorios_transferidos = int(defensor["territorios"] * 0.3)

            atacante["pib"] += pib_transferido
            atacante["territorios"] += territorios_transferidos

            defensor["pib"] -= pib_transferido
            defensor["territorios"] -= territorios_transferidos

            return f"Vitória de {atacante['name']} após uma guerra prolongada!"
        else:
            return f"{defensor['name']} defendeu seu território com sucesso!"

    # Retornar log do turno atual
    log = f"Turno {guerra['turno_atual'] - 1}: {atacante['name']} {prejuizo_atacante} perdas, {defensor['name']} {prejuizo_defensor} perdas"
    guerra["log_guerra"].append(log)
    return log
