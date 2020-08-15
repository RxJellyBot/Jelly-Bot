"""
Module of the LINE sticker utilities.
"""
import atexit
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os
import shutil
import tempfile
from threading import Thread
from typing import Optional, BinaryIO, Dict, Union

import requests

from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware
from extutils.flags import FlagSingleEnum
from extutils.imgproc import apng2gif
from extutils.checker import arg_type_ensure
from JellyBot.systemconfig import ExtraService
from mixin import ClearableMixin

__all__ = ["LineStickerType", "LineStickerUtils", "LineAnimatedStickerDownloadResult"]

_temp_dir = tempfile.mkdtemp()  # Temporary directory for LINE stickers
atexit.register(shutil.rmtree, _temp_dir)  # Clear temporary directory on exit


@dataclass
class LineAnimatedStickerDownloadResult:
    """
    Download result of the animated sticker.
    """
    available: bool = False
    already_exists: bool = False

    conversion_result: Optional[apng2gif.ConvertResult] = None

    @property
    def succeed(self):
        """
        If the download succeed.

        :return: download succeed
        """
        return self.already_exists or (self.available and self.conversion_result and self.conversion_result.succeed)

    @property
    def time_spent(self) -> float:
        """
        Total time spent on the download.

        If the image is already downloaded (highly possibly because that it was being requested previously),
        ``self.conversion_result`` will be ``None`` (not converted), hence returning ``0``.

        Otherwise, it's the sum of durations of frame extraction + frame zipping (if requested)
        + image data collation + gif merging.

        :return: time spent on downloading in seconds
        """
        if not self.conversion_result:
            return 0

        return self.conversion_result.frame_extraction.duration \
               + self.conversion_result.frame_zipping.duration \
               + self.conversion_result.image_data_collation.duration \
               + self.conversion_result.gif_merging.duration  # noqa: E127


class LineStickerType(FlagSingleEnum):
    """
    :class:`FlagSingleEnum` indicating the type of the LINE sticker.
    """

    @classmethod
    def default(cls):
        return LineStickerType.STATIC

    ANIMATED = 0, _("Animated Sticker")
    SOUND = 1, _("Sticker with Sounds")
    STATIC = 2, _("Static Sticker")


class LineStickerTempStorageManager:
    """
    Class to manage the downloaded sticker files stored in the temporary storage.
    """
    _PATH_DICT: Dict[str, datetime] = {}

    _started = False

    @classmethod
    def start_monitor(cls):
        """
        Non-blocking call to let the temporary storage starts monitoring the file.

        Have no effect if the thread is already started.
        """
        if not cls._started:
            # Running the thread in daemon mode to prevent from unterminatable test
            Thread(target=cls._scan_file, name="LINE Sticker Temp File Manager", daemon=True).start()
            cls._started = True

    @classmethod
    def _scan_file(cls):
        while cls._PATH_DICT:
            cls._remove_expired_files()
            time.sleep(60)

        cls._started = False

    @classmethod
    def _remove_expired_files(cls):
        now = now_utc_aware()

        for path, last_used in cls._PATH_DICT.items():
            if (now - last_used).total_seconds() > ExtraService.Sticker.MaxStickerTempFileLifeSeconds:
                os.remove(path)

    @classmethod
    @arg_type_ensure
    def create_file(cls, file_path: str):
        """
        Update the last file usage time at ``file_path``.

        The file at ``file_path`` will be removed by calling ``os.remove()`` once
        :class:`ExtraService.Sticker.MaxStickerTempFileLifeSeconds` seconds has passed
        since the last call of this method.

        Timeout of the file will be reset upon re-calling this method if not yet expired.

        This call also starts the storage monitor if not yet started.

        :param file_path: actual file path
        """
        cls._PATH_DICT[file_path] = now_utc_aware()

        # On-demand monitor to save performance

        # `cls.start_monitor()` should located after the assignment of `cls._PATH_DICT`,
        # or the monitoring thread cannot start because of the while loop condition.
        if not cls._started:
            cls.start_monitor()

        # Trigger the check once
        cls._remove_expired_files()


class LineStickerUtils(ClearableMixin):
    """
    Main LINE sticker utilities.
    """

    # def get_pack_meta(self, pack_id: str):
    #     """
    #     :param pack_id: Numeric string of the sticker package ID.
    #     :type pack_id: str
    #     :return: LineStickerMetadata
    #     """
    #     pack_meta = requests.get(LineStickerUtils.get_meta_url(pack_id))
    #
    #     if pack_meta.status_code == 200:
    #         json_dict = json.loads(pack_meta.text)
    #         return LineStickerMetadata(json_dict)
    #     else:
    #         raise MetaDataNotFoundError(pack_meta.status_code)

    # pylint: disable=fixme

    # https://github.com/RaenonX/Jelly-Bot/issues/55

    # TODO: download sticker package as a whole
    #   and a command for it

    # TODO: A website page for downloading stickers
    #  (may need to use LINE sticker searching API by inspecting official page)

    @classmethod
    def clear(cls):
        for file_path in Path(_temp_dir).iterdir():
            if file_path.is_file():
                file_path.unlink()

    @staticmethod
    def is_sticker_exists(sticker_id: Union[int, str]) -> bool:
        """
        Check if the sticker with ``sticker_id`` exists by checking if the static URL of the sticker returns 200.

        :param sticker_id: ID of the sticker to be checked
        :return: if the sticker exists
        """
        response = requests.get(LineStickerUtils.get_sticker_url(sticker_id))

        return response.ok

    @staticmethod
    def get_meta_url(pack_id: Union[int, str]) -> str:
        """
        Get the sticker package metadata URL.

        :param pack_id: sticker package ID
        :return: sticker package metadata URL
        """
        return f"https://stickershop.line-scdn.net/products/0/0/1/{pack_id}/android/productInfo.meta"

    @staticmethod
    def get_sticker_url(sticker_id: Union[int, str]) -> str:
        """
        Get the sticker URL. This URL only returns the static image of the sticker, regardless its actual type.

        :param sticker_id: sticker ID
        :return: static sticker URL
        """
        return f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/android/sticker.png"

    @staticmethod
    def get_apng_url(pack_id: Union[int, str], sticker_id: Union[int, str]) -> str:
        """
        Get the animated sticker URL.

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :return: sticker URL
        """
        return f"https://sdl-stickershop.line.naver.jp/products/0/0/1/{pack_id}/android/animation/{sticker_id}.png"

    @staticmethod
    def get_sound_url(sticker_id: Union[int, str]) -> str:
        """
        Get the sticker sound URL.

        :param sticker_id: sticker ID
        :return: sticker sound URL
        """
        return f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/IOS/sticker_sound.m4a"

    @staticmethod
    def download_apng_as_gif(pack_id: Union[str, int], sticker_id: Union[str, int],
                             output_path: Optional[str] = None, *,
                             with_frames: bool = True) \
            -> LineAnimatedStickerDownloadResult:
        """
        Download animated sticker as gif.

        If ``output_path`` is ``None`` / not specified, the image will be stored to a temporary storage,
        which path can be acquired via ``get_downloaded_png()``.

        Files in the temporary storage will be automatically removed once it's created for
        :class:`ExtraService.Sticker.MaxStickerTempFileLifeSeconds` seconds.

        If ``output_path`` is specified, then the file will **NOT** be automatically removed.

        If there's a file already at ``output_path``, then it's considered as the sticker is downloaded.

        The above situation will not occur if the sticker does not exist.

        Returned :class:`LineAnimatedStickerDownloadResult` will indicate this situation if occurred.

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :param output_path: gif output path
        :param with_frames: if the extracted frames should be preserved
        :return: result of the download and conversion
        """
        result = LineAnimatedStickerDownloadResult()

        if not output_path:
            output_path = os.path.join(_temp_dir, f"{sticker_id}.gif")

            LineStickerTempStorageManager.create_file(output_path)

        # Check if the sticker exists
        response = requests.get(LineStickerUtils.get_apng_url(pack_id, sticker_id))
        if not response.ok:
            return result

        result.available = True

        # Check if the file exists
        frame_zip_path = f"{os.path.splitext(output_path)[0]}-frames.zip"

        if os.path.exists(output_path) and (not with_frames or os.path.exists(frame_zip_path)):
            result.already_exists = True
            return result

        # Download the sticker as apng and store it to a file
        apng_path = os.path.join(_temp_dir, f"{sticker_id}.png")
        with open(apng_path, "wb") as apng:
            apng.write(response.content)

        # Convert apng to gif
        result.conversion_result = apng2gif.convert(apng_path, output_path, zip_frames=with_frames)

        return result

    @staticmethod
    def get_downloaded_apng(pack_id: Union[str, int], sticker_id: Union[str, int], *,
                            with_frames: bool = True) \
            -> Optional[BinaryIO]:
        """
        Get the downloaded apng from the temporary storage as a :class:`BinaryIO` stream.

        If the image has not been downloaded, the utils will try to download it.

        If the download mentioned above fails, returns ``None``.

        -------

        Recommended example usage::

            with LineStickerUtils.get_downloaded_apng(1, 1) as f:
                # code

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :param with_frames: if the extracted frames should be preserved if file not ready
        :return: `BinaryIO` stream if found / downloaded
        """
        sticker_path = os.path.join(_temp_dir, f"{sticker_id}.gif")

        if not os.path.exists(sticker_path):
            result = LineStickerUtils.download_apng_as_gif(pack_id, sticker_id, with_frames=with_frames)

            if not result.available or not result.conversion_result.succeed:
                return None

        return open(sticker_path, "rb")

    @staticmethod
    def get_downloaded_apng_frames(pack_id: Union[str, int], sticker_id: Union[str, int]) -> Optional[BinaryIO]:
        """
        Get the downloaded apng from the temporary storage as a :class:`BinaryIO` stream.

        If the image has not been downloaded, the utils will try to download it.

        If the download mentioned above fails, returns ``None``.

        -------

        Recommended example usage::

            with LineStickerUtils.get_downloaded_apng(1, 1) as f:
                # code

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :return: `BinaryIO` stream if found / downloaded
        """
        zip_path = os.path.join(_temp_dir, f"{sticker_id}-frames.zip")

        if not os.path.exists(zip_path):
            result = LineStickerUtils.download_apng_as_gif(pack_id, sticker_id)

            if not result.available or not result.conversion_result.succeed:
                return None

        return open(zip_path, "rb")

# class LineStickerMetadata:
#     DEFAULT_LOCALE = "en"
#
#     def __init__(self, meta_dict):
#         self._dict = meta_dict
#
#     @property
#     def pack_id(self) -> int:
#         return int(self._dict["packageId"])
#
#     def get_title(self, locale=DEFAULT_LOCALE):
#         return self._get_localized_object("title", locale)
#
#     def get_author(self, locale=DEFAULT_LOCALE):
#         return self._get_localized_object("author", locale)
#
#     @property
#     def stickers(self) -> List[int]:
#         stk_obj = self._dict.get("stickers", [])
#         if len(stk_obj) > 0:
#             return [int(stk["id"]) for stk in stk_obj]
#         else:
#             return stk_obj
#
#     @property
#     def is_animated_sticker(self):
#         return self._dict.get("hasAnimation", False)
#
#     @property
#     def has_se(self):
#         return self._dict.get("hasSound", False)
#
#     def _get_localized_object(self, key, locale):
#         localized_object = self._dict.get(key)
#         if localized_object is not None:
#             localized_str_ret = localized_object.get(locale)
#
#             if localized_str_ret is None:
#                 return localized_object.get(LineStickerMetadata.DEFAULT_LOCALE)
#             else:
#                 return localized_str_ret
#         else:
#             return None
#
#
# class LinkStickerDownloadResult:
#     def __init__(self, compressed_file_path, sticker_ids, downloading_consumed_time, compression_consumed_time):
#         self._compressed_file_path = compressed_file_path
#         self._sticker_ids = sticker_ids
#         self._downloading_consumed_time = downloading_consumed_time
#         self._compression_consumed_time = compression_consumed_time
#
#     @property
#     def compressed_file_path(self):
#         """\
#         Returns:
#             Returns the path of compressed sticker package file in str.
#         """
#         return self._compressed_file_path
#
#     @property
#     def sticker_ids(self):
#         """\
#         Returns:
#             Returns id array (list(int)) of downloaded stickers.
#         """
#         return self._sticker_ids
#
#     @property
#     def sticker_count(self):
#         """\
#         Returns:
#             Returns count of downloaded stickers in int.
#         """
#         return len(self._sticker_ids)
#
#     @property
#     def downloading_consumed_time(self):
#         """\
#         Returns:
#             Returns time used in downloading (sec in float).
#         """
#         return self._downloading_consumed_time
#
#     @property
#     def compression_consumed_time(self):
#         """\
#         Returns:
#             Returns time used in compression (sec in float).
#         """
#         return self._compression_consumed_time
#
# class MetaDataNotFoundError(Exception):
#     def __init__(self, sticker_id: [int, str]):
#         super().__init__(f"Sticker metadata not found for ID #{sticker_id}")
