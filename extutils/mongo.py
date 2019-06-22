from bson import CodecOptions
from bson.codec_options import TypeRegistry

from .color import ColorMongoEncoder
from .flags import type_registry as tr_flags


def get_codec_options():
    type_registry = tr_flags
    type_registry.append(ColorMongoEncoder())

    return CodecOptions(type_registry=TypeRegistry(type_registry))
