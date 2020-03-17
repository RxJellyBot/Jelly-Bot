from django.http import HttpResponse
from django.views import View


class TeapotView(View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=418)
