from typing import List, Callable, TypeVar, Any

__all__ = ["extract_list_action"]

T = TypeVar("T")


def extract_list_action(data: T, fn: Callable[[List[T], Any], Any], *fn_args):
    """
    Extract ``data`` until the currently processing data becomes a 1D list, then perform ``fn`` on it.

    ``data`` might be mutated after this method, depending on the behavior of ``fn``.

    :param data: data to be extracted
    :param fn: function to be executed on the extracted 1D list
    :param fn_args: additional args for `fn`
    :return: `data` after performing `fn` on it
    """
    if data and isinstance(data, (list, tuple, set)) and isinstance(data[0], (list, tuple, set)):
        data_new = []

        for d in data:
            data_new.append(extract_list_action(d, fn, *fn_args))

        return data_new
    else:
        return fn(data, *fn_args)
