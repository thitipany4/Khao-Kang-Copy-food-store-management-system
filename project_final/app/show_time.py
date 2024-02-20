# In your app's templatetags directory, create a new Python file, e.g., custom_filters.py

from django import template

register = template.Library()

@register.filter(name='time_format')
def time_format(value):
    if value:
        return value.strftime('%H:%M น.')
    return ''
