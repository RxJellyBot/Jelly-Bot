# noqa
from django.http import JsonResponse
from django.views import View

from JellyBot.keys import Session
from JellyBot.api.static import result


# DEPRECATE: Remove after API v1 deprecation
class CheckParameterMixin(View):  # noqa
    def mandatory_keys(self) -> set:
        return set()

    # noinspection PyAttributeOutsideInit
    def missing_keys(self, request):
        if hasattr(self, "ret"):
            ret = self.ret
        else:
            ret = self.ret = []

        q_dict = None

        if request.method == "GET":
            q_dict = request.GET
        elif request.method == "POST":
            q_dict = request.POST

        if q_dict is not None:
            for k in self.mandatory_keys():
                if k not in q_dict:
                    ret.append(k)

        return ret

    def render_on_missing_keys(self, missing_keys: list):
        self.request.session[Session.APIStatisticsCollection.DICT_RESPONSE] = {result.REQUIRED: missing_keys}
        return JsonResponse(self.request.session[Session.APIStatisticsCollection.DICT_RESPONSE])

    def dispatch(self, request, *args, **kwargs):
        missing_keys = self.missing_keys(request)

        if len(missing_keys) > 0:
            return self.render_on_missing_keys(missing_keys)
        else:
            return super().dispatch(request, *args, **kwargs)
