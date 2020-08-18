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

cmd_anim = cmd.new_child_node(codes=["a", "anim", "animated"])
cmd_sttc = cmd.new_child_node(codes=["s", "static"])
cmd_pack = cmd.new_child_node(codes=["p", "pack", "package"])


# region Download Package


def _download_package_failed(result, url_dict):
    content = None

    if not result.available:
        content = _("Sticker package not found.\n"
                    "LINE STORE Link: %(url_store)s") % url_dict
    elif not result.download_succeed:
        str_dict = dict(url_dict, missed_stkids=", ".join([str(sid) for sid in result.missed_sticker_ids]))

        content = _("Failed to download some (or all) stickers.\n"
                    "LINE STORE Link: %(url_store)s\n"
                    "ID of the stickers not downloaded: %(missed_stkids)s") % str_dict
    elif not result.zip_succeed:
        str_dict = dict(url_dict, missed_stkids=", ".join([str(sid) for sid in result.not_zipped_ids]))

        content = _("Failed to zip some (or all) stickers.\n"
                    "LINE STORE Link: %(url_store)s\n"
                    "ID of the stickers not zipped: %(missed_stkids)s") % str_dict

    if not content:
        content = _("Failed to download sticker package.\n"
                    "LINE STORE Link: %(url_store)s\n"
                    "Download result: %(result)s") % dict(url_dict, result=result)

    MailSender.send_email_async(content, subject="Failed to download LINE sticker package")

    return [HandledMessageEventText(content=content, bypass_multiline_check=True)]


@cmd_pack.command_function(
    feature=BotFeature.TXT_LINE_DL_PACKAGE,
    arg_count=1,
    arg_help=[
        _("ID of the **package** to be downloaded.")
    ]
)
def download_package(__: TextMessageEventObject, package_id: int):
    package_id = str(package_id)

    kwargs = {"pack_id": package_id}

    url_dict = {
        "url_zip": f"{HostUrl}{reverse('service.linesticker.pack', kwargs=kwargs)}",
        "url_store": LineStickerUtils.get_pack_store_url(package_id),
    }

    result = LineStickerUtils.download_sticker_pack(package_id)

    if not result.succeed:
        return _download_package_failed(result, url_dict)

    str_dict = {
        "stk_id": result.pack_meta.pack_id,
        "stk_title": result.pack_meta.get_title(),
        "stk_author": result.pack_meta.get_author(),
        "time_spent": result.time_spent
    }
    str_dict.update(**url_dict)

    return [
        HandledMessageEventText(
            content=_(
                "Please purchase the sticker package if you like it.\n"
                "\n"
                "Package ID: %(stk_id)s\n"
                "Title: %(stk_title)s\n"
                "Author: %(stk_author)s\n"
                "\n"
                "LINE Store URL: %(url_store)s\n"
                "Sticker zip file URL: %(url_zip)s\n"
                "\n"
                "Time spent: %(time_spent).3f secs") % str_dict,
            bypass_multiline_check=True
        )
    ]


def _download_animated_failed(result, url_dict):
    content = None

    if not result.available:
        content = _("Sticker download failed.\n"
                    "Original sticker link: %(url_apng)s") % url_dict
    elif not result.conversion_result.frame_extraction.success:
        ex = result.conversion_result.frame_extraction.exception

        content = _("Sticker frame extraction failed.\n"
                    "Exception: %(ex)s\n"
                    "Original sticker link: %(url_apng)s") % dict(url_dict, ex=ex)
    elif not result.conversion_result.image_data_collation.success:
        content = _("Sticker image data acquisition failed.\n"
                    "Original sticker link: %(url_apng)s") % url_dict
    elif not result.conversion_result.gif_merging.success:
        content = _("Sticker frame merger failed.\n"
                    "Original sticker link: %(url_apng)s") % url_dict

    if not content:
        content = _("Failed to download animated sticker.\n"
                    "Original sticker link: %(url_apng)s\n"
                    "Download result: %(result)s") % dict(url_dict, result=result)

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


# endregion


# region Display Static


@cmd_sttc.command_function(
    feature=BotFeature.TXT_LINE_DISP_STATIC,
    arg_count=1,
    arg_help=[
        _("ID of the **sticker**.")
    ]
)
def display_static(__: TextMessageEventObject, sticker_id: int):
    return [HandledMessageEventImage(LineStickerUtils.get_sticker_url(sticker_id))]


# endregion


# region Download Animated


@cmd_anim.command_function(
    feature=BotFeature.TXT_LINE_DL_ANIMATED,
    description=_("This command **does not** download apng frames."),
    arg_count=2,
    arg_help=[
        _("ID of the sticker **package**."),
        _("ID of the **sticker**.")
    ]
)
def download_animated(__: TextMessageEventObject, package_id: int, sticker_id: int):
    return _download_animated(package_id, sticker_id, with_frames=False)


@cmd_anim.command_function(
    feature=BotFeature.TXT_LINE_DL_ANIMATED,
    description=_("This command **downloads** apng frames."),
    arg_count=3,
    arg_help=[
        _("ID of the sticker **package**."),
        _("ID of the **sticker**."),
        _("Dummy argument. Input of this argument have no difference on the command outcome.")
    ]
)
def download_animated_with_frames(__: TextMessageEventObject, package_id: int, sticker_id: int, _: str):
    return _download_animated(package_id, sticker_id)

# endregion
