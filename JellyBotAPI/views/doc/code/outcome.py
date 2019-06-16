from django.views.generic.base import View
from django.utils.translation import gettext as _

from JellyBotAPI.views.render import render_flag_table
from mongodb.factory.results import InsertOutcome, GetOutcome, OperationOutcome, UpdateOutcome


class InsertOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Insert Outcome Code"), _("Insert Outcome"), InsertOutcome)


class GetOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Get Outcome Code"), _("Get Outcome"), GetOutcome)


class OperationOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Operation Outcome Code"), _("Operation Outcome"), OperationOutcome)


class UpdateOutcomeCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Update Outcome Code"), _("Update Outcome"), UpdateOutcome)
