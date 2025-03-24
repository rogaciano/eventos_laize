from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def currency_br(value):
    """
    Formata um valor decimal para o formato de moeda brasileira (R$ 1.234,56)
    """
    if value is None:
        return "R$ 0,00"
    
    value = Decimal(str(value))
    
    # Formata o valor com duas casas decimais
    formatted_value = f"{value:.2f}".replace('.', ',')
    
    # Adiciona separador de milhares
    parts = formatted_value.split(',')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"
    
    # Adiciona pontos como separadores de milhar
    if len(integer_part) > 3:
        result = ""
        for i in range(len(integer_part) - 1, -1, -1):
            result = integer_part[i] + result
            if i > 0 and (len(integer_part) - i) % 3 == 0:
                result = "." + result
        integer_part = result
    
    return f"R$ {integer_part},{decimal_part}"
