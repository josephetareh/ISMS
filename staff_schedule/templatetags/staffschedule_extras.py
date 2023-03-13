from datetime import timedelta

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


@register.filter
def get_clock_in_opening(shift_start_time):
    return shift_start_time - timedelta(minutes=40)


@register.filter
def subtract(first_value, second_value):
    return first_value - second_value


@register.filter
def one_return_test(counter_value):
    print(counter_value)
    # print("hi", counter_value.split("input"))
    return 0


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name="previous_day")
def previous_day(date):
    return date - timedelta(days=1)


@register.filter(name="next_day")
def next_day(date):
    return date + timedelta(days=1)

# @register.filter(name='get_group')
# def user_group(user):
#     if user.groups:
#         return user.groups.values_list('name', flat=True)
#     else:
#         return None
