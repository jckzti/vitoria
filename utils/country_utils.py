class CountryUtils:
    @staticmethod
    def get_pib(country: []):
        return f"{country['pib']:,}".replace(",", ".")

    @staticmethod
    def get_pop(country: []):
        return f"{country['pop_est']:,}".replace(",", ".")
