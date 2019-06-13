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
