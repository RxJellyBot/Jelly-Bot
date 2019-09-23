from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.views.render import render_template


class MainPageView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return render_template(request, _("Auto-Reply Home"), "ar/main.html")
