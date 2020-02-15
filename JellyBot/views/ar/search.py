from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext_lazy as _

from extutils import safe_cast
from mongodb.factory import AutoReplyManager, ProfileManager
from JellyBot.utils import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin, ChannelOidRequiredMixin
from JellyBot.views.render import render_template


class AutoReplySearchChannelView(ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)
        keyword = request.GET.get("w")
        active_only = safe_cast(request.GET.get("active_only"), bool)

        channel_data = self.get_channel_data(*args, **kwargs)

        return render_template(
            request, _("Auto-Reply search in {}").format(channel_data.model.id), "ar/search-channel.html",
            {
                "channel_name": channel_data.model.get_channel_name(get_root_oid(request)),
                "channel_oid": channel_data.model.id,
                "module_list": AutoReplyManager.get_conn_list(channel_data.model.id, keyword, active_only),
                "active_only": active_only
            }, nav_param=kwargs)


class AutoReplySearchChannelListView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)

        return render_template(
            request, _("Auto-Reply search channel list"), "ar/search-list.html",
            {
                "channel_list": ProfileManager.get_user_channel_profiles(
                    root_uid, inside_only=True, accessbible_only=True)
            }, nav_param=kwargs)
