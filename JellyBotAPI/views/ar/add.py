from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext as _

from flags import Platform, AutoReplyContentType
from JellyBotAPI.SystemConfig import AutoReply
from JellyBotAPI.components.mixin import LoginRequiredMixin
from JellyBotAPI.views.render import render_template


class AutoReplyAddView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        return render_template(request, _("Add an Auto-Reply"), "ar/add.html",
                               {"max_responses": AutoReply.MAX_RESPONSES,
                                "max_length": AutoReply.MAX_CONTENT_LENGTH,
                                "platform_list": list(Platform),
                                "contenttype_list": list(AutoReplyContentType),
                                "tag_splittor": AutoReply.TAG_SPLITTOR})
