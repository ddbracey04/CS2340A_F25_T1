from django import template

register = template.Library()

@register.filter
def split(value, separator):
    # Split a string by separator
    if value:
        return value.split(separator)
    return []

@register.filter  
def strip(value):
    # Strip whitespace from string
    if value:
        return value.strip()
    return value