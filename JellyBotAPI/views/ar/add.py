from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext as _

from mongodb.factory import ProfileManager
from flags import Platform, AutoReplyContentType, PermissionCategory
from JellyBotAPI.SystemConfig import AutoReply
from JellyBotAPI.components import get_root_oid
from JellyBotAPI.components.mixin import LoginRequiredMixin
from JellyBotAPI.views.render import render_template


class AutoReplyAddView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)

        return render_template(request, _("Add an Auto-Reply"), "ar/add.html",
                               {
                                   "max_responses": AutoReply.MAX_RESPONSES,
                                   "max_length": AutoReply.MAX_CONTENT_LENGTH,
                                   "platform_list": list(Platform),
                                   "contenttype_list": list(AutoReplyContentType),
                                   "tag_splittor": AutoReply.TAG_SPLITTOR,
                                   "user_ch_list": ProfileManager.get_user_channel_profiles(root_uid),
                                   "root_uid_str": str(root_uid),
                                   "perm_pin_access": PermissionCategory.AR_ACCESS_PINNED_MODULE.code_num
                               })
