from typing import Optional

from bson import ObjectId
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.utils import get_root_oid
from JellyBot.views import render_template, WebsiteErrorView
from extutils import safe_cast
from flags import WebsiteError
from models import ChannelCollectionModel
from mongodb.factory import ChannelCollectionManager
from mongodb.helper import MessageStatsDataProcessor, InfoProcessor


class ChannelCollectionInfoView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # `kwargs` will be used as `nav_param` so extract chcoll_oid from `kwargs` instead of creating param.

        # `chcoll_oid` may be misformatted.
        # If so, `safe_cast` will yield `None` while the original parameter needs to be kept for the case of not found.
        chcoll_oid_str = kwargs.get("chcoll_oid", "")
        chcoll_oid = safe_cast(chcoll_oid_str, ObjectId)

        chcoll_data: Optional[ChannelCollectionModel] = ChannelCollectionManager.get_chcoll_oid(chcoll_oid)

        if not chcoll_data:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_COLLECTION_NOT_FOUND, {"chcoll_oid": chcoll_oid_str}, nav_param=kwargs)

        msgdata_1d = MessageStatsDataProcessor.get_user_chcoll_messages(chcoll_data, hours_within=24)
        msgdata_7d = MessageStatsDataProcessor.get_user_chcoll_messages(chcoll_data, hours_within=168)

        return render_template(
            self.request, _("Channel Collection Info - {}").format(chcoll_oid), "info/chcoll/main.html",
            {
                "chcoll_data": chcoll_data,
                "chcoll_cch_data":
                    InfoProcessor.collate_child_channel_data(get_root_oid(request), chcoll_data.child_channel_oids),
                "user_message_data1d": msgdata_1d,
                "user_message_data7d": msgdata_7d
            },
            nav_param=kwargs)
