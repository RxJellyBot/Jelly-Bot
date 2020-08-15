import os

__all__ = ("is_testing",)


def is_testing() -> bool:
    return bool(int(os.environ.get("TEST", 0)))
