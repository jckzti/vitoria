class Formatters:
    @staticmethod
    def format_number(value):
        """Formata números com ponto a cada 3 casas decimais e remove decimais."""
        try:
            # Converte para float e depois int para remover decimais
            val_float = float(value)
            val_int = int(val_float)
            # Formata com separador de milhar (vírgula)
            formatted = f"{val_int:,}"
            # Troca vírgula por ponto (Padrão BR)
            return formatted.replace(",", ".")
        except (ValueError, TypeError):
            # Se falhar (ex: texto não numérico), retorna original tratando vírgulas
            return str(value).replace(",", ".")

    @staticmethod
    def get_pib_unity(value):
        """Retorna 'trilhões' ou 'bilhões' com base no valor."""
        # print(value)
        # print(Formatters.format_number(value))
        formatted = Formatters.format_number(value)
        return 'trilhões' if len(formatted) > 7 else 'bilhões'

