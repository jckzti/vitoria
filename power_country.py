import random


def generate_military_power(country: []):
    # Base inicial
    power = random.randint(10, 30)

    # Fatores de influência
    population = country["pop_est"]
    gdp = country["gdp_md"]

    # População influencia (mais população = mais soldados potenciais)
    if population > 100000000:  # +100 milhões
        power += 30
    elif population > 50000000:  # +50 milhões
        power += 20
    elif population > 10000000:  # +10 milhões
        power += 10

    # PIB influencia (mais dinheiro = melhor equipamento)
    power += int(gdp * 10)

    # Adicione alguns países com poder especial
    strong_countries = {
        "United States": 100,
        "Russia": 90,
        "China": 95,
        "India": 75,
        "United Kingdom": 70,
        "France": 70,
        "Germany": 65,
        "Japan": 60,
        "Brazil": 55,
        "South Korea": 65
    }

    if country["name"] in strong_countries:
        power = strong_countries[country["name"]]

    # Adicione um pouco de variação aleatória (±10%)
    power = int(power * (0.9 + random.random() * 0.2))

    return power / 100
