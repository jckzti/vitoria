class Formatters:
    @staticmethod
    def format_number(value):
        """Formata números com ponto a cada 3 casas decimais."""
        return value.replace(",", ".")

    @staticmethod
    def get_pib_unity(value):
        """Retorna 'trilhões' ou 'bilhões' com base no valor."""
        # print(value)
        # print(Formatters.format_number(value))
        formatted = Formatters.format_number(value)
        return 'trilhões' if len(formatted) > 7 else 'bilhões'

