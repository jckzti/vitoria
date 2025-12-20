import json
import os
import random

class GrowthSystem:
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join("data", "growth_rates.json")
        self.data_path = data_path
        self.growth_data = self.load_data()
        
    def load_data(self):
        """Carrega os dados de crescimento do arquivo JSON."""
        if not os.path.exists(self.data_path):
            print(f"DEBUG: Arquivo de crescimento não encontrado: {self.data_path}")
            return {}
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"DEBUG: Erro ao carregar growth_rates.json: {e}")
            return {}

    def get_country_rates(self, iso_code):
        """Retorna as taxas para um país específico ou o default."""
        iso_code = str(iso_code).lower()
        if iso_code in self.growth_data:
            return self.growth_data[iso_code]
        return self.growth_data.get("default", {
            "gdp_growth_mean": 2.0,
            "gdp_volatility": 1.0,
            "pop_growth_mean": 1.0,
            "pop_volatility": 0.2
        })

    def calculate_daily_factor(self, annual_rate_percent):
        """
        Converte uma taxa anual (%) em um fator diário multiplicativo.
        Fórmula de Juros Compostos: (1 + r)^(1/365)
        """
        rate_decimal = annual_rate_percent / 100.0
        # Evita log de número negativo ou zero complexo em casos extremos de colapso
        # Se a taxa for muito negativa (ex: -90%), limitamos para não quebrar a math
        if rate_decimal <= -1.0:
            rate_decimal = -0.99
            
        daily_factor = (1 + rate_decimal) ** (1/365.0)
        return daily_factor

    def process_daily_growth(self, country_properties):
        """
        Aplica o crescimento diário ao PIB e População de um país.
        Modifica o dicionário country_properties in-place.
        """
        # Tenta obter o código ISO (prioridade: iso_a2, wb_a2, adm0_a3...)
        iso = None
        for key in ['iso_a2', 'wb_a2', 'iso_a2_eh']:
            if key in country_properties and country_properties[key] not in [-99, "-99"]:
                iso = country_properties[key]
                break
        
        if not iso:
            # Se não tem ISO, usa default
            rates = self.growth_data.get("default")
        else:
            rates = self.get_country_rates(iso)
            
        # --- Cálculo do PIB ---
        # Adiciona aleatoriedade: Distribuição Normal ao redor da média
        # Volatilidade define o desvio padrão da variação DIÁRIA (ajustada)
        # Na verdade, aplicamos a volatilidade na taxa anual base para este "dia"
        
        current_gdp_mean = rates.get("gdp_growth_mean", 2.0)
        gdp_volatility = rates.get("gdp_volatility", 1.0)
        
        # Sorteia uma taxa anual para "hoje" baseada na média e volatilidade
        # Isso simula anos bons e ruins, ou dias de flutuação de mercado
        todays_annual_gdp_rate = random.gauss(current_gdp_mean, gdp_volatility)
        
        gdp_factor = self.calculate_daily_factor(todays_annual_gdp_rate)
        
        # Aplica ao PIB existente
        # Nota: gdp_md_est geralmente é em Milhões.
        # Atualizamos tanto 'gdp_md_est' (origem) quanto 'pib' (usado no jogo)
        current_gdp = 0
        if 'pib' in country_properties:
            current_gdp = float(country_properties['pib'])
        elif 'gdp_md_est' in country_properties:
            current_gdp = float(country_properties['gdp_md_est'])
            
        if current_gdp > 0:
            new_gdp = current_gdp * gdp_factor
            country_properties['pib'] = new_gdp
            if 'gdp_md_est' in country_properties:
                country_properties['gdp_md_est'] = new_gdp

        # --- Cálculo da População ---
        current_pop_mean = rates.get("pop_growth_mean", 1.0)
        pop_volatility = rates.get("pop_volatility", 0.2)
        
        todays_annual_pop_rate = random.gauss(current_pop_mean, pop_volatility)
        pop_factor = self.calculate_daily_factor(todays_annual_pop_rate)
        
        if 'pop_est' in country_properties:
            try:
                current_pop = float(country_properties['pop_est'])
                new_pop = current_pop * pop_factor
                country_properties['pop_est'] = int(new_pop) # População é inteira
            except (ValueError, TypeError):
                pass
                
        # --- Retorno opcional para debug ou UI ---
        return {
            "gdp_growth_today": todays_annual_gdp_rate,
            "pop_growth_today": todays_annual_pop_rate
        }

    def process_all_countries(self, country_info):
        """
        Itera sobre todos os países no country_info (lidando com duplicatas de polígonos)
        e aplica o crescimento diário.
        """
        processed_ids = set()
        
        for properties in country_info.values():
            # Tenta usar um ID único, fallback para nome
            c_id = properties.get('iso_a2', properties.get('name'))
            
            if c_id in processed_ids:
                continue
                
            processed_ids.add(c_id)
            self.process_daily_growth(properties)
