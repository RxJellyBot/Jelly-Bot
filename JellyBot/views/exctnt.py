from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.views.render import render_template
from mongodb.factory import ExtraContentManager


class ExtraContentView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, page_id, request, *args, **kwargs):
        page_content = ExtraContentManager.get_contents_condition(page_id)
        return render_template(request, _("Home Page"), "index.html")
