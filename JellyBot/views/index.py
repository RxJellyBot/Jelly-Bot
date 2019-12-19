from datetime import timedelta

from django.views.generic.base import View
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware
from JellyBot.systemconfig import Website, HostUrl
from JellyBot.utils import get_root_oid
from JellyBot.views.render import render_template
from msghandle.botcmd.command import cmd_uintg


class HomePageView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        if root_oid and now_utc_aware() - root_oid.generation_time < timedelta(days=Website.NewRegisterThresholdDays):
            messages.info(
                request,
                _('Newly registered? Visit <a href="{}{}">this page</a> to know '
                  'how to integrate your LINE / Discord account!').format(
                    HostUrl, reverse("page.doc.botcmd.cmd", kwargs={"code": cmd_uintg.main_cmd_code})),
                extra_tags="safe"
            )

        return render_template(request, _("Home Page"), "index.html")
