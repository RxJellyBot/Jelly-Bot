from typing import Any

from bson import ObjectId

from extutils.flags import FlagCodeMixin


class DecoParamCaster:
    def __init__(self, dict_keys: dict = None):
        self._dict_keys = dict_keys

    def __call__(self, f):
        def wrap_f(*args, **kwargs):
            new_args = []

            for arg_idx, val in enumerate(args):
                if arg_idx in self._dict_keys:
                    new_args.append(DecoParamCaster.type_check(val, self._dict_keys[arg_idx]))
                else:
                    new_args.append(val)

            for key, val in kwargs.items():
                if key in self._dict_keys:
                    kwargs[key] = DecoParamCaster.type_check(val, self._dict_keys[key])
                else:
                    kwargs[key] = val

            return f(*new_args, **kwargs)

        return wrap_f

    @staticmethod
    def type_check(item: Any, type_: type = None):
        ret = item

        if isinstance(ret, ObjectId) and isinstance(type_, type) and not issubclass(type_, ObjectId):
            ret = str(ret)

        if type_ is not None and not isinstance(ret, type_):
            ret = type_(int(ret)) if issubclass(type_, FlagCodeMixin) else type_(ret)

        return ret
