"""Module of the LINE sticker utilities."""
import atexit
from abc import ABC
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import os
import shutil
import tempfile
from threading import Thread
import time
from typing import Optional, BinaryIO, Dict, Union, List, Tuple
from zipfile import ZipFile

import requests

from extutils.dt import now_utc_aware
from extutils.imgproc import apng2gif
from extutils.checker import arg_type_ensure
from JellyBot.systemconfig import ExtraService
from mixin import ClearableMixin

from .flag import LineStickerLanguage, LineStickerType
from .exception import MetadataNotFoundError

__all__ = ("LineStickerUtils", "LineAnimatedStickerDownloadResult",
           "LineStickerMetadata")

_temp_dir = tempfile.mkdtemp(prefix="jellybot-line-")  # Temporary directory for LINE stickers
atexit.register(shutil.rmtree, _temp_dir)  # Clear temporary directory on exit


# region For sticker downloading


class LineStickerDownloadResultBase(ABC):
    """Result of downloading a sticker."""

    def __init__(self, sticker_id: int):
        self._sticker_id: int = sticker_id
        self._available: bool = False
        self._already_exists: bool = False
        self._downloaded: bool = False
        self._download_duration: float = 0.0

    def set_available(self):
        """Indicate that the sticker is available."""
        self._available = True

    def set_already_exists(self):
        """Indicate that the sticker already exists."""
        self._already_exists = True

    def set_downloaded(self, duration: float):
        """Indicate that the sticker is downloaded with the downloading duration."""
        self._downloaded = True
        self._download_duration = duration

    @property
    def sticker_id(self) -> int:
        """
        Get the sticker ID for this download.

        :return: sticker ID for this download
        """
        return self._sticker_id

    @property
    def available(self) -> bool:
        """
        Check if the sticker is available.

        :return: if the sticker is available
        """
        return self._available

    @property
    def already_exists(self) -> bool:
        """
        Check if the sticker already exists.

        :return: if the sticker already exists
        """
        return self._already_exists

    @property
    def downloaded(self) -> bool:
        """
        Check if the sticker is downloaded.

        :return: if the sticker is downloaded
        """
        return self._downloaded

    @property
    def download_duration(self) -> float:
        """
        Get the download duration.

        :return: download duration.
        """
        return self._download_duration

    @property
    def succeed(self):
        """
        If the download succeed.

        :return: download succeed
        """
        return self._already_exists or (self._available and self._downloaded)

    @property
    def time_spent(self) -> float:
        """
        Total time spent on the download.

        :return: time spent on downloading in seconds
        """
        return self._download_duration


class LineStickerDownloadResult(LineStickerDownloadResultBase):
    """Base object of the LINE sticker download result."""


class LineAnimatedStickerDownloadResult(LineStickerDownloadResultBase):
    """Result of downloading an animated sticker."""

    def __init__(self, sticker_id: int):
        super().__init__(sticker_id)
        self._conversion_result: Optional[apng2gif.ConvertResult] = None

    def set_conversion_result(self, conversion_result: apng2gif.ConvertResult):
        """Indicate that the conversion is completed (not necessarily succeed)."""
        self._conversion_result = conversion_result

    @property
    def conversion_result(self) -> Optional[apng2gif.ConvertResult]:
        """
        Get the apng2gif conversion result.

        :return: gif conversion result
        """
        return self._conversion_result

    @property
    def succeed(self):
        if not super().succeed:
            return False

        if self.already_exists:
            return True

        return self.downloaded and self.conversion_result is not None and self.conversion_result.succeed

    @property
    def time_spent(self) -> float:
        """
        Total time spent on downloading and converting the sticker.

        If the image is already downloaded (highly possibly because that it was being requested previously),
        ``self.conversion_result`` will be ``None`` (not converted), hence returning ``0``.

        Otherwise, it's the sum of durations of frame extraction + frame zipping (if requested)
        + image data collation + gif merging.

        :return: time spent on downloading and converting in seconds
        """
        duration = super().time_spent

        if not self.conversion_result:
            return duration

        duration += self.conversion_result.frame_extraction.duration
        duration += self.conversion_result.frame_zipping.duration
        duration += self.conversion_result.image_data_collation.duration
        duration += self.conversion_result.gif_merging.duration

        return duration


class LineStickerTempStorageManager:
    """Class to manage the downloaded sticker files stored in the temporary storage."""

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


# endregion


# region For pack downloading


class LineStickerMetadata:
    """Wrapper class for the metadata of the LINE sticker."""

    def __init__(self, meta_dict: dict):
        self._dict = meta_dict

    @property
    def pack_id(self) -> int:
        """
        Get the sticker package ID.

        :return: sticker package ID
        """
        return self._dict["packageId"]

    def get_title(self, lang: Optional[LineStickerLanguage] = None):
        """
        Get the title of the sticker.

        :param lang: language to use to get the sticker title
        :return: name of the title in `lang`
        """
        return self._get_localized_object("title", lang)

    def get_author(self, lang: Optional[LineStickerLanguage] = None):
        """
        Get the author of the sticker.

        :param lang: language to use to get the author
        :return: name of the author in `lang`
        """
        return self._get_localized_object("author", lang)

    @property
    def sticker_ids(self) -> List[int]:
        """
        Get the list of sticker IDs.

        :return: list of sticker IDs
        """
        stk_obj = self._dict.get("stickers", [])
        if not stk_obj:
            return stk_obj

        return [stk["id"] for stk in stk_obj]

    @property
    def is_animated_sticker(self):
        """
        Check if the sticker set is animated.

        :return: if the sticker set is animated
        """
        return self._dict.get("hasAnimation", False)

    @property
    def has_sound(self):
        """
        Check if the sticker set has sounds.

        :return: if the sticker set has sounds
        """
        return self._dict.get("hasSound", False)

    def _get_localized_object(self, key, lang: Optional[LineStickerLanguage] = None):
        localized_object = self._dict.get(key)
        if not localized_object:
            return None

        language = lang.key if lang else LineStickerLanguage.default().key  # pylint: disable=no-member
        localized_str_ret = localized_object.get(language)

        if not localized_str_ret:
            default = localized_object.get(LineStickerLanguage.default().key)  # pylint: disable=no-member
            if not default:
                return localized_object.popitem()[1]

            return default

        return localized_str_ret


class LineStickerPackDownloadResult:
    # pylint: disable=too-many-instance-attributes
    """
    Result of downloading a sticker pack.

    Stickers downloaded will be marked downloaded first, then mark zipped, normally.
    """

    def __init__(self):
        self._pack_meta: Optional[LineStickerMetadata] = None

        self._available: bool = False
        self._get_meta_duration: float = 0.0

        self._already_exists: bool = False

        self._downloaded_id: List[int] = []
        self._not_downloaded_id: List[int] = []
        self._download_succeed: bool = False
        self._download_duration: bool = False

        self._zipped_id: List[int] = []
        self._not_zipped_id: List[int] = []
        self._zip_completed: bool = False
        self._zip_succeed: bool = False
        self._zip_duration: bool = False

    def set_exists(self):
        """Indicate that the sticker package is already exists."""
        self._already_exists = True

    def set_available(self, pack_meta: LineStickerMetadata, get_meta_duration: float):
        """
        Indicate that the sitcker package is available.

        :param pack_meta: sticker package metadata object
        :param get_meta_duration: time spent on checking and getting the sticker package metadata
        """
        self._pack_meta = pack_meta
        self._available = True
        self._get_meta_duration = get_meta_duration

    def set_sticker_downloaded(self, sticker_id: int):
        """
        Indicate that a sticker is downloaded (not yet zipped).

        :param sticker_id: ID of the sticker downloaded
        """
        self._downloaded_id.append(sticker_id)

    def set_sticker_zipped(self, sticker_id: int):
        """
        Indicate that a sticker is zipped.

        :param sticker_id: ID of the sticker zipped
        """
        self._zipped_id.append(sticker_id)

    def set_download_completed(self, duration: float):
        """
        Indicate that all stickers are downloaded.

        :param duration: time spent on downloading all stickers
        """
        self._not_downloaded_id = list(set(self._pack_meta.sticker_ids).difference(self._downloaded_id))
        self._download_succeed = True
        self._download_succeed = len(self._not_downloaded_id) == 0
        self._download_duration = duration

    def set_zip_completed(self, duration: float):
        """
        Indicate that all stickers are zipped.

        :param duration: time spent on zipping all stickers
        """
        self._not_zipped_id = list(set(self._downloaded_id).difference(self._zipped_id))
        self._zip_completed = True
        self._zip_succeed = len(self._not_zipped_id) == 0
        self._zip_duration = duration

    @property
    def pack_meta(self) -> LineStickerMetadata:
        """
        Get the LINE sticker package metadata.

        :return: sticker package metadata
        """
        return self._pack_meta

    @property
    def available(self) -> bool:
        """
        Check if the sticker package is available.

        :return: if the sticker is available
        """
        return self._available

    @property
    def already_exists(self) -> bool:
        """
        Check if the sticker package is already exists (already downloaded).

        :return: if the sticker package already exists
        """
        return self._already_exists

    @property
    def download_succeed(self) -> bool:
        """
        Check if the download succeed.

        :return: if the download succeed
        """
        return self._download_succeed

    @property
    def zip_succeed(self) -> bool:
        """
        Check if the downloaded stcxkers are successfully zipped.

        :return: if the stickers are zipped
        """
        return self._zip_succeed

    @property
    def missed_sticker_id(self) -> List[int]:
        """
        Get the ID of the list stickers that failed to download.

        :return: sticker IDs not downloaded
        """
        return self._not_downloaded_id

    @property
    def succeed(self) -> bool:
        """
        If the process of downloading and zipping the stickers succeed.

        :return: if the whole download process succeed
        """
        return self._already_exists or (self._available and self._download_succeed and self._zip_succeed)

    @property
    def time_spent(self) -> float:
        """
        Get the time spent on downloading and zipping the stickers.

        :return: time spent on the whole download process
        """
        return self._get_meta_duration + self._download_duration + self._zip_duration


class LineStickerPackDownloader:
    """Class for downloading a sticker pack."""

    @staticmethod
    def _get_metadata(pack_dl_result: LineStickerPackDownloadResult, pack_id: Union[str, int]):
        _start = time.time()

        try:
            pack_meta = LineStickerUtils.get_pack_meta(pack_id)
        except MetadataNotFoundError:
            return None

        pack_dl_result.set_available(pack_meta, time.time() - _start)
        return pack_meta

    @staticmethod
    def _download_stickers(pack_dl_result: LineStickerPackDownloadResult, pack_id: Union[str, int]) \
            -> List[Tuple[BinaryIO, int]]:
        pack_meta = pack_dl_result.pack_meta

        _start = time.time()

        sticker_to_zip: List[Tuple[BinaryIO, int]] = []

        with ThreadPoolExecutor() as executor:
            def handle_animated(stk_id) -> Tuple[Optional[BinaryIO], int]:
                stk_io = LineStickerUtils.get_downloaded_animated(pack_id, stk_id, with_frames=False)
                if not stk_io:
                    return None, stk_id

                pack_dl_result.set_sticker_downloaded(stk_id)
                return stk_io, stk_id

            def handle_static(stk_id) -> Tuple[Optional[BinaryIO], int]:
                stk_io = LineStickerUtils.get_downloaded_sticker(stk_id)
                if not stk_io:
                    return None, stk_id

                pack_dl_result.set_sticker_downloaded(stk_id)
                return stk_io, stk_id

            futures = []

            if pack_meta.is_animated_sticker:
                for sticker_id in pack_meta.sticker_ids:
                    futures.append(executor.submit(handle_animated, sticker_id))
            else:
                for sticker_id in pack_meta.sticker_ids:
                    futures.append(executor.submit(handle_static, sticker_id))

            for future in as_completed(futures):
                sticker_io, sticker_id = future.result()
                if sticker_io:
                    sticker_to_zip.append((sticker_io, sticker_id))

        pack_dl_result.set_download_completed(time.time() - _start)

        return sticker_to_zip

    @staticmethod
    def _zip_stickers(pack_dl_result: LineStickerPackDownloadResult,
                      sticker_to_zip: List[Tuple[BinaryIO, int]], zip_path: str):
        _start = time.time()

        with ZipFile(zip_path, "w") as zip_file:
            for sio, sid in sticker_to_zip:
                with sio:
                    zip_file.writestr(f"{sid}.png", sio.read())
                    pack_dl_result.set_sticker_zipped(sid)

        pack_dl_result.set_zip_completed(time.time() - _start)

    @staticmethod
    def get_pack(pack_id: Union[str, int]) -> Optional[BinaryIO]:
        """
        Get the sticker package zip as a :class:`BinaryIO`.

        Will try to download the sticker package if not downloaded.

        Returns ``None`` if the sticker package is not available (not found).

        :param pack_id: sticker package ID to be downloaded
        :return: binary stream of the sticker package zip file
        """
        sticker_pack_path = os.path.join(_temp_dir, f"{pack_id}.zip")

        if not os.path.exists(sticker_pack_path):
            result = LineStickerPackDownloader.download_pack(pack_id)

            if not result.succeed:
                return None

        return open(sticker_pack_path, "rb")

    @staticmethod
    def download_pack(pack_id: Union[str, int]) -> LineStickerPackDownloadResult:
        """
        Download the sticker package.

        :param pack_id: ID of the sticker package to be downloaded
        :return: sticker package download result
        """
        pack_dl_result = LineStickerPackDownloadResult()

        pack_meta = LineStickerPackDownloader._get_metadata(pack_dl_result, pack_id)
        if not pack_meta:
            return pack_dl_result

        zip_path = os.path.join(_temp_dir, f"{pack_id}.zip")
        if os.path.exists(zip_path):
            pack_dl_result.set_exists()
            return pack_dl_result

        sticker_to_zip = LineStickerPackDownloader._download_stickers(pack_dl_result, pack_id)

        LineStickerPackDownloader._zip_stickers(pack_dl_result, sticker_to_zip, zip_path)

        return pack_dl_result


# endregion


class LineStickerUtils(ClearableMixin):
    """Main LINE sticker utilities."""

    # pylint: disable=fixme

    # https://github.com/RaenonX/Jelly-Bot/issues/55

    # TODO: command for download sticker package

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
    def get_pack_meta(pack_id: Union[str, int]) -> LineStickerMetadata:
        """
        Get the sticker package metadata.

        :param pack_id: sticker package ID
        :return: packed metadata object
        :raises MetadataNotFoundError: request to get the metadata does not return 200
        """
        pack_meta = requests.get(LineStickerUtils.get_meta_url(pack_id))

        if not pack_meta.ok:
            raise MetadataNotFoundError(pack_id)

        return LineStickerMetadata(pack_meta.json())

    @staticmethod
    def _prepare_output(output_path: str, sticker_id: int, sticker_type: LineStickerType):
        if not output_path:
            output_path = os.path.join(_temp_dir, f"{sticker_id}.{sticker_type.to_extension()}")

            LineStickerTempStorageManager.create_file(output_path)

        return output_path

    @staticmethod
    def get_downloaded_sticker(sticker_id: Union[str, int]) -> Optional[BinaryIO]:
        """
        Get the downloaded sticker as gif from the temporary storage as a :class:`BinaryIO` stream.

        If the image has not been downloaded, the utils will try to download it.

        If the download mentioned above fails, returns ``None``.

        -------

        Recommended example usage::

        >>> with LineStickerUtils.get_downloaded_sticker(1, 1) as f:
        >>>     # code

        :param sticker_id: sticker ID
        :return: `BinaryIO` stream if found / downloaded
        """
        sticker_path = os.path.join(_temp_dir, f"{sticker_id}.png")

        if not os.path.exists(sticker_path):
            result = LineStickerUtils.download_sticker(sticker_id, sticker_path)

            if not result.succeed:
                return None

        return open(sticker_path, "rb")

    @staticmethod
    def get_downloaded_animated(pack_id: Union[str, int], sticker_id: Union[str, int], *, with_frames: bool = True) \
            -> Optional[BinaryIO]:
        """
        Get the downloaded animated sticker as gif from the temporary storage as a :class:`BinaryIO` stream.

        If the image has not been downloaded, the utils will try to download it.

        If the download mentioned above fails, returns ``None``.

        -------

        Recommended example usage::

        >>> with LineStickerUtils.get_downloaded_animated(1, 1) as f:
        >>>     # code

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :param with_frames: if the extracted frames should be preserved if file not ready
        :return: `BinaryIO` stream if found / downloaded
        """
        sticker_path = os.path.join(_temp_dir, f"{sticker_id}.gif")

        if not os.path.exists(sticker_path):
            result = LineStickerUtils.download_apng_as_gif(pack_id, sticker_id, with_frames=with_frames)

            if not result.succeed:
                return None

        return open(sticker_path, "rb")

    @staticmethod
    def get_downloaded_apng_frames(pack_id: Union[str, int], sticker_id: Union[str, int]) -> Optional[BinaryIO]:
        """
        Get the downloaded png frames of the animated sticker from the temporary storage as a :class:`BinaryIO` stream.

        If the image has not been downloaded, the utils will try to download it.

        If the download mentioned above fails, returns ``None``.

        -------

        Recommended example usage::

        >>> with LineStickerUtils.get_downloaded_apng_frames(1, 1) as f:
        >>>     # code

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

    @staticmethod
    def get_downloaded_sticker_pack(pack_id: Union[str, int]) -> Optional[BinaryIO]:
        """
        Get the downloaded sticker package zip as a :class:`BinaryIO`.

        Will try to download the sticker package if not downloaded.

        Returns ``None`` if the sticker package is not available (not found).

        :param pack_id: sticker package ID to be downloaded
        :return: binary stream of the sticker package zip file
        """
        return LineStickerPackDownloader.get_pack(pack_id)

    @staticmethod
    def download_apng_as_gif(pack_id: Union[str, int], sticker_id: Union[str, int],
                             output_path: Optional[str] = None, *,
                             with_frames: bool = True) \
            -> LineAnimatedStickerDownloadResult:
        """
        Download animated sticker as gif.

        ----

        If ``output_path`` is specified:

        - The file will **NOT** be automatically removed.

        - Cannot acquire using ``get_downloaded_animated()``

        If ``output_path`` is not specified:

        - The file will be automatically removed
        after :class:`ExtraService.Sticker.MaxStickerTempFileLifeSeconds` seconds

        - Can be acquired using ``get_downloaded_animated()``

        ----

        If there's a file already at ``output_path``, then it's considered as the sticker is downloaded,
        regardless its actual content.

        Returned :class:`LineAnimatedStickerDownloadResult` will indicate if this situation occurred.

        :param pack_id: sticker package ID
        :param sticker_id: sticker ID
        :param output_path: gif output path
        :param with_frames: if the extracted frames should be preserved
        :return: result of the download and conversion
        """
        result = LineAnimatedStickerDownloadResult(int(sticker_id))

        output_path = LineStickerUtils._prepare_output(output_path, sticker_id, LineStickerType.ANIMATED)

        # Check if the sticker exists
        response = requests.get(LineStickerUtils.get_apng_url(pack_id, sticker_id))
        if not response.ok:
            return result

        result.set_available()

        # Check if the file exists
        frame_zip_path = f"{os.path.splitext(output_path)[0]}-frames.zip"

        if os.path.exists(output_path) and (not with_frames or os.path.exists(frame_zip_path)):
            result.set_already_exists()
            return result

        # Download the sticker
        _start = time.time()
        apng_bin = response.content

        result.set_downloaded(time.time() - _start)

        # Convert apng to gif
        result.set_conversion_result(apng2gif.convert(apng_bin, output_path, zip_frames=with_frames))

        return result

    @staticmethod
    def download_sticker(sticker_id: Union[str, int], output_path: Optional[str] = None) -> LineStickerDownloadResult:
        """
        Download a static sticker.

        ----

        If ``output_path`` is specified:

        - The file will **NOT** be automatically removed.

        - Cannot acquire using ``get_downloaded_sticker()``

        If ``output_path`` is not specified:

        - The file will be automatically removed
        after :class:`ExtraService.Sticker.MaxStickerTempFileLifeSeconds` seconds

        - Can be acquired using ``get_downloaded_sticker()``

        ----

        If there's a file already at ``output_path``, then it's considered as the sticker is downloaded,
        regardless its actual content.

        Returned :class:`LineStickerDownloadResult` will indicate if this situation occurred.

        :param sticker_id: sticker ID
        :param output_path: gif output path
        :return: result of the download
        """
        result = LineStickerDownloadResult(int(sticker_id))

        output_path = LineStickerUtils._prepare_output(output_path, sticker_id, LineStickerType.STATIC)

        # Check if the sticker exists
        response = requests.get(LineStickerUtils.get_sticker_url(sticker_id))
        if not response.ok:
            return result

        result.set_available()

        # Check if the file exists
        if os.path.exists(output_path):
            result.set_already_exists()
            return result

        # Download the sticker
        _start = time.time()
        png_bin = response.content

        result.set_downloaded(time.time() - _start)

        # Save the file
        with open(output_path, "wb") as f:
            f.write(png_bin)

        return result

    @staticmethod
    def download_sticker_pack(pack_id: Union[str, int]) -> LineStickerPackDownloadResult:
        """
        Download the sticker package.

        ----

        If the sticker is animated:

        - The frames of it will **NOT** be downloaded

        :param pack_id: sticker package to be downloaded
        :return: sticker package download result
        """
        return LineStickerPackDownloader.download_pack(pack_id)
