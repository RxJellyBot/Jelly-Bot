from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from bot.markdown import markdown as md_object

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
@mark_safe
def markdown(text):
    """Use markdown2 to convert the markdown text."""
    return md_object.convert(text)
