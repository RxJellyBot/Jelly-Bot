from typing import List
import traceback

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from extutils.emailutils import MailSender
from extutils.utils import str_reduce_length
from flags import BotFeature, CommandScopeCollection, Execode, AutoReplyContentType, ExtraContentType
from models import AutoReplyModuleExecodeModel, AutoReplyContentModel
from models.utils import AutoReplyValidators
from mongodb.utils import CursorWithCount
from mongodb.factory import AutoReplyManager, ExecodeManager, ExtraContentManager
from mongodb.factory.results import WriteOutcome
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import HostUrl, Bot

from ._base_ import CommandNode

__all__ = ["cmd_main"]

# region Command Nodes
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
cmd_info = cmd_main.new_child_node(codes=["i", "info"])
cmd_rk = cmd_main.new_child_node(codes=["k", "rk", "rank", "ranking"])
# endregion


# region Add
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
            "Failed to construct an Auto-reply module using Execode.<br>"
            f"User ID: {e.user_model.id}<br>"
            f"Channel ID: {e.channel_oid}<br>"
            f"Execode: {excde_entry.execode}<br>"
            f"Exception: <pre>{traceback.format_exception(None, ex, ex.__traceback__)}</pre>",
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
    ret = []
    kw_type = AutoReplyContentType.determine(keyword)
    # Issue #124
    if not AutoReplyValidators.is_valid_content(kw_type, keyword, online_check=True):
        kw_type = AutoReplyContentType.TEXT
        ret.append(HandledMessageEventText(
            content=_("The type of the keyword has been automatically set to `TEXT` "
                      "because the validation was failed.")))

    resp_type = AutoReplyContentType.determine(response)
    # Issue #124
    if not AutoReplyValidators.is_valid_content(resp_type, response, online_check=True):
        resp_type = AutoReplyContentType.TEXT
        ret.append(HandledMessageEventText(
            content=_("The type of the response has been automatically set to `TEXT` "
                      "because the validation was failed.")))

    add_result = AutoReplyManager.add_conn_complete(
        keyword, kw_type, [AutoReplyContentModel(Content=response, ContentType=resp_type)],
        e.user_model.id, e.channel_oid,
        Bot.AutoReply.DefaultPinned, Bot.AutoReply.DefaultPrivate, Bot.AutoReply.DefaultTags,
        Bot.AutoReply.DefaultCooldownSecs)

    if add_result.outcome.is_success:
        ret.append(HandledMessageEventText(
            content=_(
                "Auto-Reply module successfully registered.\n"
                "Keyword Type: {}\n"
                "Response Type: {}").format(
                kw_type.key, resp_type.key),
            bypass_multiline_check=True))
    else:
        ret.append(HandledMessageEventText(
            content=_("Failed to register the Auto-Reply module.\n"
                      "Code: `{}`\n"
                      "Visit {} to see the code explanation.").format(
                add_result.outcome.code_str, f"{HostUrl}{reverse('page.doc.code.insert')}")))

    return ret
# endregion


# region Delete
@cmd_del.command_function(
    feature_flag=BotFeature.TXT_AR_DEL,
    arg_count=1,
    arg_help=[_("The keyword of the module to delete. Note that this also deletes the keyword which type is NOT text. "
                "For example, if there is a module which keyword 100(Text) and another module which keyword "
                "is 100(Sticker), both modules will be deleted if this argument is 100.")],
    scope=CommandScopeCollection.GROUP_ONLY
)
def delete_auto_reply_module(e: TextMessageEventObject, keyword: str):
    outcome = AutoReplyManager.del_conn(keyword, e.channel_oid, e.user_model.id)

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
# endregion


# region List / Query / Info / Ranking
def get_list_of_keyword_html(conn_list: CursorWithCount) -> List[str]:
    return [f"- {conn.keyword.content_html}<br>" for conn in conn_list]


@cmd_list.command_function(
    feature_flag=BotFeature.TXT_AR_LIST_USABLE,
    arg_count=0,
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def list_usable_auto_reply_module(e: TextMessageEventObject):
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid)

    if not conn_list.empty:
        ctnt = _("Usable Keywords ({}):").format(len(conn_list)) + \
            "\n\n" + \
            "<div class=\"ar-content\">" + "".join(get_list_of_keyword_html(conn_list)) + "</div>"

        return [HandledMessageEventText(content=ctnt, force_extra=True)]
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
def list_usable_auto_reply_module_keyword(e: TextMessageEventObject, keyword: str):
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid, keyword)

    if not conn_list.empty:
        ctnt = _("Usable Keywords ({}):").format(len(conn_list)) \
            + "\n\n" \
            + "<div class=\"ar-content\">" + "".join(get_list_of_keyword_html(conn_list)) + "</div>"

        return [HandledMessageEventText(content=ctnt, force_extra=True)]
    else:
        return [HandledMessageEventText(
            content=_("Cannot find any auto-reply module including the substring `{}` in their keyword.")
                .format(keyword))]


@cmd_info.command_function(
    feature_flag=BotFeature.TXT_AR_INFO,
    arg_count=1,
    arg_help=[_("The search keyword to find the Auto-Reply module. "
                "Auto-Reply module which keyword contains this will be returned.")],
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def auto_reply_module_detail(e: TextMessageEventObject, keyword: str):
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid, keyword)

    if not conn_list.empty:
        result = ExtraContentManager.record_content(
            ExtraContentType.AUTO_REPLY_SEARCH, [module.id for module in conn_list],
            _("Auto-Reply module with keyword {} in {}").format(
                keyword, e.channel_model.get_channel_name(e.user_model.id)),
            channel_oid=e.channel_oid)

        if result.success:
            content = _("Visit {} to see the result.").format(result.url)
        else:
            content = _("Failed to record the result. ({})").format(result.outcome.code_str)
    else:
        content = _("Cannot find any auto-reply module including the substring `{}` in their keyword.").format(keyword)

    content += "\n"
    content += _("Visit {}{} for more completed module searching functionality. Login required.").format(
        HostUrl, reverse("page.ar.search.channel", kwargs={"channel_oid": e.channel_oid}))

    return [HandledMessageEventText(content=content)]


@cmd_rk.command_function(
    feature_flag=BotFeature.TXT_AR_RANKING,
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=120
)
def auto_reply_ranking(e: TextMessageEventObject):
    ret = [_("Auto-Reply TOP{} ranking").format(Bot.AutoReply.RankingMaxCount)]

    # Attach module stats section
    module_stats = list(AutoReplyManager.get_module_count_stats(e.channel_oid, Bot.AutoReply.RankingMaxCount))
    if module_stats:
        ret.append("")
        ret.append(_("# Module usage ranking"))

        for rank, module in module_stats:
            reduced_kw = str_reduce_length(str(module.keyword).replace("\n", "\\n"),
                                           Bot.AutoReply.RankingMaxContentLength)
            reduced_rs1 = str_reduce_length(str(module.responses[0]).replace("\n", "\\n"),
                                            Bot.AutoReply.RankingMaxContentLength)

            ret.append(
                f"#{rank} - {'' if module.active else '[X] '}"
                f"{reduced_kw} → {reduced_rs1} ({module.called_count})"
            )

    # Attach unique keyword stats section
    unique_kw = AutoReplyManager.get_unique_keyword_count_stats(e.channel_oid, Bot.AutoReply.RankingMaxCount)
    if unique_kw.data:
        ret.append("")
        ret.append(_("# Unique keyword ranking"))

        for data in unique_kw.data:
            ret.append(f"#{data.rank} - {data.word_str} ({data.count_usage})")

    # Attach external url section
    ret.append("")
    ret.append(_("For more ranking data, please visit {}{}.").format(
        HostUrl, reverse("page.ar.ranking.channel", kwargs={"channel_oid": e.channel_oid})
    ))

    if len(ret) > 1:
        return [HandledMessageEventText(content="\n".join([str(s) for s in ret]))]
    else:
        return [HandledMessageEventText(content=_("No ranking data available for now."))]
# endregion
