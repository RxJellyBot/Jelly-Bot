import abc
from datetime import datetime

from .base import TestCase


class TestTimeComparisonMixin(TestCase, abc.ABC):
    def assertTimeDifferenceLessEqual(self, a: datetime, b: datetime, diff_sec: float):
        a_ts = a.timestamp()
        b_ts = b.timestamp()
        t_diff = abs(a_ts - b_ts)

        if t_diff > diff_sec:
            self.fail(f"Time difference between {a} and {b} are greater than {diff_sec} secs. (Actual: {t_diff})")

    def assertTimeDifferenceGreaterEqual(self, a: datetime, b: datetime, diff_sec: float):
        a_ts = a.timestamp()
        b_ts = b.timestamp()
        t_diff = abs(a_ts - b_ts)

        if t_diff < diff_sec:
            self.fail(f"Time difference between {a} and {b} are less than {diff_sec} secs. (Actual: {t_diff})")
