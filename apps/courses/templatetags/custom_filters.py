from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split une chaîne par un délimiteur"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def strip_whitespace(value):
    """Supprime les espaces en début et fin"""
    if value:
        return value.strip()
    return value