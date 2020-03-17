from django.views import View
from django.utils.translation import gettext_lazy as _

from extutils import char_description
from flags import WebsiteError
from msghandle.botcmd.command import cmd_root
from JellyBot.systemconfig import Bot
from JellyBot.views import WebsiteErrorView
from JellyBot.views.render import render_template


class BotCommandMainView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        cmd_splitters_html = "<b>"\
            + f"</b>&nbsp;{_('or')}&nbsp;<b>".join([str(char_description(spl)) for spl in cmd_root.splitters])\
            + "</b>"

        return render_template(
            request, _("Bot Commands List"), "doc/botcmd_main.html",
            {
                "cmd_prefix": cmd_root.prefix,
                "cmd_splitters_html": cmd_splitters_html,
                "cmd_nodes": cmd_root.child_nodes,
                "case_insensitive": cmd_root.case_insensitive,
                "case_insensitive_prefix": Bot.CaseInsensitivePrefix
            })


class BotCommandHelpView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, code, *args, **kwargs):
        node = cmd_root.get_child_node(code)
        if node:
            return render_template(
                request,
                _("Bot Command - {}").format(node.main_cmd_code), "doc/botcmd_node.html", {"cmd_node": node},
                nav_param={"code": code})
        else:
            return WebsiteErrorView.website_error(
                request, WebsiteError.BOT_CMD_NOT_FOUND, {"cmd_code": code}, nav_param={"code": code})
