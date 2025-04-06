from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro para acessar valores de um dicionário usando uma chave.
    Uso: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key, 0)
