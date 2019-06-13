from django.views.generic.base import View
from django.utils.translation import gettext as _

from flags import APIAction, TokenAction
from JellyBotAPI.views.render import render_template


class APIActionCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/generic.html", {"title": _("API Action Code"),
                                                                  "table_title": _("API Action"),
                                                                  "flags": list(APIAction)})


class TokenActionCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/generic.html", {"title": _("Token Action Code"),
                                                                  "table_title": _("Token Action"),
                                                                  "flags": list(TokenAction)})
