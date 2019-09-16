from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from flags import APICommand, TokenAction
from JellyBotAPI.views.render import render_flag_table


class APIActionCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("API Command Code"), _("API Action"), APICommand)


class TokenActionCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Token Action Code"), _("Token Action"), TokenAction)
