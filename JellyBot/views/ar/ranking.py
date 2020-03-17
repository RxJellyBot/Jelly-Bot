from django.views.generic.base import View, TemplateResponseMixin
from django.utils.translation import gettext_lazy as _

from mongodb.factory import AutoReplyManager, ProfileManager
from JellyBot.systemconfig import Website
from JellyBot.utils import get_limit, get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin, ChannelOidRequiredMixin
from JellyBot.views.render import render_template


class AutoReplyRankingChannelView(ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        channel_data = self.get_channel_data(*args, **kwargs)

        limit = get_limit(request.GET, Website.AutoReply.RankingMaxCount)

        return render_template(
            request, _("Auto-Reply ranking in {}").format(channel_data.model.id), "ar/rk-channel.html",
            {
                "rk_module": AutoReplyManager.get_module_count_stats(channel_data.model.id, limit),
                "rk_ukw": AutoReplyManager.get_unique_keyword_count_stats(channel_data.model.id, limit),
                "channel_current": channel_data.model,
                "limit": limit,
                "max": Website.AutoReply.RankingMaxCount
            }, nav_param=kwargs)


class AutoReplyRankingChannelListView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic, PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_uid = get_root_oid(request)

        return render_template(
            request, _("Auto-Reply ranking channel list"), "ar/rk-list.html",
            {
                "channel_list": ProfileManager.get_user_channel_profiles(
                    root_uid, inside_only=True, accessbible_only=True)
            }, nav_param=kwargs)
