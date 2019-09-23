from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext_lazy as _

from mongodb.factory import ProfileManager
from flags import Platform, AutoReplyContentType, PermissionCategory
from JellyBot.sysconfig import AutoReply
from JellyBot.components import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin
from JellyBot.views.render import render_template


class AutoReplyAddView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)

        return render_template(request, _("Add an Auto-Reply"), "ar/add.html",
                               {
                                   "max_responses": AutoReply.MaxResponses,
                                   "max_length": AutoReply.MaxContentLength,
                                   "platform_list": list(Platform),
                                   "contenttype_list": list(AutoReplyContentType),
                                   "tag_splittor": AutoReply.TagSplittor,
                                   "user_ch_list": ProfileManager.get_user_channel_profiles(root_uid),
                                   "root_uid_str": str(root_uid),
                                   "perm_pin_access": PermissionCategory.AR_ACCESS_PINNED_MODULE.code_num
                               })
