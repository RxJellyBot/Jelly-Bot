from django import template

register = template.Library()


@register.simple_tag
def join_extract(arr, attr_str, join_str):
    """Join the ``attr_str`` of the element of the ``arr`` with ``join_str``."""

    return join_str.join([str(getattr(item, attr_str)) for item in arr])


@register.filter
def concat(str1, str2):
    """Concatenate two strings."""
    return str(str1) + str(str2)


@register.filter
def get_val(dict_: dict, key):
    return dict_.get(key, "")


# modified from https://stackoverflow.com/a/28513600/11571888
@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)
