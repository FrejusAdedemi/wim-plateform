from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    """Multiplie value par arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='div')
def divide(value, arg):
    """Divise value par arg"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='sub')
def subtract(value, arg):
    """Soustrait arg de value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='add_number')
def add_number(value, arg):
    """Additionne value et arg"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0