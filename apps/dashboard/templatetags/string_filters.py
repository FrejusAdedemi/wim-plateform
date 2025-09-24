# apps/dashboard/templatetags/string_filters.py

from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Divise une chaîne par un délimiteur"""
    try:
        return value.split(arg)
    except (AttributeError, TypeError):
        return []

@register.filter(name='join')
def join_list(value, arg):
    """Joint une liste avec un délimiteur"""
    try:
        return arg.join(value)
    except (AttributeError, TypeError):
        return value

@register.filter(name='first')
def first_item(value):
    """Retourne le premier élément d'une liste"""
    try:
        return value[0] if value else ""
    except (IndexError, TypeError):
        return ""

@register.filter(name='last')
def last_item(value):
    """Retourne le dernier élément d'une liste"""
    try:
        return value[-1] if value else ""
    except (IndexError, TypeError):
        return ""