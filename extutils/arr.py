from typing import List, Callable, TypeVar, Any, Union

__all__ = ["extract_list_action", "extract_one"]

T = TypeVar("T")


def extract_one(obj: Union[list, tuple, set]):
    """
    Extract one element from ``obj``.

    :param obj: iterable to be extracted an element
    :return: an element extracted from `obj`
    :raise TypeError: obj type mismatch
    """
    if isinstance(obj, (list, tuple)):
        return obj[0] if len(obj) > 0 else None
    elif isinstance(obj, set):
        return obj.pop() if len(obj) > 0 else None
    else:
        raise TypeError(f"Type of `obj` must be one of `list`, `set` or `tuple`. (Actual: {type(obj)})")


def extract_list_action(data: T, fn: Callable[[List[T], Any], Any], *fn_args):
    """
    Extract ``data`` until the currently processing data becomes a 1D list, then perform ``fn`` on it.

    ``data`` might be mutated after this method, depending on the behavior of ``fn``.

    :param data: data to be extracted
    :param fn: function to be executed on the extracted 1D list
    :param fn_args: additional args for `fn`
    :return: `data` after performing `fn` on it
    """

    def is_iterable(obj):
        return isinstance(obj, (list, tuple, set))

    if data and is_iterable(data) and is_iterable(extract_one(data)):
        data_new = []

        for d in data:
            data_new.append(extract_list_action(d, fn, *fn_args))

        return data_new
    else:
        return fn(data, *fn_args)
