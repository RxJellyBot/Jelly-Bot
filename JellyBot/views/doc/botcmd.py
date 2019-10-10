from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from flags import WebsiteError
from msghandle.botcmd.command import cmd_root
from JellyBot.views import WebsiteErrorView
from JellyBot.views.render import render_template


class BotCommandMainView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(
            request, _("Bot Commands List"), "doc/botcmd_main.html", {"cmd_nodes": cmd_root.child_nodes})


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