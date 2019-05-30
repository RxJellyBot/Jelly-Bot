from django.views import View
from django.views.decorators.csrf import csrf_exempt


class CsrfExemptMixin(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
