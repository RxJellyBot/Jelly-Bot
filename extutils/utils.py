import re
from datetime import datetime
from typing import List, Tuple, Union, Generator, Any, Optional
import html

from bson import ObjectId
from django.utils.translation import gettext_lazy as _


def cast_keep_none(obj, dest_type: type):
    """Cast ``obj`` to ``dest_type``. If ``obj`` is ``None``, let it be ``None``."""
    if obj is not None:
        if issubclass(dest_type, bool):
            return dest_type(int(obj))
        else:
            return dest_type(obj)
    else:
        return None


def cast_iterable(iterable: Union[List, Tuple], dest_type):
    """
    Cast ``iterable`` to ``List[dest_type]``.

    Can be performed on a nested list.

    If ``iterable`` is not :class:`list` or :class:`tuple`, then directly cast ``iterable`` to ``dest_type``.
    """
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
    Will NOT modify the ``o`` itself.

    Do the following corresponding to its type:

    :class:`str`
        > return the lower case of :class:`str`.
    :class:`tuple`, :class:`list`, :class:`set`
        > return the corresponding data structure
        which every element with a :class:`str` content will be lowered.
    :class:`dict`
        > return lowered case of data which is the value of a pair.
    (Not matching the above)
        > return the original ``o``
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
        for k, v in tmp.items():
            tmp[k] = all_lower(v)

        return tmp
    else:
        return o


def to_snake_case(s: str):
    return re.sub(r"(?!^)([A-Z]+)", r"_\1", s).lower()


def to_camel_case(s: str):
    return ''.join(x[0].upper() + x[1:] for x in s.split('_') if x)


def split_fill(s: str, n: int, *, delim="", fill=None):
    """
    Split the string ``s`` with delimeter ``delim`` into pieces which minimum is ``n``.

    If splitted element count is < ``n``.
        > Fill the rest of the count with ``fill``
    If splitted element count is > ``n``.
        > Truncate the splitted element list to ``n`` elements.
    """
    return ((s.split(delim) if s else []) + [fill] * n)[:n]


def str_reduce_length(s: str, max_: int, *, escape_html=False, suffix: str = "..."):
    """
    Reduce the length of ``s`` to ``max_`` including the length of ``suffix``.

    HTML escape performed after the length reduction.
    :exception ValueError: suffix length > max content length
    """
    if len(suffix) > max_:
        raise ValueError("Suffix length > max content length is invalid.")

    if len(s) > max_:
        s = s[:max_ - len(suffix)] + suffix

    if escape_html:
        s = html.escape(s)

    return s


def list_insert_in_between(lst: list, insert_obj):
    """Insert ``insert_obj`` as an element between every elements of the ``lst``."""
    ret = lst.copy()

    for i in range(1, len(ret) * 2 - 2, 2):
        ret[i:i] = [insert_obj]

    return ret


def char_description(c: str):
    if c == "\n":
        return _("(Newline)")
    elif c == " ":
        return _("(Space)")
    else:
        return c


def enumerate_ranking(iterable_sorted, start=1, t_prefix=True, is_tie: callable = lambda cur, prv: cur == prv) -> \
        Generator[Tuple[Union[int, str], Any], None, None]:
    # noinspection PyUnresolvedReferences
    """
    Generates the ranking and the corresponding data in ``iterable_sorted``.

    If ``t_prefix`` is ``True``, the ranking

    Example:

    >>> for rank, data in enumerate_ranking(["A", "C", "C", "E"]):
    >>>     print(f"{rank} - {data}")

    Output:

    >>> 1 - A
    >>> T2 - C
    >>> T2 - C
    >>> 4 - E

    :param iterable_sorted: things to be ranked/iterated on
    :param start: starting index
    :param t_prefix: attach "T" in front of the ranking
    :param is_tie: lambda expression to check if the current and the previous item are the same
    """
    _null_ = object()

    iterator = iter(iterable_sorted)

    prev = next(iterator, _null_)
    rank = start
    temp = []

    while prev != _null_:
        curr = next(iterator, _null_)

        # Check tied
        while curr != _null_ and is_tie(curr, prev):
            temp.append(prev)

            prev = curr
            curr = next(iterator, _null_)

        # Add prefix if any is tied
        for d in temp:
            yield f"T{rank}" if t_prefix else rank, d

        if len(temp) > 0:
            yield f"T{rank}" if t_prefix else rank, prev
        else:
            yield str(rank) if t_prefix else rank, prev

        rank += 1 + len(temp)
        prev = curr

        temp = []


def dt_to_objectid(dt: Optional[datetime]):
    """Parse ``dt`` to :class:`ObjectId`. ``None`` if failed to convert."""
    try:
        return ObjectId.from_datetime(dt)
    except Exception:
        return None
