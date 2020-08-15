"""
Module to extract the frames of APNG **without** constraint violation checking.

.. note::
    https://wiki.mozilla.org/APNG_Specification
    https://github.com/eight04/pyAPNG
    https://github.com/tonix0114/apng-splitter
"""
# pylint: disable=C0103

from abc import ABC
import binascii
from fractions import Fraction
from enum import Enum
from dataclasses import dataclass, field
import io
import struct
from typing import Union, Generator, List, Tuple

from PIL import Image

__all__ = ("extract_frames",)

SIGNATURE_PNG = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"


class _Dispose(Enum):
    APNG_DISPOSE_OP_NONE = 0
    APNG_DISPOSE_OP_BACKGROUND = 1
    APNG_DISPOSE_OP_PREVIOUS = 2


@dataclass
class _BaseChunk:
    type_raw: str
    length: int
    data: bytes
    crc: str

    @staticmethod
    def make_chunk(chunk_type: str, chunk_data: bytes) -> '_BaseChunk':
        """
        Make a new chunk with the type as ``chunk_type`` and ``chunk_data``.

        ``chunk_data`` **MUST** exclude length (0~4 B), type (4~8 B) and CRC (last 4 B).

        :param chunk_type: type of the chunk
        :param chunk_data: data of the chunk excluding length, type and CRC
        :return: a new `_BaseChunk` with CRC calculated
        """
        new_data = struct.pack(">I", len(chunk_data))
        chunk_data = chunk_type.encode("latin-1") + chunk_data
        new_data += chunk_data + struct.pack(">I", binascii.crc32(chunk_data) & 0xffffffff)

        return _BaseChunk.from_bytes(new_data)

    @staticmethod
    def from_bytes(data: bytes) -> '_BaseChunk':
        """
        Make a :class:`_BaseChunk` from :class:`bytes`.

        :param data: data to construct the chunk
        :return: constructed `_BaseChunk`
        """
        chunk_length: int = struct.unpack('>I', data[:4])[0]
        chunk_data = data[:4]
        data = data[4:]

        # Extract chunk type
        chunk_type: str = data[:4].decode("utf-8")
        chunk_data += data[:4]
        data = data[4:]

        # Extract chunk data
        chunk_data += data[:chunk_length]
        data = data[chunk_length:]

        # Extract CRC
        crc_data = data[:4]
        chunk_crc: str = hex(struct.unpack('>I', crc_data)[0])
        chunk_data += crc_data

        return _BaseChunk(chunk_type, chunk_length, chunk_data, chunk_crc)

    @property
    def pure_data(self) -> bytes:
        """
        Get the data excluding length, type and CRC.

        :return: data excluding length, type and CRC
        """
        return self.data[8:-4]

    def to_chunk_class(self) -> Union['_DataChunkIHDR', '_DataChunkacTL', '_DataChunkIDAT', '_DataChunkfcTL',
                                      '_DataChunkfdAT', '_DataChunkIEND', '_DataChunkOther']:
        """
        Convert this :class:`_BaseChunk` to its corresponding chunk class.

        Currently supported chunk types:
        - ``IHDR`` - :class`_DataChunkIHDR`

        - ``acTL`` - :class`_DataChunkacTL`

        - ``IDAT`` - :class`_DataChunkIDAT`

        - ``fcTL`` - :class`_DataChunkfcTL`

        - ``fdAT`` - :class`_DataChunkfdAT`

        - ``IEND`` - :class`_DataChunkIEND`

        Types which are not yet supported will be converted to :class:`_DataChunkOther`.

        :return: data chunk class corresponding to its type
        """
        convert_dict = {
            "IHDR": _DataChunkIHDR,
            "acTL": _DataChunkacTL,
            "IDAT": _DataChunkIDAT,
            "fcTL": _DataChunkfcTL,
            "fdAT": _DataChunkfdAT,
            "IEND": _DataChunkIEND,
        }

        chuck_cls: type = convert_dict.get(self.type_raw, _DataChunkOther)

        return chuck_cls(self)


@dataclass
class _DataChunkBase(ABC):
    """
    Base data chunk class.

    Inherit this class for specific type of data chunk for extended utility.
    """

    base_chunk: _BaseChunk

    length: int = field(init=False)
    data: bytes = field(init=False)
    crc: str = field(init=False)

    def __post_init__(self):
        self.length = self.base_chunk.length
        self.data = self.base_chunk.data
        self.crc = self.base_chunk.crc

    @property
    def pure_data(self) -> bytes:
        """
        Get the data excluding length, type and CRC.

        :return: data excluding length, type and CRC
        """
        return self.base_chunk.pure_data


@dataclass
class _DataChunkIHDR(_DataChunkBase):
    """Data class of ``IHDR`` chunk."""

    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.width, self.height = struct.unpack(">II", self.pure_data[0:8])

    def replace_resolution(self, new_width: int, new_height: int) -> '_DataChunkIHDR':
        """
        Replace the resolution of ``IHDR`` chunk, then generate a new ``IHDR`` chunk and return it.

        :param new_width: new width of the image
        :param new_height: new height of the image
        :return: newly generated `IHDR` chunk with the new resolutions
        """
        new_data = struct.pack(">II", new_width, new_height) + self.pure_data[8:]

        return _DataChunkIHDR(_BaseChunk.make_chunk("IHDR", new_data))


@dataclass
class _DataChunkacTL(_DataChunkBase):
    """Data class of ``acTL`` chunk."""

    frame_count: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.frame_count = struct.unpack(">I", self.pure_data[0:4])[0]


@dataclass
class _DataChunkIDAT(_DataChunkBase):
    """Data class of ``IDAT`` chunk."""


@dataclass
class _DataChunkIEND(_DataChunkBase):
    """Data class of ``IEND`` chunk."""


@dataclass
class _DataChunkOther(_DataChunkBase):
    """Data class for not-yet-supported data chunk."""


@dataclass
class _DataChunkfcTL(_DataChunkBase):
    """Data class of ``fcTL`` chunk."""

    # pylint: disable=R0902

    seq_num: int = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)
    x_offset: int = field(init=False)
    y_offset: int = field(init=False)
    delay_num: int = field(init=False)
    delay_den: int = field(init=False)
    dispose: _Dispose = field(init=False)
    blend: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.seq_num, self.width, self.height, self.x_offset, self.y_offset = \
            struct.unpack(">IIIII", self.pure_data[0:20])
        self.delay_num, self.delay_den, self.dispose, self.blend = \
            struct.unpack(">HHBB", self.pure_data[20:26])

        self.dispose = _Dispose(self.dispose)

    # noinspection PyPep8Naming
    def generate_IHDR(self, IHDR: _DataChunkIHDR) -> _DataChunkIHDR:
        """
        Generate a new ``IHDR`` chunk using the resolutions encoded in this chunk.

        :param IHDR: Original `_DataChunkIHDR` to be used to generate a new `IHDR` chunk
        :return: new `IHDR` chunk with the resolutions defined in this chunk
        """
        return IHDR.replace_resolution(self.width, self.height)


@dataclass
class _DataChunkfdAT(_DataChunkBase):
    """Data class of ``fdAT`` chunk."""

    # noinspection PyPep8Naming
    def to_IDAT(self) -> _DataChunkIDAT:
        """
        Convert this chunk to be an ``IDAT` chunk.

        :return: a converted `_DataChunkIDAT` instance
        """
        # Skipping 4 B because it's frame number
        return _DataChunkIDAT(_BaseChunk.make_chunk("IDAT", self.base_chunk.pure_data[4:]))


def _parse_chunks(data) -> Generator[_BaseChunk, None, None]:
    data = data[8:]

    while data:
        new_chunk = _BaseChunk.from_bytes(data)
        yield new_chunk

        data = data[new_chunk.length + 12:]


# noinspection PyPep8Naming
def _create_image_bytes(IHDR: _DataChunkIHDR, fcTL: _DataChunkfcTL,
                        fdAT_IDAT: Union[_DataChunkfdAT, _DataChunkIDAT], IEND: _DataChunkIEND):
    # Append signature
    image_data = SIGNATURE_PNG

    # Append new header by size info from fcTC
    image_data += fcTL.generate_IHDR(IHDR).data

    if hasattr(fdAT_IDAT, "to_IDAT"):
        # fdAT
        image_data += fdAT_IDAT.to_IDAT().data
    else:
        # IDAT
        image_data += fdAT_IDAT.data

    # Append IEND
    image_data += IEND.data

    return image_data


def extract_frames(apng_path: str) -> List[Tuple[bytes, Fraction]]:
    """
    Extract the frames of apng file at ``apng_path``.

    Returns a 2-tuple containing the byte data of a frame and its delay.

    :param apng_path: path of the apng file to be extracted
    :return: list of 2-tuple containing frame byte data and its delay
    """
    # pylint: disable=R0914

    with open(apng_path, "rb") as f:
        data = f.read()

    chunk = [c.to_chunk_class() for c in _parse_chunks(data)]

    ret: List[Tuple[bytes, Fraction]] = []

    IHDR = chunk[0]
    acTL = chunk[1]
    IEND = chunk[-1]

    image_data_prev = None

    for idx in range(2, 2 + (acTL.frame_count * 2), 2):
        if image_data_prev:
            fcTL = chunk[idx - 4]
            fdAT_IDAT = chunk[idx - 3]
            image_data_prev = False
        else:
            fcTL = chunk[idx]
            fdAT_IDAT = chunk[idx + 1]

        # Create image byte data
        image_data = _create_image_bytes(IHDR, fcTL, fdAT_IDAT, IEND)

        # Check and set flag to handle `_Dispose.APNG_DISPOSE_OP_PREVIOUS`
        if fcTL.dispose == _Dispose.APNG_DISPOSE_OP_PREVIOUS:
            image_data_prev = True

        # Save image
        img = Image.new("RGBA", (IHDR.width, IHDR.height), (255, 255, 255, 0))
        img.paste(Image.open(io.BytesIO(image_data)), (fcTL.x_offset, fcTL.y_offset))
        img_byte_data = io.BytesIO()
        img.save(img_byte_data, format="PNG")
        img_byte_data = img_byte_data.getvalue()

        delay = Fraction(f"{fcTL.delay_num}/{fcTL.delay_den}")

        ret.append((img_byte_data, delay))

    return ret
