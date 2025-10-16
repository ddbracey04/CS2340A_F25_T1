from django import template

register = template.Library()

@register.filter
def split(value, separator):
    # Split a string by separator
    return value.split(separator)

@register.filter
def lookup_index(lst, value):
    # Get the index of a value in a list
    try:
        return lst.index(value)
    except (ValueError, AttributeError):
        return -1