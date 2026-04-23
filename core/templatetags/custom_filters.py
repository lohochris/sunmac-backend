from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_range(value):
    """Return a range of numbers from 1 to value"""
    return range(1, value + 1)

@register.filter
def multiply(value, arg):
    """Multiply value by argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0