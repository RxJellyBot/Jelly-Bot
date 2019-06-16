from django.http import JsonResponse
from django.views import View

from JellyBotAPI import keys
from JellyBotAPI.api.static import result


class CheckParameterMixin(View):
    def mandatory_keys(self) -> set:
        return set()

    # noinspection PyAttributeOutsideInit
    def lacking_keys(self, request):
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

    def render_on_lacking_keys(self, lacking_keys: list):
        self.request.session[keys.APIStatisticsCollection.DICT_RESPONSE] = {result.REQUIRED: lacking_keys}
        return JsonResponse(self.request.session[keys.APIStatisticsCollection.DICT_RESPONSE])

    def dispatch(self, request, *args, **kwargs):
        lack_keys = self.lacking_keys(request)

        if len(lack_keys) > 0:
            return self.render_on_lacking_keys(lack_keys)
        else:
            return super().dispatch(request, *args, **kwargs)
