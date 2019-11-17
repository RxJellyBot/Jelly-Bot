from typing import List

from django.urls import reverse

from extutils.utils import str_reduce_length
from flags import BotFeature, CommandScopeCollection
from mongodb.factory import AutoReplyManager, AutoReplyContentManager
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from msghandle.translation import gettext as _
from JellyBot.systemconfig import HostUrl, Bot

from ._base_ import CommandNode
from ._tree_ import cmd_trfm

__all__ = ["cmd_main", "cmd_old_add", "cmd_old_del"]

# ------------- Command Nodes

# ----- New

cmd_main = CommandNode(
    codes=["ar"], order_idx=0, name=_("Auto Reply"),
    brief_description=_("Perform operations related to the auto-reply feature."),
    description=_(
        "Perform operations related to the auto-reply feature.\n"
        "\n"
        "<hr>\n"
        "## ADD\n"
        "Register an auto-reply module which is 1 keyword to 1 response to the current channel.\n\n"
        "The content type for both keyword and the response will be automatically determined.\n\n"
        "To specify more properties of the module which the related controls are not implemented / allowed here, "
        "please use the website to register.<hr>"
        "The properties of the auto-reply module created here will be defaulted as below:\n\n"
        "- Pinned: `{}`\n\n"
        "- Private: `{}`\n\n"
        "- Tags: `{}`\n\n"
        "- Cooldown: `{}` secs").format(
        Bot.AutoReply.DefaultPinned, Bot.AutoReply.DefaultPrivate, Bot.AutoReply.DefaultTags,
        Bot.AutoReply.DefaultCooldownSecs)
)
cmd_add = cmd_main.new_child_node(codes=["a", "aa", "add"])
cmd_del = cmd_main.new_child_node(codes=["d", "del"])

# ----- Old

# DEPRECATE: Command Call - Auto Reply / Add
cmd_old_add = CommandNode(
    codes=["aa", "a", "add"], order_idx=50, name=_("Auto Reply - Add"),
    brief_description=_("**(DEPRECATING)**\n\n\n"
                        "Register an auto-reply module which is 1 keyword to 1 response to the current channel."),
    description=_(
        "### DEPRECATING, PLEASE CHECK THE DOCUMENTATION TO SEE HOW TO USE THE COMMAND IN THE FUTURE\n\n\n"
        "Register an auto-reply module which is 1 keyword to 1 response to the current channel.\n\n"
        "The content type for both keyword and the response will be automatically determined.\n\n"
        "To specify more properties of the module which the related controls are not implemented / allowed here, "
        "please use the website to register.<hr>"
        "The properties of the auto-reply module created here will be defaulted as below:\n\n"
        "- Pinned: `{}`\n\n"
        "- Private: `{}`\n\n"
        "- Tags: `{}`\n\n"
        "- Cooldown: `{}` secs").format(
        Bot.AutoReply.DefaultPinned, Bot.AutoReply.DefaultPrivate, Bot.AutoReply.DefaultTags,
        Bot.AutoReply.DefaultCooldownSecs))

# DEPRECATE: Command Call - Auto Reply / Delete
cmd_old_del = CommandNode(
    codes=["d", "del"], order_idx=60, name=_("Auto Reply - Delete"),
    brief_description=_("**(DEPRECATING)**\n\n\n"
                        "Delete a module in the current channel."),
    description=_(
        "### DEPRECATING, PLEASE CHECK THE DOCUMENTATION TO SEE HOW TO USE THE COMMAND IN THE FUTURE\n\n\n"
        "Deleted a module in the current channel."))


def _get_deprecating_msgs_() -> List[HandledMessageEventText]:
    return [HandledMessageEventText(
        content=_(
            "The way to use this command is deprecating. "
            "Please visit {} to see how to use the command in the future.").format(
            f"{HostUrl}{reverse('page.doc.botcmd.cmd', kwargs={'code': cmd_main.main_cmd_code})}"))]


# ------------- Main Functions


@cmd_old_add.command_function(
    feature_flag=BotFeature.TXT_AR_ADD,
    arg_count=2,
    arg_help=[
        _("The message for the auto-reply module to be triggered.\n\n"
          "If the content **is number**, the content type will be **LINE sticker**. "
          "Otherwise, the content type will be **text**."),
        _("The message for the auto-reply module to respond when triggered.<hr>"
          "If the content **is number**, the content type will be **LINE sticker**.\n\n"
          "If the content **endswith .jpg**, the content type will be **image**.\n\n"
          "Otherwise, the content type will be **text**.<hr>"
          "Notes:\n\n"
          "- For content **endswith .jpg** - "
          "Please ensure that the URL is an image when you open it, **NOT** a webpage. "
          "Otherwise, unexpected things may happen.\n"
          "- Please make sure that the newline **is escaped**, which means that the real newline characters are "
          "transformed to be \\n.\n\n"
          "Check the documentation of command code `{}` "
          "to see the convenience command to replace the newline character.").format(
            cmd_trfm.main_cmd_code
        )
    ],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_auto_reply_module_old(e: TextMessageEventObject, keyword: str, response: str) -> List[HandledMessageEventText]:
    ret = _get_deprecating_msgs_()
    ret.extend(add_auto_reply_module(e, keyword, response))

    return ret


@cmd_add.command_function(
    feature_flag=BotFeature.TXT_AR_ADD,
    arg_count=2,
    arg_help=[
        _("The message for the auto-reply module to be triggered.\n\n"
          "If the content **is number**, the content type will be **LINE sticker**.\n\n"
          "Otherwise, the content type will be **text**."),
        _("The message for the auto-reply module to respond when triggered.<hr>"
          "If the content **is number**, the content type will be **LINE sticker**.\n\n"
          "If the content **endswith .jpg**, the content type will be **image**."
          "Otherwise, the content type will be **text**.<hr>"
          "- For content **endswith .jpg**\n"
          "Please ensure that the URL is an image when you open it, **NOT** a webpage.\n"
          "Otherwise, unexpected things may happen.")
    ],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_auto_reply_module(e: TextMessageEventObject, keyword: str, response: str) -> List[HandledMessageEventText]:
    kw_ctnt_result = AutoReplyContentManager.get_content(keyword)
    if not kw_ctnt_result.success:
        return [HandledMessageEventText(
            content=_("Failed to fetch the content ID of the **keyword**.\n"
                      "Auto-Reply module not registered.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                kw_ctnt_result.outcome, f"{HostUrl}{reverse('page.doc.code.get')}"))]

    rep_ctnt_result = AutoReplyContentManager.get_content(response)
    if not rep_ctnt_result.success:
        return [HandledMessageEventText(
            content=_("Failed to fetch the content ID of the response.\n"
                      "Auto-Reply module not registered.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                rep_ctnt_result.outcome, f"{HostUrl}{reverse('page.doc.code.get')}"))]

    add_result = AutoReplyManager.add_conn(
        kw_ctnt_result.model.id, (rep_ctnt_result.model.id,), e.user_model.id, e.channel_oid,
        Bot.AutoReply.DefaultPinned, Bot.AutoReply.DefaultPrivate, Bot.AutoReply.DefaultTags,
        Bot.AutoReply.DefaultCooldownSecs)

    if add_result.success:
        kw_ctnt = str_reduce_length(kw_ctnt_result.model.content, Bot.AutoReply.MaxContentResultLength)
        rep_ctnt = str_reduce_length(rep_ctnt_result.model.content, Bot.AutoReply.MaxContentResultLength)

        return [HandledMessageEventText(
            content=_(
                "Auto-Reply module successfully registered.\n\n"
                "ID: `{}`\n"
                "Keyword: \n"
                "    Type: {}\n"
                "    Content: {}\n"
                "Response: \n"
                "    Type: {}\n"
                "    Content: {}\n").format(
                add_result.model.id,
                kw_ctnt_result.model.content_type.key, kw_ctnt,
                rep_ctnt_result.model.content_type.key, rep_ctnt),
            bypass_multiline_check=True)]
    else:
        return [
            HandledMessageEventText(
                content=_("Failed to register the Auto-Reply module.\n"
                          "Code: {}\n"
                          "Visit {} to see the code explanation.").format(
                    add_result.outcome.code_str, f"{HostUrl}{reverse('page.doc.code.insert')}"))]


@cmd_old_del.command_function(
    feature_flag=BotFeature.TXT_AR_DEL,
    arg_count=1,
    arg_help=[_("The keyword of the module to delete.")],
    scope=CommandScopeCollection.GROUP_ONLY
)
def delete_auto_reply_module_old(e: TextMessageEventObject, keyword: str):
    ret = _get_deprecating_msgs_()
    ret.extend(delete_auto_reply_module(e, keyword))

    return ret


@cmd_del.command_function(
    feature_flag=BotFeature.TXT_AR_DEL,
    arg_count=1,
    arg_help=[_("The keyword of the module to delete.")],
    scope=CommandScopeCollection.GROUP_ONLY
)
def delete_auto_reply_module(e: TextMessageEventObject, keyword: str):
    kw_ctnt_result = AutoReplyContentManager.get_content(keyword)
    if not kw_ctnt_result.success:
        return [HandledMessageEventText(
            content=_("Failed to fetch the content ID of the **keyword**.\n"
                      "Auto-Reply module not deleted.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                kw_ctnt_result.outcome, f"{HostUrl}{reverse('page.doc.code.get')}"))]

    outcome = AutoReplyManager.del_conn(kw_ctnt_result.model.id, e.channel_oid)

    if outcome.is_success:
        return [HandledMessageEventText(content=_("Auto-Reply Module deleted."))]
    else:
        return [
            HandledMessageEventText(
                content=_("Failed to delete the Auto-Reply module.\n"
                          "Code: {}\n"
                          "Visit {} to see the code explanation.").format(
                    outcome.code_str, f"{HostUrl}{reverse('page.doc.code.insert')}"))]
