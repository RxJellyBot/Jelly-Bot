from gettext import gettext as _
from typing import List

from extutils import exec_timing_result
from extutils.imgproc import ImgurClient
from flags import ChannelType, BotFeature
from mongodb.factory import BotFeatureUsageDataManager
from msghandle.models import HandledMessageEvent, HandledMessageEventText, ImageMessageEventObject


def process_imgur_upload(e: ImageMessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_type == ChannelType.PRIVATE_TEXT:
        BotFeatureUsageDataManager.record_usage(BotFeature.IMG_IMGUR_UPLOAD, e.channel_oid, e.user_model.id)

        exec_result = exec_timing_result(ImgurClient.upload_image, e.content.content, e.content.content_type)
        upload_result = exec_result.return_

        return [
            HandledMessageEventText(
                content=_(f"Uploaded to imgur.\n"
                          f"Time consumed: {exec_result.execution_ms:.2f} ms\n"
                          f"Link to the image below."),
                bypass_multiline_check=True),
            HandledMessageEventText(
                content=_(upload_result.link),
                bypass_multiline_check=True)
        ]
    else:
        return []
