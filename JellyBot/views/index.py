from django.views import View
from django.utils.translation import gettext_lazy as _

from JellyBot.utils import get_root_oid, msg_for_newly_created_account
from JellyBot.views.render import render_template


class HomePageView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        msg_for_newly_created_account(request, root_oid)

        return render_template(request, _("Home Page"), "index.html")
