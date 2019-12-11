import tempfile
from typing import List

import requests

from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class LineStickerType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return LineStickerType.STATIC

    ANIMATED = 0, _("Animated Sticker")
    SOUND = 1, _("Sticker with Sounds")
    STATIC = 2, _("Static Sticker")


class LineStickerManager:
    def __init__(self):
        self._tmp_dir = tempfile.TemporaryFile(prefix="LineSticker")

    # DRAFT: Line Sticker: Download Utils not completed
    # def _get_content_(self, sticker_type, pack_id, list_ids):
    #     """
    #     :param sticker_type: The type of the sticker
    #     :type sticker_type: LineStickerType
    #
    #     Parameters:
    #         `sticker_content_type`: The type of content to download. (sticker_content_type)
    #         `pack_id`: line sticker package ID.
    #         `pack_name`: line sticker package ID.
    #         `list_ids`: id list of the content to download.
    #
    #     Returns:
    #         Returns path of the writed contents in list.
    #
    #     Errors:
    #         raise `MetaNotFoundException` if status code of getting pack meta is not 200.
    #     """
    #     act = LineStickerManager.get_download_action(sticker_content_type)
    #     if act is None:
    #         raise ValueError("Url function and file extension of specified sticker type not handled. {}".format(
    #         repr(sticker_content_type)))
    #
    #     url_func, file_ext = act
    #
    #     stk_dir = os.path.join(self._file_proc_path, str(pack_id))
    #     files_path = []
    #
    #     try:
    #         os.makedirs(stk_dir)
    #     except OSError as e:
    #         if e.errno != errno.EEXIST:
    #             raise
    #
    #     for stk_id in list_ids:
    #         save_path = os.path.join(stk_dir, str(stk_id) + file_ext)
    #
    #         url = url_func(pack_id, stk_id)
    #         request_result = requests.get(url, stream=True)
    #
    #         with open(save_path, "wb") as f:
    #             for chunk in request_result.iter_content(chunk_size=20480):
    #                 if chunk:
    #                     f.write(chunk)
    #
    #         files_path.append(save_path)
    #
    #     return files_path

    # def download_stickers(self, sticker_metadata, download_sound_if_available=False):
    #     """\
    #     Parameters:
    #         `sticker_metadata`: metadata of sticker package.
    #
    #     Returns:
    #         Returns path of compressed sticker package(zip).
    #     """
    #     stk_ids = sticker_metadata.stickers
    #     pack_id = sticker_metadata.pack_id
    #     pack_name = str(pack_id) + (LineStickerManager.DOWNLOAD_SOUND_CODE if download_sound_if_available else "")
    #     comp_file_path = os.path.join(self._file_proc_path, pack_name + ".zip")
    #
    #     if os.path.isfile(comp_file_path):
    #         time_consumed_dl = 0.0
    #         time_consumed_comp = 0.0
    #     else:
    #         content_type_to_download = LineStickerType.ANIMATED if sticker_metadata.is_animated_sticker else
    #         LineStickerType.STATIC
    #
    #         _start = time.time()
    #         path_list = self._get_content_(content_type_to_download, pack_id, stk_ids)
    #
    #         if download_sound_if_available and sticker_metadata.is_animated_sticker:
    #             path_list.extend(self._get_content_(LineStickerType.SOUND, pack_id, stk_ids))
    #         time_consumed_dl = time.time() - _start
    #
    #         _start = time.time()
    #
    #         with zipfile.ZipFile(comp_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    #             for path in path_list:
    #                 try:
    #                     zipf.write(path, os.path.basename(path))
    #                 except OSError:
    #                     return None
    #
    #         try:
    #             shutil.rmtree(os.path.join(self._file_proc_path, pack_name))
    #         except OSError as exc:
    #             if exc.errno == errno.ENOENT:
    #                 pass
    #             else:
    #                 raise exc
    #
    #         time_consumed_comp = time.time() - _start
    #
    #     return LinkStickerDownloadResult(comp_file_path, stk_ids, time_consumed_dl, time_consumed_comp)
    #
    # def get_pack_meta(self, pack_id: str):
    #     """
    #
    #     :param pack_id: Numeric string of the sticker package ID.
    #     :type pack_id: str
    #     :return: LineStickerMetadata
    #     """
    #     pack_meta = requests.get(LineStickerManager.get_meta_url(pack_id))
    #
    #     if pack_meta.status_code == 200:
    #         json_dict = json.loads(pack_meta.text)
    #         return LineStickerMetadata(json_dict)
    #     else:
    #         raise MetaDataNotFoundError(pack_meta.status_code)

    @staticmethod
    def is_sticker_exists(sticker_id: [int, str]):
        response = requests.get(LineStickerManager.get_sticker_url(sticker_id))

        return response.ok

    @staticmethod
    def get_meta_url(pack_id: [int, str]) -> str:
        return f"https://stickershop.line-scdn.net/products/0/0/1/{pack_id}/android/productInfo.meta"

    @staticmethod
    def get_sticker_url(sticker_id: [int, str]) -> str:
        return f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/android/sticker.png"

    @staticmethod
    def get_apng_url(pack_id: [int, str], sticker_id: [int, str]) -> str:
        return f"https://sdl-stickershop.line.naver.jp/products/0/0/1/{pack_id}/android/animation/{sticker_id}.png"

    @staticmethod
    def get_sound_url(sticker_id: [int, str]) -> str:
        return f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/IOS/sticker_sound.m4a"

    @staticmethod
    def get_dl_info(content_type: LineStickerType) -> (callable, str):
        dl_dict = {
            LineStickerType.ANIMATED: (LineStickerManager.get_apng_url, ".apng"),
            LineStickerType.STATIC: (LineStickerManager.get_sticker_url, ".png"),
            LineStickerType.SOUND: (LineStickerManager.get_sound_url, ".m4a")
        }

        return dl_dict.get(content_type)


class LineStickerMetadata:
    DEFAULT_LOCALE = "en"

    def __init__(self, meta_dict):
        self._dict = meta_dict

    @property
    def pack_id(self) -> int:
        return int(self._dict["packageId"])

    def get_title(self, locale=DEFAULT_LOCALE):
        return self._get_localized_object_("title", locale)

    def get_author(self, locale=DEFAULT_LOCALE):
        return self._get_localized_object_("author", locale)

    @property
    def stickers(self) -> List[int]:
        stk_obj = self._dict.get("stickers", [])
        if len(stk_obj) > 0:
            return [int(stk["id"]) for stk in stk_obj]
        else:
            return stk_obj

    @property
    def is_animated_sticker(self):
        return self._dict.get("hasAnimation", False)

    @property
    def has_se(self):
        return self._dict.get("hasSound", False)

    def _get_localized_object_(self, key, locale):
        localized_object = self._dict.get(key)
        if localized_object is not None:
            localized_str_ret = localized_object.get(locale)

            if localized_str_ret is None:
                return localized_object.get(LineStickerMetadata.DEFAULT_LOCALE)
            else:
                return localized_str_ret
        else:
            return None


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

class MetaDataNotFoundError(Exception):
    def __init__(self, sticker_id: [int, str]):
        super().__init__(f"Sticker metadata not found for ID #{sticker_id}")
