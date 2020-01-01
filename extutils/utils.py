import re
from typing import List, Tuple, Union, Generator, Any

from django.utils.translation import gettext_lazy as _


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
        return s[:max_ - len(suffix)] + suffix
    else:
        return s


def list_insert_in_between(l: list, insert_obj):
    ret = l.copy()

    for i in range(1, len(ret) * 2 - 2, 2):
        ret[i:i] = [insert_obj]

    return ret


def rotate_list(l: List, n: int):
    """`n` means elements to rotate from left to right"""
    n = int(n)
    return l[n:] + l[:n]


def char_description(c: str):
    if c == "\n":
        return _("(Newline)")
    elif c == " ":
        return _("(Space)")
    else:
        return c


def enumerate_ranking(iterable, start=1, t_prefix=True, is_equal: callable = lambda cur, prv: cur == prv) -> \
        Generator[Tuple[Union[int, str], Any], None, None]:
    _null_ = object()

    iterator = iter(iterable)

    prev = next(iterator, _null_)
    rank = start
    temp = []

    while prev != _null_:
        curr = next(iterator, _null_)

        while curr != _null_ and is_equal(curr, prev):
            temp.append(prev)

            prev = curr
            curr = next(iterator, _null_)

        for d in temp:
            yield f"T{rank}" if t_prefix else rank, d

        if len(temp) > 0:
            yield f"T{rank}" if t_prefix else rank, prev
        else:
            yield str(rank) if t_prefix else rank, prev

        rank += 1 + len(temp)
        prev = curr

        temp = []
