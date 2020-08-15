"""
Implementations to enable these ``Flag`` can be directly used on ``pymongo``.
"""

from bson import CodecOptions
from bson.codec_options import TypeRegistry, TypeEncoder


def register_encoder(cls):
    """
    Register the flag type encoder ``cls``.

    The final :class:`CodecOptions` to be used on ``pymongo`` can be acquired by calling ``get_codec_options()``.

    :param cls: flag enocder class to be registered
    """
    cls_encoder = type(f"Flag{cls.__name__}Encoder",
                       (TypeEncoder,),
                       {"transform_python": lambda self, value: value.code,
                        "python_type": property(lambda self: cls)})

    type_registry.append(cls_encoder())


type_registry: list = []


def get_codec_options() -> CodecOptions:
    """
    Register all flag type registry and get the :class:`CodecOptions` to be used on ``pymongo``.

    :return: `CodecOptions` to be used from `pymongo`
    """
    return CodecOptions(type_registry=TypeRegistry(type_registry))
