class CountryUtils:
    @staticmethod
    def get_pib(country: []):
        try:
            val = int(float(country.get('pib', 0)))
        except (ValueError, TypeError):
            val = 0
        return f"{val:,}".replace(",", ".")

    @staticmethod
    def get_pop(country: []):
        try:
            val = int(float(country.get('pop_est', 0)))
        except (ValueError, TypeError):
            val = 0
        return f"{val:,}".replace(",", ".")
