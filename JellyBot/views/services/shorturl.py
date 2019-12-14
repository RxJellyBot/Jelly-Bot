
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.components import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin
from JellyBot.views import render_template
from mongodb.factory import ShortUrlDataManager


class ShortUrlMainView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            self.request, _("Short URL Service"), "services/shorturl/main.html",
            {"records": ShortUrlDataManager.get_user_record(get_root_oid(request))})
