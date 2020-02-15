from typing import List

from .response import Response
from .result import Result

PRODUCT_TARGET = ("53134238", "Anti-Viral Face Mask - 10ct - Up&Up™")
PRODUCT_WALGREENS1 = ("40000153109", "Walgreens Face Mask, Cone Style")
PRODUCT_WALGREENS2 = ("40000384673", "Walgreens Earloop-Style Face Mask")


def get_results(zip_code, target_range_mi, silent_fail=True) -> List[Result]:
    results = []
    results.extend(Response.get_target(zip_code, PRODUCT_TARGET, target_range_mi, silent_fail))
    results.extend(Response.get_walgreens(zip_code, PRODUCT_WALGREENS1, silent_fail))
    results.extend(Response.get_walgreens(zip_code, PRODUCT_WALGREENS2, silent_fail))

    return sorted(results, key=lambda x: x.distance)
