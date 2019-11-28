from concurrent.futures.thread import ThreadPoolExecutor
from typing import List
import traceback

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from extutils.emailutils import MailSender
from flags import BotFeature, CommandScopeCollection, Execode, AutoReplyContentType
from models import AutoReplyModuleExecodeModel
from mongodb.utils import CursorWithCount
from mongodb.factory import AutoReplyManager, AutoReplyContentManager, ExecodeManager
from mongodb.factory.results import WriteOutcome
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import HostUrl, Bot

from ._base_ import CommandNode

__all__ = ["cmd_main"]

# ------------- Command Nodes

# ----- New

cmd_main = CommandNode(
    codes=["ar", "auto"], order_idx=0, name=_("Auto Reply"),
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
cmd_list = cmd_main.new_child_node(codes=["q", "query", "l", "list"])


# ----------------------- Add


@cmd_add.command_function(
    feature_flag=BotFeature.TXT_AR_ADD_EXECODE,
    arg_count=1,
    arg_help=[
        _("The Execode obtained else where to complete the auto-reply module registration.")
    ],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_auto_reply_module_execode(e: TextMessageEventObject, execode: str) -> List[HandledMessageEventText]:
    get_excde_result = ExecodeManager.get_execode_entry(execode, Execode.AR_ADD)

    if not get_excde_result.success:
        return [
            HandledMessageEventText(content=_(
                "Failed to get the Execode data using the Execode `{}`. Code: `{}`"
            ).format(execode, get_excde_result.outcome))
        ]

    excde_entry = get_excde_result.model

    if e.user_model.id != excde_entry.creator_oid:
        return [
            HandledMessageEventText(content=_(
                "The ID of the creator of this Execode: `{}` does not match your ID: `{}`.\n"
                "Only the creator of this Execode can complete this action."
            ).format(excde_entry.creator_oid, e.user_model.id))
        ]

    try:
        ar_model = AutoReplyModuleExecodeModel(**excde_entry.data, from_db=True).to_actual_model(
            e.channel_oid, excde_entry.creator_oid)
    except Exception as ex:
        MailSender.send_email_async(
            "Failed to construct an Auto-reply module using Execode.\n"
            f"User ID: {e.user_model.id}\n"
            f"Channel ID: {e.channel_oid}\n"
            f"Execode: {excde_entry.execode}\n"
            f"Exception: {traceback.format_exception(None, ex, ex.__traceback__)}",
            subject="Failed to construct AR module")

        return [HandledMessageEventText(content=_(
            "Failed to create auto-reply module. An error report was sent for investigation."))]

    add_result = AutoReplyManager.add_conn_by_model(ar_model)

    if not add_result.success:
        MailSender.send_email_async(
            "Failed to register an Auto-reply module using model.\n"
            f"User ID: {e.user_model.id}\n"
            f"Channel ID: {e.channel_oid}\n"
            f"Execode: {excde_entry.execode}\n"
            f"Add result json: {add_result.serialize()}",
            subject="Failed to construct AR module")

        return [HandledMessageEventText(content=_(
            "Failed to register the auto-reply module. Code: `{}`"
        ).format(add_result.outcome))]

    ExecodeManager.remove_execode(execode)

    return [HandledMessageEventText(content=_("Auto-reply module registered."))]


@cmd_add.command_function(
    feature_flag=BotFeature.TXT_AR_ADD,
    arg_count=2,
    arg_help=[
        _("The message for the auto-reply module to be triggered.\n\n"
          "If the content **is number**, the content type will be **LINE sticker**.\n\n"
          "Otherwise, the content type will be **text**."),
        _("The message for the auto-reply module to respond when triggered.<hr>"
          "If the content **is number**, the content type will be **LINE sticker**.\n\n"
          "If the content **endswith .jpg**, the content type will be **image**.\n\n"
          "Otherwise, the content type will be **text**.<hr>"
          "Notes:\n\n"
          "- For content **endswith .jpg** - "
          "Please ensure that the URL is an image when you open it, **NOT** a webpage. "
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
            content=_("Failed to fetch the content ID of the **response**.\n"
                      "Auto-Reply module not registered.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                rep_ctnt_result.outcome, f"{HostUrl}{reverse('page.doc.code.get')}"))]

    add_result = AutoReplyManager.add_conn_complete(
        kw_ctnt_result.model.id, (rep_ctnt_result.model.id,), e.user_model.id, e.channel_oid,
        Bot.AutoReply.DefaultPinned, Bot.AutoReply.DefaultPrivate, Bot.AutoReply.DefaultTags,
        Bot.AutoReply.DefaultCooldownSecs)

    if add_result.outcome.is_success:
        return [HandledMessageEventText(
            content=_(
                "Auto-Reply module successfully registered.\n"
                "Keyword Type: {}\n"
                "Response Type: {}").format(
                kw_ctnt_result.model.content_type.key, rep_ctnt_result.model.content_type.key),
            bypass_multiline_check=True)]
    else:
        return [
            HandledMessageEventText(
                content=_("Failed to register the Auto-Reply module.\n"
                          "Code: `{}`\n"
                          "Visit {} to see the code explanation.").format(
                    add_result.outcome.code_str, f"{HostUrl}{reverse('page.doc.code.insert')}"))]


# ----------------------- Delete


@cmd_del.command_function(
    feature_flag=BotFeature.TXT_AR_DEL,
    arg_count=1,
    arg_help=[_("The keyword of the module to delete.")],
    scope=CommandScopeCollection.GROUP_ONLY
)
def delete_auto_reply_module(e: TextMessageEventObject, keyword: str):
    kw_ctnt_result = AutoReplyContentManager.get_content(
        keyword, type_=AutoReplyContentType.TEXT, add_on_not_found=False)
    if not kw_ctnt_result.success:
        return [HandledMessageEventText(
            content=_("Failed to fetch the content ID of the **keyword**.\n"
                      "Auto-Reply module not deleted.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                kw_ctnt_result.outcome, f"{HostUrl}{reverse('page.doc.code.get')}"))]

    outcome = AutoReplyManager.del_conn(kw_ctnt_result.model.id, e.channel_oid, e.user_model.id)

    if outcome.is_success:
        return [HandledMessageEventText(content=_("Auto-Reply Module deleted.\nKeyword: {}").format(keyword))]
    elif outcome == WriteOutcome.X_INSUFFICIENT_PERMISSION:
        return [HandledMessageEventText(content=_("Insufficient Permission to delete the auto-reply module."))]
    elif outcome == WriteOutcome.X_NOT_FOUND:
        return [HandledMessageEventText(content=_("Auto-reply module of the keyword {} not found.").format(keyword))]
    else:
        return [
            HandledMessageEventText(
                content=_("Failed to delete the Auto-Reply module.\n"
                          "Code: {}\n"
                          "Visit {} to see the code explanation.").format(
                    outcome.code_str, f"{HostUrl}{reverse('page.doc.code.insert')}"))]


# ----------------------- List

def get_list_of_keyword(conn_list: CursorWithCount) -> List[str]:
    ret = []

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="ConnList") as executor:
        futures = []
        for conn in conn_list:
            futures.append(executor.submit(conn.get_keyword_repr_in_cmd))

        # Non-lock call & Free resources when execution is done
        executor.shutdown(False)

        for completed in futures:
            result = completed.result()
            if result:
                ret.append(result)

    return ret


@cmd_list.command_function(
    feature_flag=BotFeature.TXT_AR_LIST_USABLE,
    arg_count=0,
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def list_usable_auto_reply_module(e: TextMessageEventObject):
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid)

    if not conn_list.empty:
        return [HandledMessageEventText(
            content=_("Usable Keywords:") + "\n" + _(", ").join(get_list_of_keyword(conn_list))
        )]
    else:
        return [HandledMessageEventText(content=_("No usable auto-reply module in this channel."))]


@cmd_list.command_function(
    feature_flag=BotFeature.TXT_AR_LIST_KEYWORD,
    arg_count=1,
    arg_help=[_("The search keyword to find the Auto-Reply module. "
                "Auto-Reply module which keyword contains this will be returned.")],
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def list_usable_auto_reply_module(e: TextMessageEventObject, keyword: str):
    ctnt_mdls = AutoReplyContentManager.get_contents_by_word(keyword)

    if ctnt_mdls.empty:
        return [HandledMessageEventText(
            content=_("No content including the substring \"{}\" was found.").format(keyword))]

    conn_list = AutoReplyManager.get_conn_list(e.channel_oid, [ctnt.id for ctnt in ctnt_mdls])

    if not conn_list.empty:
        return [HandledMessageEventText(
            content=_("Usable Keywords:") + "\n" + _(", ").join(get_list_of_keyword(conn_list))
        )]
    else:
        return [HandledMessageEventText(
            content=_("Cannot find any auto-reply module including the substring `{}` in their keyword."))]
