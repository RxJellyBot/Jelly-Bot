from django.views import View

from JellyBotAPI import keys
from flags import APIAction


class APIStatisticsCollectMixin(View):
    def get_api_action(self):
        return APIAction.UNKNOWN

    def dispatch(self, request, *args, **kwargs):
        request.session[keys.APIStatisticsCollection.COLLECT] = True
        request.session[keys.APIStatisticsCollection.API_ACTION] = self.get_api_action()

        return super().dispatch(request, *args, **kwargs)
