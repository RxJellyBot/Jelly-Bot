"""
Module of various EXTra / EXTernal utilities.
"""
# noinspection PyUnresolvedReferences
from .timing import exec_timing, exec_timing_ns, exec_timing_result
# noinspection PyUnresolvedReferences
from .utils import cast_keep_none, safe_cast, split_fill, char_description, dt_to_objectid
# noinspection PyUnresolvedReferences,PyPep8Naming
from .github import _inst as GithubWrapper
# noinspection PyUnresolvedReferences
from .singleton import Singleton, SingletonABC
