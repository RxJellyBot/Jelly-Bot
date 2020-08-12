from datetime import timedelta
from typing import Optional

from bson import ObjectId
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware
from JellyBot.systemconfig import Website, HostUrl
from msghandle.botcmd.command import cmd_uintg

__all__ = ["msg_for_newly_created_account"]

_KEY_NEW_ACCOUNT = "new-account"


def _msg_queued(request, key: str):
    return bool([msg.message for msg in list(messages.get_messages(request)) if key in msg.level_tag])


def msg_for_newly_created_account(request, root_oid: Optional[ObjectId]):
    if _msg_queued(request, _KEY_NEW_ACCOUNT):
        return

    if root_oid and now_utc_aware() - root_oid.generation_time < timedelta(days=Website.NewRegisterThresholdDays):
        str_dict = {
            "cmd": cmd_uintg.get_usage(),
            "url1": HostUrl,
            "url2": reverse("account.integrate")
        }

        messages.info(
            request,
            _('Thanks for using JellyBot! Enter <code>%(cmd)s</code> to get a code, '
              'then paste it in <a href="%(url1)s%(url2)s">this page</a> '
              'to unlock the power of the bot!') % str_dict,
            extra_tags=f"safe {_KEY_NEW_ACCOUNT}"
        )
