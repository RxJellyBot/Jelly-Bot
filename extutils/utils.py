import re
from typing import List, Tuple, Union


def cast_keep_none(obj, dest_type: type):
    if obj is not None:
        if issubclass(dest_type, bool):
            return dest_type(int(obj))
        else:
            return dest_type(obj)
    else:
        return None


def cast_iterable(iterable: Union[List, Tuple], dest_type):
    if isinstance(iterable, (list, tuple)):
        ret = []

        for item in iterable:
            if isinstance(item, (list, tuple)):
                ret.append(cast_iterable(item, dest_type))
            else:
                ret.append(dest_type(item))

        return ret
    else:
        return dest_type(iterable)


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


def demarkdown(markdown_str: str):
    # OPTIMIZE: Regex?
    return markdown_str\
        .replace("\n\n", "\n")\
        .replace("<br>", "\n")\
        .replace("<br/>", "\n")\
        .replace("<hr>", "----------")\
        .replace("<pre>", "```")\
        .replace("</pre>", "```")


def rotate_list(l: List, n: int):
    """`n` means elements to rotate from left to right"""
    n = int(n)
    return l[n:] + l[:n]
