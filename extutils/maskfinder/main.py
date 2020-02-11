from typing import List

from .response import Response
from .result import Result

PRODUCT_TARGET = ("53134238", "Anti-Viral Face Mask - 10ct - Up&Up™")


def get_results(zip_code, target_range_mi, silent_fail=True) -> List[Result]:
    results = []
    results.extend(Response.get_target(zip_code, PRODUCT_TARGET, target_range_mi, silent_fail))

    return sorted(results, key=lambda x: x.distance)
