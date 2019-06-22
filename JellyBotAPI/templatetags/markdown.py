from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from markdown2 import Markdown

register = template.Library()

md_proc = Markdown()


@register.filter(is_safe=True)
@stringfilter
@mark_safe
def markdown(text):
    text = md_proc.convert(text)
    return text
