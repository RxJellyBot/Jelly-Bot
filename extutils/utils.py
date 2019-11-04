import re


def cast_keep_none(obj, dest_type: type):
    if obj is not None:
        if issubclass(dest_type, bool):
            return dest_type(int(obj))
        else:
            return dest_type(obj)
    else:
        return None


def safe_cast(obj, dest_type: type):
    """
    Executes type-cast safely.

    :param obj: Object to be casted.
    :param dest_type: Destination type.
    :return: Casted `obj`. Return `None` if failed.
    """
    try:
        return dest_type(obj)
    except Exception:
        return None


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


def to_snake_case(s: str):
    return re.sub(r"(?!^)([A-Z]+)", r"_\1", s).lower()


def to_camel_case(s: str):
    return ''.join(x[0].upper() + x[1:] if x else "_" for x in s.split('_'))


def split_fill(s: str, n: int, delim="", fill=None):
    return (s.split(delim) + [fill] * n)[:n]


def str_reduce_length(s: str, max_: int):
    suffix = "..."

    if len(s) > max_ - len(suffix):
        return s[:-3] + suffix
    else:
        return s


def list_insert_in_between(l: list, insert_obj):
    ret = l.copy()

    for i in range(1, len(ret) * 2 - 2, 2):
        ret[i:i] = [insert_obj]

    return ret
