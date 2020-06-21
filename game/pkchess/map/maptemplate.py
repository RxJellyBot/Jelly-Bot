__all__ = ["get_map_template"]

_cache = {}


def get_map_template(name: str):
    if name not in _cache:
        # On-demand import & avoid circular import
        from game.pkchess.objbase import MapTemplate

        _cache[name] = MapTemplate.load_from_file(f"game/pkchess/res/map/{name}")

    return _cache[name]
