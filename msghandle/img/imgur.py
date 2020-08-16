from typing import List

from django.utils.translation import gettext_lazy as _

from extutils import exec_timing_result
from extutils.imgproc import ImgurClient
from flags import ChannelType, BotFeature, Platform
from mongodb.factory import BotFeatureUsageDataManager
from msghandle.models import HandledMessageEvent, HandledMessageEventText, ImageMessageEventObject


def process_imgur_upload(e: ImageMessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_type == ChannelType.PRIVATE_TEXT:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.IMG_IMGUR_UPLOAD, e.channel_oid, e.user_model.id)

        # Using the key of `e.content.content_type` because it's a directly-used-parameter to upload the image
        exec_result = exec_timing_result(ImgurClient.upload_image, e.content.content, e.content.content_type.key)
        upload_result = exec_result.return_

        if upload_result.success:
            ret = [
                HandledMessageEventText(
                    content=_("Uploaded to imgur.com\n\n"
                              "Time consumed: *{:.2f} ms*\n"
                              "Link to the image below.").format(exec_result.execution_ms),
                    bypass_multiline_check=True)
            ]

            if e.channel_model.platform == Platform.DISCORD:
                # Using markdown because Discord automatically transform the image URL to be an image message
                ret.append(HandledMessageEventText(content=f"`{upload_result.link}`"))
            else:
                ret.append(HandledMessageEventText(content=upload_result.link))

            return ret
        else:
            return [
                HandledMessageEventText(
                    content=_("Image upload failed. Status Code: `{}`\nType: `{}`\nContent: {}").format(
                        upload_result.status, type(e.content.content), e.content.content
                    ),
                    bypass_multiline_check=True)
            ]
    else:
        return []
