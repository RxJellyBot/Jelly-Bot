"""Game map resource manager."""
__all__ = ("get_map_template",)

_cache = {}


def get_map_template(name: str):
    """
    Get a map template by its ``name``.

    Returns ``None`` if not found.

    Loaded :class:`MapTemplate` will be cached until the application exits.

    :param name: name of the map template.
    :return: map template object if found
    """
    if name not in _cache:
        # On-demand import & avoid circular import
        from game.pkchess.map import MapTemplate

        _cache[name] = MapTemplate.load_from_file(f"game/pkchess/res/map/{name}")

    return _cache[name]
