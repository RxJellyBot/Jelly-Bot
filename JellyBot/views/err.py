from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.views.render import render_template
from mongodb.factory import ExtraContentManager


class WebsiteErrorView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, code, *args, **kwargs):
        page_content = ExtraContentManager.get_content(page_id)
        d = {"page_id": page_id}
        if page_content:
            title = page_content.title if page_content.title != ExtraContentManager.DefaultTitle else page_id
            return render_template(request, _("Extra Content - {}").format(title), "exctnt.html", {
                "content": page_content.content_html,
                "expiry": page_content.expires_on
            }, nav_param=d)
        else:
            return render_template(request, _("Extra Content Not Found"), "err/unknown.html", {"err_code": code})
