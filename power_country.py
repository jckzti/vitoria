import random
from resource_system import ResourceSystem

# Instância global para ser usada aqui
res_sys = ResourceSystem()

def generate_military_power(country: []):
    country_name = country.get("name")
    
    # 1. Verifica se tem poder pré-definido no JSON
    predefined_power = res_sys.get_country_military_estimate(country_name)
    
    # Mapeamento manual para nomes que podem diferir do GeoJSON vs nosso JSON
    if predefined_power is None:
        # Ex: "United States of America" no GeoJSON pode ser "United States" ou vice-versa
        aliases = {
            "United States of America": "United States",
            "United States": "United States of America"
        }
        if country_name in aliases:
            predefined_power = res_sys.get_country_military_estimate(aliases[country_name])

    if predefined_power is not None:
        # Aplica variação aleatória pequena (±5%) para não ficar estático sempre
        variation = 0.95 + random.random() * 0.10
        return int(predefined_power * variation)

    # 2. Cálculo baseado em PIB (Fallback)
    # A fórmula anterior estava dividindo por 10000 no final, resultando em números muito pequenos (ex: 0.005)
    # Vamos ajustar para uma escala compatível com os números do JSON (ex: 100k - 2M)
    
    gdp = country.get("gdp_md", 0) # PIB em milhões de USD
    pop = country.get("pop_est", 0)
    
    # Fórmula: Base + (PIB * Fator) + (Pop * Fator)
    # GDP MD é em milhões. Ex: Brasil ~1.8M (1.8 trilhões) -> gdp_md = 1800000 ? Não, gdp_md costuma ser em milhoes
    # No GeoJSON sample: Brasil gdp_md: 3248000 (3.2T PPP?)
    
    # Vamos assumir que gdp_md 1000 = 1 Bi
    # Um país médio com 500 Bi PIB teria gdp_md = 500,000
    # Queremos que isso resulte em ~100k de poder militar
    
    base_power = gdp * 0.2 # 500k * 0.2 = 100k
    
    # População ajuda um pouco
    pop_bonus = pop * 0.001 # 50M * 0.001 = 50k
    
    total_power = base_power + pop_bonus
    
    # Limites mínimos e aleatoriedade
    if total_power < 5000:
        total_power = 5000 # Mínimo para não ser 0
        
    variation = 0.8 + random.random() * 0.4 # ±20%
    return int(total_power * variation)
