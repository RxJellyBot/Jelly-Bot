"""Entry point of the bot command ``JC AR`` - auto-reply."""
from typing import List

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from extutils.emailutils import MailSender
from extutils.utils import str_reduce_length
from flags import BotFeature, CommandScopeCollection, Execode, AutoReplyContentType, ExtraContentType
from models import AutoReplyContentModel, AutoReplyModuleModel
from models.utils import AutoReplyValidator
from mongodb.utils import ExtendedCursor
from mongodb.factory import AutoReplyManager, ExecodeManager, ExtraContentManager
from mongodb.factory.results import UpdateOutcome
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import HostUrl, Bot

from ._base import CommandNode

__all__ = ("CMD_MAIN",)

_description_str_dict = {
    "default_pinned": Bot.AutoReply.DefaultPinned,
    "default_private": Bot.AutoReply.DefaultPrivate,
    "default_tags": Bot.AutoReply.DefaultTags,
    "default_cd": Bot.AutoReply.DefaultCooldownSecs
}

# region Command Nodes
CMD_MAIN = CommandNode(
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
        "The default properties of a new auto-reply module are:\n\n"
        "- Pinned: `%(default_pinned)s`\n\n"
        "- Private: `%(default_private)s`\n\n"
        "- Tags: `%(default_tags)s`\n\n"
        "- Cooldown: `%(default_cd)d` secs") % _description_str_dict
)
CMD_ADD = CMD_MAIN.new_child_node(codes=["a", "aa", "add"])
CMD_DEL = CMD_MAIN.new_child_node(codes=["d", "del"])
CMD_LIST = CMD_MAIN.new_child_node(codes=["q", "query", "l", "list"])
CMD_INFO = CMD_MAIN.new_child_node(codes=["i", "info"])
CMD_RK = CMD_MAIN.new_child_node(codes=["k", "rk", "rank", "ranking"])


# endregion


# region Add
@CMD_ADD.command_function(
    feature=BotFeature.TXT_AR_ADD_EXECODE,
    arg_count=1,
    arg_help=[
        _("The Execode obtained else where to complete the auto-reply module registration.")
    ],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_auto_reply_module_execode(e: TextMessageEventObject, execode: str) -> List[HandledMessageEventText]:
    """
    Command to add an auto-reply module via Execode.

    :param e: message event that called this command
    :param execode: Execode to add the auto-reply module
    :return: if the auto-reply module is successfully registered
    """
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

    add_result = AutoReplyManager.add_conn(
        **excde_entry.data,
        **{AutoReplyModuleModel.ChannelOid.key: e.channel_oid,
           AutoReplyModuleModel.CreatorOid.key: excde_entry.creator_oid},
        from_db=True)

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


@CMD_ADD.command_function(
    feature=BotFeature.TXT_AR_ADD,
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
    """
    Command to add an auto-reply module with the provided ``keyword`` and ``response``.

    :param e: message event that called this command
    :param keyword: keyword of the new auto-reply module
    :param response: response of the new auto-reply module
    :return: if the auto-reply module was added successfully
    """
    ret = []

    def determine_type(content, error_text):
        type_ = AutoReplyContentType.determine(content)
        # https://github.com/RxJellyBot/Jelly-Bot/issues/124
        if not AutoReplyValidator.is_valid_content(type_, content):
            type_ = AutoReplyContentType.TEXT
            ret.append(HandledMessageEventText(content=error_text))

        return type_

    kw_type = determine_type(
        keyword,
        _("The type of the keyword has been automatically set to `TEXT` because the validation was failed."))
    resp_type = determine_type(
        response,
        _("The type of the response has been automatically set to `TEXT` because the validation was failed."))

    add_result = AutoReplyManager.add_conn(
        Keyword=AutoReplyContentModel(Content=keyword, ContentType=kw_type),
        Responses=[AutoReplyContentModel(Content=response, ContentType=resp_type)],
        ChannelOid=e.channel_oid, CreatorOid=e.user_model.id, Pinned=Bot.AutoReply.DefaultPinned,
        Private=Bot.AutoReply.DefaultPrivate, TagIds=Bot.AutoReply.DefaultTags,
        CooldownSec=Bot.AutoReply.DefaultCooldownSecs
    )

    if add_result.outcome.is_success:
        ret.append(HandledMessageEventText(
            content=_("Auto-Reply module successfully registered.\n"
                      "Keyword Type: %(kw_type)s\n"
                      "Response Type: %(resp_type)s") % {"kw_type": kw_type.key, "resp_type": resp_type.key},
            bypass_multiline_check=True))
    else:
        str_dict = {"outcome": add_result.outcome.code_str,
                    "url": f"{HostUrl}{reverse('page.doc.code.insert')}"}

        ret.append(HandledMessageEventText(
            content=_("Failed to register the Auto-Reply module.\n"
                      "Code: `%(outcome)s`\n"
                      "Visit %(url)s to see the code explanation.") % str_dict))

    return ret


# endregion


# region Delete
@CMD_DEL.command_function(
    feature=BotFeature.TXT_AR_DEL,
    arg_count=1,
    arg_help=[_("The keyword of the module to delete. Note that this also deletes the keyword which type is NOT text. "
                "For example, if there is a module which keyword 100(Text) and another module which keyword "
                "is 100(Sticker), both modules will be deleted if this argument is 100.")],
    scope=CommandScopeCollection.GROUP_ONLY
)
def delete_auto_reply_module(e: TextMessageEventObject, keyword: str):
    """
    Command to delete an auto-reply module which keyword is ``keyword``.

    :param e: message event object
    :param keyword: keyword of the module to be deleted
    """
    outcome = AutoReplyManager.del_conn(keyword, e.channel_oid, e.user_model.id)

    if outcome == UpdateOutcome.X_INSUFFICIENT_PERMISSION:
        return [HandledMessageEventText(content=_("Insufficient Permission to delete the auto-reply module."))]

    if outcome == UpdateOutcome.X_NOT_FOUND:
        return [HandledMessageEventText(
            content=_("Active auto-reply module of the keyword `%s` not found.") % keyword)]

    if not outcome.is_success:
        str_dict = {
            "code_str": outcome.code_str,
            "code_url": f"{HostUrl}{reverse('page.doc.code.insert')}"
        }

        return [HandledMessageEventText(content=_("Failed to delete the Auto-Reply module.\n"
                                                  "Code: {}\n"
                                                  "Visit {} to see the code explanation.") % str_dict)]

    return [HandledMessageEventText(content=_("Auto-Reply Module deleted.\nKeyword: %s") % keyword)]


# endregion


# region List / Query / Info / Ranking
def _get_list_of_keyword_html(conn_list: ExtendedCursor[AutoReplyModuleModel]) -> List[str]:
    return [f"- {conn.keyword.content_html}<br>" for conn in conn_list]


@CMD_LIST.command_function(
    feature=BotFeature.TXT_AR_LIST_USABLE,
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def list_usable_auto_reply_module(e: TextMessageEventObject):
    """
    Command to get the list of all usable auto-reply modules by providing the link to see the list.

    If there is no usable auto-reply modules, return a message indicating this instead.

    :param e: text message event
    :return: a link to the extra content page which contains the keywords of usable auto-reply modules
    """
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid)

    if conn_list.empty:
        return [HandledMessageEventText(content=_("No usable auto-reply module in this channel."))]

    ctnt = _("Usable Keywords ({}):").format(len(conn_list))
    ctnt += "\n\n<div class=\"ar-content\">" + "".join(_get_list_of_keyword_html(conn_list)) + "</div>"

    return [HandledMessageEventText(content=ctnt, force_extra=True)]


@CMD_LIST.command_function(
    feature=BotFeature.TXT_AR_LIST_KEYWORD,
    arg_count=1,
    arg_help=[_("The search keyword to find the Auto-Reply module. "
                "Auto-Reply module which keyword contains this will be returned.")],
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def list_usable_auto_reply_module_keyword(e: TextMessageEventObject, keyword: str):
    """
    Command to get the list of all auto-reply modules containing ``keyword`` by providing the link to see the list.

    If there is no auto-reply modules matching the condition, return a message indicating this instead.

    :param e: text message event
    :param keyword: keyword of the auto-reply module
    :return: a link to the extra content page
    """
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid, keyword)

    if conn_list.empty:
        return [HandledMessageEventText(
            content=_("Cannot find any auto-reply module with substring `%s` in their keyword.") % keyword)]

    ctnt = _("Usable Keywords ({}):").format(len(conn_list))
    ctnt += "\n\n<div class=\"ar-content\">" + "".join(_get_list_of_keyword_html(conn_list)) + "</div>"

    return [HandledMessageEventText(content=ctnt, force_extra=True)]


@CMD_INFO.command_function(
    feature=BotFeature.TXT_AR_INFO,
    arg_count=1,
    arg_help=[_("The search keyword to find the Auto-Reply module. "
                "Auto-Reply module which keyword contains this will be returned.")],
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=10
)
def auto_reply_module_detail(e: TextMessageEventObject, keyword: str):
    """
    Command to get the details of the auto-reply modules with ``keyword`` by providing the link to view it.

    :param e: text message event
    :param keyword: keyword of the auto-reply module
    :return: a link to the extra content page
    """
    conn_list = AutoReplyManager.get_conn_list(e.channel_oid, keyword)

    if not conn_list.empty:
        result = ExtraContentManager.record_content(
            ExtraContentType.AUTO_REPLY_SEARCH, e.channel_oid, [module.id for module in conn_list],
            _("Auto-Reply module with keyword {} in {}").format(
                keyword, e.channel_model.get_channel_name(e.user_model.id)))

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


@CMD_RK.command_function(
    feature=BotFeature.TXT_AR_RANKING,
    scope=CommandScopeCollection.GROUP_ONLY,
    cooldown_sec=120
)
def auto_reply_ranking(e: TextMessageEventObject):
    """
    Get the auto-reply module usage ranking.

    This command directly output the result instead of redirecting it to extra content page.

    :param e: text message event
    :return: auto-reply module usage ranking
    """
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

    if len(ret) == 1:
        return [HandledMessageEventText(content=_("No ranking data available for now."))]

    return [HandledMessageEventText(content="\n".join([str(s) for s in ret]))]
# endregion
