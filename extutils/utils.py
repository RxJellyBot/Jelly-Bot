"""
Module of the miscellaneous utilities.

Mostly transforming data of built-in basic data types such as :class:`str` and :class:`list`.
"""
# pylint: disable=C0103

import re
from datetime import datetime
from typing import List, Tuple, Union, Generator, Any, Optional, TypeVar, Type
import html

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

T = TypeVar("T")  # pylint: disable=C0103


def cast_keep_none(obj, dest_type: type):
    """
    Cast ``obj`` to ``dest_type``.

    If ``obj`` is ``None``, returns ``None``.

    :param obj: object to be casted
    :param dest_type: target type to cast `obj`
    :return: casted `obj`
    """
    if obj is None:
        return None

    if issubclass(dest_type, bool):
        return dest_type(int(obj))

    return dest_type(obj)


def cast_iterable(iterable: Union[List[T], Tuple[T]], dest_type: Type[T]):
    """
    Cast ``iterable`` to ``List[dest_type]`` or ``Tuple[dest_type]`` depending on the actual type of ``iterable``.

    Can be performed on a nested list.

    If ``iterable`` is not :class:`list` or :class:`tuple`, directly cast ``iterable`` to ``dest_type``.

    :param iterable: iterable to be casted
    :param dest_type: target type for the non-list non-tuple elements inside `iterable`
    :return: casted `iterable`
    """
    if not isinstance(iterable, (list, tuple)):
        return dest_type(iterable)

    ret = []

    for item in iterable:
        ret.append(cast_iterable(item, dest_type))

    if isinstance(iterable, tuple):
        return tuple(ret)

    return ret


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


def all_lower(o: Union[str, tuple, list, set, dict]) -> Union[str, tuple, list, set, dict]:
    """
    Lower the letter cases of all elements in ``obj``.

    Will **NOT** modify the ``o`` itself.

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

    :param o: object to lower the letter case
    :returns: an object with the same shape of `obj` but the letter case of the string elements are lowered
    """
    if isinstance(o, str):
        return o.lower()

    if isinstance(o, (tuple, list, set)):
        org_type = type(o)
        tmp = list(o)

        for idx, oo in enumerate(o):
            tmp[idx] = all_lower(oo)

        return org_type(tmp)

    if isinstance(o, dict):
        tmp = o.copy()
        for k, v in tmp.items():
            tmp[k] = all_lower(v)

        return tmp

    return o


def to_snake_case(s: str) -> str:
    """
    Convert camel-cased ``s`` to snake case.

    :param s: string to be converted
    :returns: `s` in snake case
    """
    return re.sub(r"(?!^)([A-Z]+)", r"_\1", s).lower()


def to_camel_case(s: str) -> str:
    """
    Convert snake-cased ``s`` to camel case.

    :param s: string to be converted
    :returns: `s` in camel case
    """
    return ''.join(x[0].upper() + x[1:] for x in s.split('_') if x)


def split_fill(s: str, n: int, *, delim="", fill=None) -> List[str]:
    """
    Split the string ``s`` with delimeter ``delim`` into pieces which minimum is ``n``.

    If splitted element count is < ``n``.
        > Fill the rest of the count with ``fill``
    If splitted element count is > ``n``.
        > Truncate the splitted element list to ``n`` elements.

    :param s: string to be splitted
    :param n: minimum number of the elements to be splitted
    :param delim: delimeter of the string
    :param fill: object to fill if necessary
    :return: list of `str` elements
    """
    return ((s.split(delim) if s else []) + [fill] * n)[:n]


def str_reduce_length(s: str, max_: int, *, escape_html=False, suffix: str = "...") -> str:
    """
    Reduce the length of ``s`` to ``max_`` including the length of ``suffix``.

    HTML escape performed after the length reduction.

    :param s: string to be reduced the length
    :param max_: max length of the string including the length of `suffix`
    :param escape_html: if the HTML characters should be escaped
    :param suffix: suffix of the string to be attached
    :return: truncated string
    :raises ValueError: suffix length > max content length
    """
    if len(suffix) > max_:
        raise ValueError("Suffix length > max content length is invalid.")

    if len(s) > max_:
        s = s[:max_ - len(suffix)] + suffix

    if escape_html:
        s = html.escape(s)

    return s


def list_insert_in_between(lst: list, insert_obj: Any) -> list:
    """
    Insert ``insert_obj`` as an element between every elements of the ``lst``.

    Example:

    >>> > list_insert_in_between([1, 2, 3], 0)
    >>> [1, 0, 2, 0, 3]

    :param lst: list to be inserted `insert_obj`
    :param insert_obj: object to be insert in between the elements of `lst`
    :return: list with `insert_obj` inserted in between the elements
    """
    ret = lst.copy()

    for i in range(1, len(ret) * 2 - 2, 2):
        ret[i:i] = [insert_obj]

    return ret


def char_description(c: str) -> str:
    r"""
    Get the character description of ``c``. If no matching description for ``c``, returns ``c``.

    Currently, there are only 2 special charcters have special description:

    - Newline (``\n``)

    - Space (``\x20``)

    :param c: character to get the description
    :return: description of the character `c`
    """
    if c == "\n":
        return _("(Newline)")

    if c == " ":
        return _("(Space)")

    return c


def enumerate_ranking(iterable_sorted, start=1, t_prefix=True, is_tie: callable = lambda cur, prv: cur == prv) -> \
        Generator[Tuple[Union[int, str], Any], None, None]:
    # noinspection PyUnresolvedReferences,PyShadowingNames
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
    :return: a generator yielding the current rank and the the current object
    """
    _null = object()

    iterator = iter(iterable_sorted)

    prev = next(iterator, _null)
    rank = start
    temp = []

    while prev != _null:
        curr = next(iterator, _null)

        # Check tied
        while curr != _null and is_tie(curr, prev):
            temp.append(prev)

            prev = curr
            curr = next(iterator, _null)

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


def dt_to_objectid(dt: Optional[datetime]) -> Optional[ObjectId]:
    """
    Parse ``dt`` to :class:`ObjectId`. Returns ``None`` if failed to convert.

    :param dt: datetime to be parsed into `ObjectId`
    :return: `ObjectId` for the speicific `dt`
    """
    try:
        return ObjectId.from_datetime(dt)
    except Exception:
        return None
