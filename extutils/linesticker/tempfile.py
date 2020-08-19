"""Temporary storage manager for :class:`extline.linesticker.LineStickerUtils`."""

__all__ = ("LineStickerTempStorageManager",)

from datetime import datetime
import os
from threading import Thread
import time
from typing import Dict

from extutils.checker import arg_type_ensure
from extutils.dt import now_utc_aware
from JellyBot.systemconfig import ExtraService


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
