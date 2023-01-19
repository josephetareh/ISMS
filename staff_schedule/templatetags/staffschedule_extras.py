from django import template

register = template.Library()


@register.filter
def get_value_from_index(provided_deque, index_searching):
    return provided_deque[index_searching]


@register.filter
def get_date_as_string(provided_deque, index_searching):
    return provided_deque[index_searching][0]