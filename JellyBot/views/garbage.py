from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View


class TeapotView(View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        content = render_to_string("garbage/418.html")
        return HttpResponse(content=content, status=418)
