from bson import CodecOptions
from bson.codec_options import TypeRegistry

from rxtoolbox.flags.mongo import type_registry as tr_flags

from .color import ColorMongoEncoder


def get_codec_options():
    type_registry = tr_flags
    type_registry.append(ColorMongoEncoder())

    return CodecOptions(type_registry=TypeRegistry(type_registry))
