"""
Main implementations for the US mask finder service.
"""
from typing import List

from .response import Response
from .result import MaskFindingResult

__all__ = ["get_results"]

PRODUCT_TARGET = ("53134238", "Anti-Viral Face Mask - 10ct - Up&Up™")
PRODUCT_WALGREENS1 = ("40000153109", "Walgreens Face Mask, Cone Style")
PRODUCT_WALGREENS2 = ("40000384673", "Walgreens Earloop-Style Face Mask")


def get_results(zip_code, target_range_mi, silent_fail=True) -> List[MaskFindingResult]:
    """
    Get the crawling results for the masks at ``zip_code`` within ``target_range_mi`` miles.

    :param zip_code: zip code to search
    :param target_range_mi: search range limit
    :param silent_fail: if the method should fail silently
    :return: mask finding results
    """
    results = []
    results.extend(Response.get_target(zip_code, PRODUCT_TARGET, target_range_mi, silent_fail))
    results.extend(Response.get_walgreens(zip_code, PRODUCT_WALGREENS1, silent_fail))
    results.extend(Response.get_walgreens(zip_code, PRODUCT_WALGREENS2, silent_fail))

    return sorted(results, key=lambda x: x.distance)
