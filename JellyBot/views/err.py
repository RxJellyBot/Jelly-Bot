from django.utils.translation import gettext_lazy as _

from flags import WebsiteError
from JellyBot.views.render import render_template


class WebsiteErrorView:
    # noinspection PyArgumentList
    @staticmethod
    def website_error(request, code, ctxt, nav_param=None):
        if not nav_param:
            nav_param = {}

        d = {
            WebsiteError.EXTRA_CONTENT_NOT_FOUND:
                (_("Extra Content Not Found"), "err/exctnt_not_found.html"),
            WebsiteError.PROFILE_LINK_NOT_FOUND:
                (_("Profile Link Not Found"), "err/account/proflink_not_found.html"),
            WebsiteError.CHANNEL_NOT_FOUND:
                (_("Channel Data Not Found"), "err/info/channel_not_found.html"),
            WebsiteError.PROFILE_NOT_FOUND:
                (_("Profile Data Not Found"), "err/info/profile_not_found.html"),
            WebsiteError.CHANNEL_COLLECTION_NOT_FOUND:
                (_("Channel Collection Not Found"), "err/info/chcoll_not_found.html"),
            WebsiteError.BOT_CMD_NOT_FOUND:
                (_("Bot Command Not Found"), "err/doc/cmd_not_found.html"),
            WebsiteError.UNKNOWN:
                (_("Unknown"), "err/unknown.html")
        }

        label, template = d.get(WebsiteError(code), WebsiteError.UNKNOWN)

        return render_template(request, label, template, ctxt, nav_param=nav_param)
