
def processar_crescimento_diario(country_info):
    """
    Processa o crescimento econômico e militar diário de todos os países.
    Deve ser chamado uma vez por dia no jogo.
    """
    
    # Fator de conversão PIB -> Militar Diário
    # Ajuste este valor para balancear a velocidade de crescimento
    # Considerando PIB na casa dos milhões/bilhões e Militar na casa dos milhares/milhões
    MILITARY_GROWTH_FACTOR = 0.000005 
    
    # Conjunto para rastrear países já processados neste turno (evitar duplicatas de MultiPolygon)
    processed_countries = set()

    for properties in country_info.values():
        country_name = properties.get('name')
        
        if country_name in processed_countries:
            continue
            
        processed_countries.add(country_name)
        
        # Obtém PIB e Militar atual
        pib = properties.get('pib', 0)
        militar_atual = properties.get('militar', 0)
        
        # Calcula crescimento
        # O crescimento é proporcional ao PIB
        crescimento = pib * MILITARY_GROWTH_FACTOR
        
        # Atualiza o valor
        properties['militar'] = militar_atual + crescimento

