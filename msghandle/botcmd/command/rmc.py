from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from bot.rmc import RemoteControl
from flags import BotFeature, CommandScopeCollection
from JellyBot.systemconfig import Bot
from msghandle.models import TextMessageEventObject, HandledMessageEventText

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["rmc", "remote"], order_idx=800, name=_("Remote Control"),
    brief_description=_("Controls related to the remote control system."),
    description=_(
        "Controls related to the remote control system.\n\n"
        "- By activating this, the channel (source channel) where the user have any activites will "
        "be assumed that it is executed the designated channel (target channel).\n\n"
        "- Automatically deactivate when the source channel has idled for {} seconds.\n\n"
        "- These commands are only executable in private channels.\n\n"
        "- This **surpasses the scope limit** of the command.").format(
        Bot.RemoteControl.IdleDeactivateSeconds)
)

cmd_actv = cmd.new_child_node(codes=["a", "actv", "activate"])
cmd_dctv = cmd.new_child_node(codes=["d", "dctv", "deactivate"])
cmd_status = cmd.new_child_node(codes=["s", "cur", "status", "current"])


@cmd_actv.command_function(
    feature_flag=BotFeature.TXT_RMC_ACTIVATE,
    description=_("Target channel will be replaced if the system has already been activated."),
    arg_count=1,
    arg_help=[_("The ID of the remote control target channel.")],
    scope=CommandScopeCollection.PRIVATE_ONLY
)
def remote_control_activate(e: TextMessageEventObject, target_channel: ObjectId):
    activated = RemoteControl.activate(e.user_model, e.channel_model_source.id, target_channel)

    if activated:
        return [HandledMessageEventText(content=_("Remote control activated."))]
    else:
        return [HandledMessageEventText(content=_("Target channel not found. Failed to activate remote control."))]


@cmd_dctv.command_function(
    feature_flag=BotFeature.TXT_RMC_DEACTIVATE,
    scope=CommandScopeCollection.PRIVATE_ONLY
)
def remote_control_deactivate(e: TextMessageEventObject):
    RemoteControl.deactivate(e.user_model.id, e.channel_model_source.id)
    return [HandledMessageEventText(content=_("Remote control deactivated."))]


@cmd_status.command_function(
    feature_flag=BotFeature.TXT_RMC_STATUS,
    scope=CommandScopeCollection.PRIVATE_ONLY
)
def remote_control_status(e: TextMessageEventObject):
    current = RemoteControl.get_current(e.user_model.id, e.channel_model_source.id)

    if current:
        return [
            HandledMessageEventText(
                content=_("Remote control is activated.\n"
                          "Target Channel ID: `{}`\n"
                          "Target Channel Platform & Name: *{} / {}*\n"
                          "Will be deactivated at `{}`.").format(
                    current.target_channel.id, current.target_channel.platform.key,
                    current.target_channel.get_channel_name(e.user_model.id), current.expiry_str))
        ]
    else:
        return [HandledMessageEventText(content=_("Remote control is not activated."))]
