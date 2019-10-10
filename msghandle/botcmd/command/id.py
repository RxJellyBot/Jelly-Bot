from gettext import gettext as _
from msghandle.models import TextMessageEventObject

from ._base_ import CommandNode

cmd = CommandNode(
    ["id", "info"], 500, _("Information"),
    _("Check the information of various things (see the description section for more details)."))
cmd_me = cmd.new_child_node(["me", "my"])
cmd_ch = cmd.new_child_node(["ch", "channel"])


@cmd_me.command_function(description=_("Check the user info of self."))
def check_sender_identity(e: TextMessageEventObject):
    return _("User ID: `{}`").format(e.user_model.id)


@cmd_ch.command_function(description=_("Check the channel info."))
def check_channel_info(e: TextMessageEventObject):
    return _("Channel ID: `{}`\nChannel Token: `{}`").format(e.channel_model.id, e.channel_model.token)
