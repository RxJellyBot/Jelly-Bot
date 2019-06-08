def cast_keep_none(target, type_: type):
    if target is not None:
        return type_(target)
    else:
        return None
