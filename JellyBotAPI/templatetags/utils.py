from django import template

register = template.Library()


@register.simple_tag(name="join_extract")
def join_extract(arr, attr_str, join_str):
    """
    Join the `attr_str` of the element of the `arr` with `join_str`.
    """

    return join_str.join([getattr(item, attr_str) for item in arr])


@register.filter
def concat(str1, str2):
    """
    Concatenate two strings.
    """
    return str(str1) + str(str2)
