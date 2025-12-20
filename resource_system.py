import json
import os


class ResourceSystem:
    def __init__(self):
        self.resources_def = {}
        self.country_data = {}
        self.load_data()

    def load_data(self):
        try:
            path = os.path.join("data", "country_data.json")
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                self.resources_def = data.get("resources", {})
                self.country_data = data.get("countries", {})
        except FileNotFoundError:
            print("Resource data file not found.")
        except Exception as e:
            print(f"Error loading resource data: {e}")

    def get_country_resources(self, country_name):
        """Retorna a lista de recursos de um país."""
        # Tenta nome exato
        if country_name in self.country_data:
            return self.country_data[country_name].get("resources", [])

        # Tenta mapear nomes comuns se não achar exato (ex: USA -> United States)
        # Por enquanto, simplificado
        return []

    def get_country_military_estimate(self, country_name):
        """Retorna a estimativa militar fixa se existir, senão None."""
        if country_name in self.country_data:
            return self.country_data[country_name].get("military_power")
        return None

    def calculate_resource_bonuses(self, resources_list):
        """Calcula os bônus totais baseado numa lista de recursos."""
        bonuses = {
            "military_mult": 1.0,
            "economy_mult": 1.0,
            "pop_growth_mult": 1.0
        }

        if not resources_list:
            return bonuses

        for res_id in resources_list:
            if res_id in self.resources_def:
                res_def = self.resources_def[res_id]
                b_type = res_def.get("bonus_type")
                b_val = res_def.get("bonus_value", 0)

                if b_type == "military":
                    bonuses["military_mult"] += b_val
                elif b_type == "economy":
                    bonuses["economy_mult"] += b_val
                elif b_type == "population":
                    bonuses["pop_growth_mult"] += b_val
                elif b_type == "military_special":
                    bonuses["military_mult"] += b_val # Treat as strong military bonus for now

        return bonuses

    def get_resource_icon(self, res_id):
        if res_id in self.resources_def:
            return self.resources_def[res_id].get("icon", "")
        return ""

    def get_resource_name(self, res_id):
        if res_id in self.resources_def:
            return self.resources_def[res_id].get("name", res_id)
        return res_id
