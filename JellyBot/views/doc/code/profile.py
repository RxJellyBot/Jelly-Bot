from django.views import View
from django.utils.translation import gettext_lazy as _

from flags import ProfilePermission
from JellyBot.views.render import render_flag_table


class ProfilePermissionCodeView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_flag_table(request, _("Profile Permission Code"), _("Profile Permission"), ProfilePermission)
