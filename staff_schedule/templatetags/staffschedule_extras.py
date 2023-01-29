from django import template

register = template.Library()


@register.filter
def get_value_from_index(provided_deque, index_searching):
    return provided_deque[index_searching]


@register.filter
def get_date_as_string(provided_deque, index_searching):
    return provided_deque[index_searching][0]


@register.filter
def get_dict_value(dictionary, key):
    # use dictionary.get in this case because standard dictionary access will raise a KeyError if the key does not exist
    # in this case only None will be returned.
    return dictionary.get(key)