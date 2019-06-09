def cast_keep_none(target, type_: type):
    if target is not None:
        if issubclass(type_, bool):
            return type_(int(target))
        else:
            return type_(target)
    else:
        return None
