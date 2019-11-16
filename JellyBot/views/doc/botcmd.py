from django.contrib import messages
from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from flags import WebsiteError
from msghandle.botcmd.command import cmd_root, cmd_root_old
from JellyBot.systemconfig import Bot, HostUrl
from JellyBot.views import WebsiteErrorView
from JellyBot.views.render import render_template


class BotCommandMainView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(
            request, _("Bot Commands List"), "doc/botcmd_main.html",
            {"cmd_nodes": cmd_root.child_nodes,
             "case_insensitive": cmd_root.case_insensitive,
             "case_insensitive_prefix": Bot.CaseInsensitivePrefix})


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


# DEPRECATE: Bot Command - Documentation Views


def _warn_deprecation_(request):
    messages.warning(
        request, _("This way of using the bot command is deprecating. "
                   "Please visit to see the usage of new command set.").format(
            f"{HostUrl}/{reverse('page.doc.botcmd.main')}"),
        extra_tags="warning")


class BotOldCommandMainView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        _warn_deprecation_(request)

        return render_template(
            request, _("Bot Commands List (Old, DEPRECATING)"), "doc/botcmd_main.html",
            {"cmd_nodes": cmd_root_old.child_nodes,
             "case_insensitive": cmd_root_old.case_insensitive,
             "case_insensitive_prefix": Bot.CaseInsensitivePrefix,
             "is_old": True})


class BotOldCommandHelpView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, code, *args, **kwargs):
        _warn_deprecation_(request)

        node = cmd_root_old.get_child_node(code)
        if node:
            return render_template(
                request,
                _("Bot Command - {} (DEPRECATING)").format(node.main_cmd_code),
                "doc/botcmd_node.html", {"cmd_node": node}, nav_param={"code": code})
        else:
            return WebsiteErrorView.website_error(
                request, WebsiteError.BOT_CMD_NOT_FOUND, {"cmd_code": code}, nav_param={"code": code})
