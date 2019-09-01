import re
from typing import Optional


def cast_keep_none(target, type_: type):
    if target is not None:
        if issubclass(type_, bool):
            return type_(int(target))
        else:
            return type_(target)
    else:
        return None


def is_empty_string(s: Optional[str]):
    return s is None or len(s) == 0


def all_lower(o: [str, tuple, list, set, dict]):
    """
    Will NOT modify the `o` itself.
    """
    if isinstance(o, str):
        return o.lower()
    elif isinstance(o, (tuple, list, set)):
        org_type = type(o)
        tmp = list(o)

        for idx, oo in enumerate(o):
            tmp[idx] = all_lower(oo)

        return org_type(tmp)
    elif isinstance(o, dict):
        tmp = o.copy()
        for k, v in tmp:
            tmp[k] = all_lower(v)

        return tmp
    else:
        return o


def safe_cast(obj, dest_type: type):
    """
    Execute type-cast safely.

    :param obj: Object to be casted.
    :param dest_type: Destination type.
    :return: Casted `obj`. Return `None` if failed.
    """
    try:
        return dest_type(obj)
    except Exception:
        return None


def to_snake_case(s: str):
    return re.sub(r"(?!^)([A-Z]+)", r"_\1", s).lower()


def to_camel_case(s: str):
    return ''.join(x[0].upper() + x[1:] if x else "_" for x in s.split('_'))
