"""
Implementations to bridge the utilities and MongoDB.
"""
from bson import CodecOptions
from bson.codec_options import TypeRegistry

from .color import ColorMongoEncoder
from .flags import type_registry as tr_flags


def get_codec_options() -> CodecOptions:
    """
    Get the :class:`CodecOptions` to be used for ``pymongo``.

    This :class:`CodecOptions` will include the type encoder for:

    - ``extutils.color.Color``

    - ``extutils.flag`` - All types of flags

    :return: `CodecOptions` to be used for ``pymongo``.
    """
    type_registry = tr_flags
    type_registry.append(ColorMongoEncoder())

    return CodecOptions(type_registry=TypeRegistry(type_registry))
