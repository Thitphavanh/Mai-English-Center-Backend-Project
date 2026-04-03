from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allow dict[key] in templates: {{ my_dict|get_item:key }}"""
    return dictionary.get(key)

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0
