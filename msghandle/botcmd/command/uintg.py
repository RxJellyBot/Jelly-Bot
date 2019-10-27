from django.urls import reverse

from flags import TokenAction, CommandScopeCollection
from JellyBot.systemconfig import HostUrl
from msghandle.models import TextMessageEventObject
from msghandle.translation import gettext as _
from mongodb.factory import TokenActionManager

from ._base_ import CommandNode

cmd = CommandNode(
    ["uintg", "userintegrate"], 2000, _("User Integrate"), _("Controls related to user identity integration."))


@cmd.command_function(
    description=_("Issue a token for user identity integration."), scope=CommandScopeCollection.PRIVATE_ONLY)
def issue_token(e: TextMessageEventObject):
    result = TokenActionManager.enqueue_action(e.root_oid, TokenAction.INTEGRATE_USER_IDENTITY)
    if result.success:
        return _("User Identity Integration process started.\nToken: `{}`\nExpiry: `{}`\n\n"
                 "Please record the token and go to {}{} to complete the integration.").format(\
            result.token, result.expiry.strftime("%Y-%m-%d %H:%M:%S"), HostUrl, reverse("account.integrate")
        )
    else:
        return _("User Identity Integration process failed to start.\nResult: {}\nException: {}").format(
            result.outcome, result.exception)
