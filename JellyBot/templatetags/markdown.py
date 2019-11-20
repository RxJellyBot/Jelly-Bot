from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from markdown2 import Markdown

register = template.Library()

md_proc = Markdown(extras=["fenced-code-blocks"])


@register.filter(is_safe=True)
@stringfilter
@mark_safe
def markdown(text):
    """Use markdown2 to convert the markdown text."""
    text = md_proc.convert(text)
    return text
