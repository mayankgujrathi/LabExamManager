from django import template

register = template.Library()

@register.filter
def getTheExamOnlyName(value):
    return value[5:]