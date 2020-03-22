from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext_lazy as _

from extutils import safe_cast
from mongodb.factory import AutoReplyManager, ProfileManager
from mongodb.helper import IdentitySearcher
from JellyBot.utils import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin, ChannelOidRequiredMixin
from JellyBot.views.render import render_template


class AutoReplySearchChannelView(LoginRequiredMixin, ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        keyword = request.GET.get("w")
        include_inactive = safe_cast(request.GET.get("include_inactive"), bool)

        channel_data = self.get_channel_data(*args, **kwargs)
        channel_name = channel_data.model.get_channel_name(get_root_oid(request))

        module_list = list(AutoReplyManager.get_conn_list(channel_data.model.id, keyword, not include_inactive))

        uids = []
        for module in module_list:
            uids.append(module.creator_oid)
            if not module.active and module.remover_oid:
                uids.append(module.remover_oid)

        username_dict = IdentitySearcher.get_batch_user_name(uids, channel_data.model, on_not_found="")

        return render_template(
            request, _("Auto-Reply search in {}").format(channel_name), "ar/search-main.html",
            {
                "channel_name": channel_name,
                "channel_oid": channel_data.model.id,
                "module_list": module_list,
                "username_dict": username_dict,
                "include_inactive": include_inactive,
                "keyword": keyword or ""
            }, nav_param=kwargs)


class AutoReplySearchChannelListView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)

        return render_template(
            request, _("Auto-Reply search channel list"), "ar/search-chlist.html",
            {
                "channel_list": ProfileManager.get_user_channel_profiles(
                    root_uid, inside_only=True, accessbible_only=True)
            }, nav_param=kwargs)
