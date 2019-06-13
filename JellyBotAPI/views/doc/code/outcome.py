from django.views.generic.base import View
from django.utils.translation import gettext as _

from JellyBotAPI.views.render import render_template
from mongodb.factory.results import InsertOutcome, GetOutcome, OperationOutcome


class InsertOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/generic.html", {"title": _("Insert Outcome Code"),
                                                                  "table_title": _("Insert Outcome"),
                                                                  "flags": list(InsertOutcome)})


class GetOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/generic.html", {"title": _("Get Outcome Code"),
                                                                  "table_title": _("Get Outcome"),
                                                                  "flags": list(GetOutcome)})


class OperationOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, "doc/code/generic.html", {"title": _("Operation Outcome Code"),
                                                                  "table_title": _("Operation Outcome"),
                                                                  "flags": list(OperationOutcome)})
