from bson import CodecOptions
from bson.codec_options import TypeRegistry, TypeEncoder


def register_encoder(cls):
    cls_encoder = type(f"Flag{cls.__name__}Encoder",
                       (TypeEncoder,),
                       {"transform_python": lambda self, value: value.code,
                        "python_type": property(lambda self: cls)})

    type_registry.append(cls_encoder())


type_registry: list = []


def get_codec_options():
    return CodecOptions(
        type_registry=TypeRegistry(type_registry))
