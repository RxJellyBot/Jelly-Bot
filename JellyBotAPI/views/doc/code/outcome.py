from django.views.generic.base import View
from django.utils.translation import gettext as _

from JellyBotAPI.views.render import render_template
from mongodb.factory import InsertOutcome, GetOutcome


class InsertOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/insert.html", {"title": _("Insert Outcome Code"),
                                                                 "flags": list(InsertOutcome)})


class GetOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/get.html", {"title": _("Get Outcome Code"),
                                                              "flags": list(GetOutcome)})
