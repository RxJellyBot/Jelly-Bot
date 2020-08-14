from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse

from extutils.line_sticker import LineStickerUtils
from extutils.emailutils import MailSender
from flags import BotFeature
from JellyBot.systemconfig import HostUrl
from msghandle.models import TextMessageEventObject, HandledMessageEventText, HandledMessageEventImage

from ._base import CommandNode

cmd = CommandNode(
    codes=["stk", "sticker"], order_idx=350, name=_("LINE Sticker"),
    description=_("Utilities of LINE stickers."))


def _download_animated_failed(result, url_dict):
    content = None

    if not result.available:
        content = _("Sticker download failed.\n"
                    "Original sticker link: %(url_apng)s\n") % url_dict
    elif result.already_exists:
        content = _("Sticker already exists.\n"
                    "Original sticker link: %(url_apng)s\n") % url_dict
    elif not result.conversion_result.frame_extracted:
        ex = result.conversion_result.frame_extraction_exception

        content = _("Sticker frame extraction failed.\n"
                    "Exception: %(ex)s"
                    "Original sticker link: %(url_apng)s\n") % dict(url_dict, ex=ex)
    elif not result.conversion_result.image_data_acquired:
        content = _("Sticker image data acquisition failed.\n"
                    "Original sticker link: %(url_apng)s\n") % url_dict
    elif not result.conversion_result.gif_merged:
        content = _("Sticker frame merger failed.\n"
                    "Original sticker link: %(url_apng)s\n") % url_dict

    if not content:
        content = _("Failed to download animated sticker.\n"
                    "Original sticker link: %(url_apng)s\n"
                    "Download result: %s") % result

    MailSender.send_email_async(content, subject="Failed to download animated LINE sticker")

    return [HandledMessageEventText(content=content, bypass_multiline_check=True)]


def _download_animated(package_id: int, sticker_id: int, *, with_frames: bool = True):
    # Get `package_id` and `sticker_id` as `int` to ensure the user entered correct type of the parameter
    # and cast it to `str` here for later execution
    package_id, sticker_id = str(package_id), str(sticker_id)

    kwargs = {"pack_id": package_id, "sticker_id": sticker_id}

    url_dict = {
        "url_gif": f"{HostUrl}{reverse('service.linesticker.animated.gif', kwargs=kwargs)}",
        "url_frames": f"{HostUrl}{reverse('service.linesticker.animated.frames', kwargs=kwargs)}",
        "url_apng": f"{HostUrl}{reverse('service.linesticker.animated.apng', kwargs=kwargs)}",
    }

    result = LineStickerUtils.download_apng_as_gif(package_id, sticker_id, with_frames=with_frames)

    if not result.succeed:
        return _download_animated_failed(result, url_dict)

    str_dict = {"time_spent": result.time_spent}
    str_dict.update(**url_dict)
    str_dict["frame_str"] = f"Frames: {url_dict['url_frames']}\n" if with_frames else ""

    return [
        HandledMessageEventText(
            content=_(
                "GIF: %(url_gif)s\n"
                "%(frame_str)s"
                "APNG: %(url_apng)s\n"
                "\n"
                "Time spent: %(time_spent).3f secs") % str_dict,
            bypass_multiline_check=True
        ),
        HandledMessageEventImage(LineStickerUtils.get_sticker_url(sticker_id))
    ]


# noinspection PyUnusedLocal
@cmd.command_function(
    feature=BotFeature.TXT_LINE_DISP_STATIC,
    arg_count=1,
    arg_help=[
        _("ID of the **sticker**.")
    ]
)
def display_static(e: TextMessageEventObject, sticker_id: int):
    return [HandledMessageEventImage(LineStickerUtils.get_sticker_url(sticker_id))]


# noinspection PyUnusedLocal
@cmd.command_function(
    feature=BotFeature.TXT_LINE_DL_ANIMATED,
    description=_("This command **does not** download apng frames."),
    arg_count=2,
    arg_help=[
        _("ID of the sticker **package**."),
        _("ID of the **sticker**.")
    ]
)
def download_animated(e: TextMessageEventObject, package_id: int, sticker_id: int):
    return _download_animated(package_id, sticker_id, with_frames=False)


# noinspection PyUnusedLocal
@cmd.command_function(
    feature=BotFeature.TXT_LINE_DL_ANIMATED,
    description=_("This command **downloads** apng frames."),
    arg_count=3,
    arg_help=[
        _("ID of the sticker **package**."),
        _("ID of the **sticker**."),
        _("Dummy argument. Input of this argument have no difference on the command outcome.")
    ]
)
def download_animated_with_frames(e: TextMessageEventObject, package_id: int, sticker_id: int, _: str):
    return _download_animated(package_id, sticker_id)
