from dataclasses import dataclass
from fractions import Fraction
import glob
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time
from typing import Any, Tuple, List, Optional
from zipfile import ZipFile

from PIL import Image

__all__ = ["convert", "ConvertResult"]

_IDX_CLR_BACKGROUND = 255
_IDX_CLR_TRANSPARENT = 255


@dataclass
class ConvertResult:
    """
    The result of the conversion.

    Unit of the duration is seconds.
    """
    input_exists: bool = True

    frame_extracted: bool = False
    frame_extraction_duration: float = 0.0

    frame_zipped: bool = False
    frame_zipping_time: float = 0.0
    frame_zipping_exception: Optional[Exception] = None

    image_data_acquired: bool = False
    image_data_acquisition_duration: float = 0.0

    gif_merged: bool = False
    gif_merge_duration: float = 0.0

    @property
    def succeed(self):
        if not self.input_exists:
            return False

        return self.frame_extracted and self.image_data_acquired and self.gif_merged

    @property
    def time_spent(self):
        return self.frame_extraction_duration \
               + self.frame_zipping_time \
               + self.image_data_acquisition_duration \
               + self.gif_merge_duration  # noqa: E126,E127


def _get_file_name(file_path: str) -> str:
    """
    Get the file name without extension.

    :param file_path: path of the file
    :return: file name without extension
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def _extract_frames(result: ConvertResult, file_path: str):
    """
    Extract the frames of the APNG file at ``apng_path`` using ``apngdis``.

    :param result: conversion result object
    :param file_path: file path of the apng file to be extracted
    """
    _start = time.time()

    file_name = _get_file_name(file_path)

    return_code = subprocess.call(f"apngdis {file_path} {file_name}-")

    if return_code == 0:
        result.frame_extraction_duration = time.time() - _start
        result.frame_extracted = True


def _zip_frames(result: ConvertResult, apng_path: str, output_path: str):
    """
    Zip the frames to be a single zip file preceded with the apng file name.

    :param result: conversion result object
    :param apng_path: path of the source apng
    :param output_path: output directory of the zip file
    """
    _start = time.time()

    apng_name = _get_file_name(apng_path)
    out_name = _get_file_name(output_path)

    try:
        with ZipFile(os.path.join(os.path.dirname(output_path), f"{out_name}-frames.zip"), "w") as f:
            for apng_path in glob.glob(f"{apng_name}-*.png"):
                f.write(apng_path)
    except Exception as ex:
        result.frame_zipping_exception = ex
        return

    result.frame_zipping_time = time.time() - _start
    result.frame_zipped = True


def _process_frame_transparent(image_path: str):
    """
    Apply color index for transparency ``transparent_index`` to the image
    at ``image_path`` and return the modified image.

    Copied and modified from ``apng2gif``.

    :param image_path: path of the image
    """
    image = Image.open(image_path)
    alpha = image.getchannel("A")
    # Convert the image into P mode but only use 255 colors in the palette out of 256
    image = image.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    # Set all alpha < 128 to value 255, 0 otherwise
    image.paste(_IDX_CLR_TRANSPARENT, Image.eval(alpha, lambda a: 255 if a <= 128 else 0))
    return image


def _process_frame_duration(file_path: str) -> Fraction:
    """
    Get the duration of the frame by extracting the corresponding text file yielded by ``apngdis``.

    :param file_path: path of the info text file
    :return: duration of the frame
    """
    with open(file_path, "r") as f:
        duration = f.read()
        duration = duration.split("=", 1)[1]  # Split `delay=X/Y` to 2 parts and only get the right one
        duration = Fraction(duration)  # Cast the delay fraction to `Fraction`

        return duration


def _get_image_data(result: ConvertResult, apng_path: str) -> Tuple[List[Any], List[Fraction]]:
    """
    Get the data of the png frames extracted from ``apng_path``.

    Returns a 2-tuple which:
    - 1st element is the processed frames in PIL image objects
    - 2nd element is the duration of each frames

    :param result: conversion result object
    :param apng_path: path of the source apng
    :return: frame data to be used
    """
    _start = time.time()

    images = []
    durations = []

    for file_path in sorted(glob.glob(f"{_get_file_name(apng_path)}-*.png")):
        images.append(_process_frame_transparent(file_path))
        durations.append(_process_frame_duration(f"{_get_file_name(file_path)}.txt"))

    result.image_data_acquisition_duration = time.time() - _start
    result.image_data_acquired = True

    return images, durations


def _make_gif(result: ConvertResult, apng_path: str, output_path: str):
    """
    Mix all png frames extracted from ``apng_path`` to be an single gif and output it to ``output_path``.

    :param result: conversion result object
    :param apng_path: path of the apng file
    :param output_path: path for the completed gif
    """
    images, durations = _get_image_data(result, apng_path)

    if not result.image_data_acquired:
        return

    _start = time.time()

    image, *images = images  # Take out the first image as the base image

    image.save(output_path, format="GIF", save_all=True, append_images=images, loop=0, disposal=2,
               transparency=_IDX_CLR_TRANSPARENT, background=_IDX_CLR_BACKGROUND,
               optimize=True, duration=durations)

    result.gif_merge_duration = time.time() - _start
    result.gif_merged = True


def convert(apng_path: str, output_path: str, *, zip_frames: bool = True) -> ConvertResult:
    """
    Convert the file at ``apng_path`` to gif and store it at ``output_path``.

    :param apng_path: path of the apng to be converted
    :param output_path: path for the processed gif
    :param zip_frames: to zip the extracted frames
    :returns: result of the conversion
    """
    original_dir = os.getcwd()
    result = ConvertResult()

    if not os.path.exists(apng_path):
        result.input_exists = False
        return result

    with TemporaryDirectory() as temp_dir:
        # Copy `apngdis` to the temp directory
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apngdis.exe"),
                    os.path.join(temp_dir, "apngdis.exe"))

        # Copy the image for extraction
        apng_path_dst = os.path.join(temp_dir, os.path.basename(apng_path))

        shutil.copy(apng_path, apng_path_dst)
        apng_path = apng_path_dst

        # Set the current working directory to the temp directory
        os.chdir(temp_dir)

        # Main process
        out_path = output_path if os.path.isabs(output_path) else os.path.join(original_dir, output_path)

        _extract_frames(result, apng_path)
        if result.frame_extracted:
            if zip_frames:
                _zip_frames(result, apng_path, out_path)

            _make_gif(result, apng_path, out_path)

        # Restore the working directory (REQUIRED, disabling this causes infinite recursion)
        os.chdir(original_dir)

        return result
