from django.views.generic.base import View
from django.utils.translation import gettext as _

from JellyBotAPI.views.render import render_template


class HomePageView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return render_template(request, "index.html", {"title": _("Home Page")})
