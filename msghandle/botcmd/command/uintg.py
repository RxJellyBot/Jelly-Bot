from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from flags import Execode, CommandScopeCollection, BotFeature
from JellyBot.systemconfig import HostUrl
from msghandle.models import TextMessageEventObject
from mongodb.factory import ExecodeManager

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["uintg", "userintegrate"], order_idx=2000, name=_("User Data Integration"),
    description=_("Controls related to user data integration."))


@cmd.command_function(
    feature_flag=BotFeature.TXT_FN_UDI_START, scope=CommandScopeCollection.PRIVATE_ONLY)
def issue_execode(e: TextMessageEventObject):
    result = ExecodeManager.enqueue_execode(e.root_oid, Execode.INTEGRATE_USER_DATA)
    if result.success:
        return _("User Data Integration process started.\nExecode: `{}`\nExpiry: `{}`\n\n"
                 "Please record the Execode and go to {}{} to complete the integration.").format(
            result.execode, result.expiry.strftime("%Y-%m-%d %H:%M:%S"), HostUrl, reverse("account.integrate")
        )
    else:
        return _("User Data Integration process failed to start.\nResult: {}\nException: {}").format(
            result.outcome, result.exception)
