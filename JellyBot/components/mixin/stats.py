from django.views import View

from JellyBot.keys import Session
from flags import APICommand


class APIStatisticsCollectMixin(View):
    def get_api_action(self):
        return APICommand.UNKNOWN

    def dispatch(self, request, *args, **kwargs):
        request.session[Session.APIStatisticsCollection.COLLECT] = True
        request.session[Session.APIStatisticsCollection.API_ACTION] = self.get_api_action()

        return super().dispatch(request, *args, **kwargs)
