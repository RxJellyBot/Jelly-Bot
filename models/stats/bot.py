"""Result model objects for bot usage stats."""
from collections import namedtuple
from datetime import datetime
from typing import Optional

from extutils.utils import enumerate_ranking
from flags import BotFeature
from models import OID_KEY
from strres.models import StatsResults

from .base import HourlyResult

__all__ = ("BotFeatureUsageResult", "BotFeaturePerUserUsageResult", "BotFeatureHourlyAvgResult")


# Fine for result objects to have 2 or less public methods
# pylint: disable=too-few-public-methods


class BotFeatureUsageResult:
    """
    Result of the bot feature usage stats.

    ``data`` will be sorted by its corresponding feature usage count (DESC) then its code (ASC).

    --------

    **Sample data**

    Including not used features (``incl_not_used`` is ``True``).

    ``BotFeature.TXT_AR_ADD`` was used 10 times.

    ``BotFeature.TXT_PING`` was used 5 times.

    --------

    **Sub-classes**

    ``FeatureUsageEntry``

    - ``feature_name`` (``str``): name of the feature acquired by calling ``BotFeature.key``

    - ``count`` (``int``): amount of times that a command was being used

    - ``rank`` (``str``): T-prefixed rank among all command usage

    --------

    **Fields**

    ``chart_label`` (``List[str]``)
        A list of feature acquired by calling ``BotFeature.key`` names for webpage rendering.

        Sample data output: ``["Auto Reply / Add", "Ping", "Auto Reply / Query", ...]``

    ``chart_data`` (``List[int]``)
        A list of the usage count corresponds to ``chart_lable`` for webpage rendering.

        Sample data output: ``[10, 5, 0, ..., 0]``

    ``data`` (``List[FeatureUsageEntry]``)
        A list of entries containing what feature was being used for how many times.

        This will sorted by the usage count (DESC) then the feature code (ASC).

        Sample data output::

            [0]: ("Auto Reply / Add", 10, "1"),
            [1]: ("Ping", 5, "2"),
            [2]: ("Auto Reply / Query", 0, "T3"),
            [3...]: ... (sorted by feature code)
    """

    KEY_COUNT = "count"

    def __init__(self, data, incl_not_used: bool):
        """
        Initalizing method of :class:`BotFeatureUsageResult`.

        :param data: aggregated data
        :param incl_not_used: to include the features that were not being used
        """
        FeatureUsageEntry = namedtuple("FeatureUsageEntry", ["feature_name", "count", "rank"])

        self.data = []

        for rank, entry in enumerate_ranking(data, is_tie=lambda cur, prv: cur[self.KEY_COUNT] == prv[self.KEY_COUNT]):
            raw_bot_feature = entry[OID_KEY]
            if feature := BotFeature.cast(raw_bot_feature, silent_fail=True):
                entry = FeatureUsageEntry(feature_name=feature.key, count=entry[self.KEY_COUNT], rank=rank)
                self.data.append(entry)

        if incl_not_used:
            diff = set(BotFeature).difference({BotFeature.cast(d[OID_KEY]) for d in data})
            diff.difference_update({BotFeature.UNDEFINED})

            last_rank = f"{'T' if len(diff) > 0 else ''}{len(self.data) + 1 if self.data else 1}"
            for diff_ in sorted(diff, key=lambda ftr: ftr.code):
                self.data.append(FeatureUsageEntry(feature_name=diff_.key, count=0, rank=last_rank))

        self.chart_label = [d.feature_name for d in self.data]
        self.chart_data = [d.count for d in self.data]


class BotFeaturePerUserUsageResult:
    """
    Result of the bot feature usage per user.

    --------

    **Sample data**

    - Member A used ``BotFeature.TXT_AR_ADD`` 10 times and ``BotFeature.TXT_PING`` 5 times

    - Member B used ``BotFeature.TXT_AR_ADD`` 20 times and ``BotFeature.TXT_PING`` 15 times

    --------

    **Fields**

    ``data`` (``Dict[ObjectId, Dict[BotFeature, int]]``)
        A :class:`dict` which key is the member OID and the value is another :class:`dict` of their feature usage.

        The value of the inner :class:`dict` is the bot feature usage count corresponding to its key.

        Sample data output::

            {
                (ID of member A): {
                    BotFeature.TXT_AR_ADD: 10,
                    BotFeature.TXT_PING: 5
                },
                (ID of member B): {
                    BotFeature.TXT_AR_ADD: 20,
                    BotFeature.TXT_PING: 15
                }
            }
    """

    KEY_FEATURE = "ft"
    KEY_UID = "uid"

    KEY_COUNT = "ct"

    def __init__(self, cursor):
        self.data = {}

        for data in cursor:
            uid = data[OID_KEY][BotFeaturePerUserUsageResult.KEY_UID]
            feature = BotFeature.cast(data[OID_KEY][BotFeaturePerUserUsageResult.KEY_FEATURE])

            if uid not in self.data:
                self.data[uid] = {feature: 0 for feature in BotFeature}

            self.data[uid][feature] = data[BotFeaturePerUserUsageResult.KEY_COUNT]


class BotFeatureHourlyAvgResult(HourlyResult):
    """
    Result of the hourly average bot feature usage stats.

    --------

    **Sample data**

    Including not used features (``incl_not_used`` is ``True``).

    Bot was used in 5 days with the following details:

    ``BotFeature.TXT_AR_ADD`` was used at AM 1 for 10 times and AM 2 for 15 times.

    ``BotFeature.TXT_PING`` was used at AM 1 for 20 times and AM 2 for 25 times.

    --------

    **Sub-classes**

    ``UsageEntry``

    Entry for the field ``data``. The entry is also being used to render the webpage.

    - ``feature`` (Union[:class:`BotFeature`, ``str``]): :class:`BotFeature` or the name for the total

    - ``data`` (``List[float]``): hourly average bot feature usage counts

    - ``color`` (``str``): color for the data series in the format of ``#AAAAAA``

        Default for total average is ``#323232``

        Default for category that was being used is ``#00A14B``

        Default for category that was **NOT** being used is ``#9C0000``

    - ``hidden`` (``str``): either ``true`` or ``false`` to set the default hidden property of the data

        Default for total average entry is ``false``

        Default for category-specific entry is ``true``

    --------

    **Fields**

    ``hr_range`` (``int``)
        Time length of the data being collected in hours.

        Sample data output: ``120``

    ``label_hr`` (``List[int]``)
        A list of numbers representing the hours in a day for webpage rendering.

        Sample data output: ``[0, 1, 2, ..., 23]``

    ``data`` (``List[UsageEntry]``)
        A list of entries containing each feature's hourly average usage count.

        This will sorted by the feature code (ASC).

        The first element of this will be the total average usage count among features.

        Sample data output::

            [0]: ("Total avg count", [0, 6, 8, ...], "#323232", "false"),
            [1]: ("Auto Reply / Add", [0, 2, 3, ...], "#00A14B", "true"),
            [2...]: entries which feature code is between AR/ADD and PING
            [x]: ("Ping", [0, 4, 5, ...], "#00A14B", "true"),
            [x + 1...]: ("Ping", [0, 0, 0, ...], "#9C0000", "false")...
    """

    KEY_FEATURE = "ft"
    KEY_HR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, incl_not_used: bool, days_collected: float, end_time: Optional[datetime] = None):
        super().__init__(days_collected, end_time=end_time)

        self.hr_range = int(days_collected * 24)
        self.label_hr = list(range(24))

        # `show` is `str` because it's for js
        UsageEntry = namedtuple("UsageEntry", ["feature", "data", "color", "hidden"])

        data_points = {}
        hr_sum = [0] * 24

        for data in cursor:
            feature = BotFeature.cast(data[OID_KEY][BotFeatureHourlyAvgResult.KEY_FEATURE])
            hour = data[OID_KEY][BotFeatureHourlyAvgResult.KEY_HR]

            if feature not in data_points:
                data_points[feature] = [0] * 24

            count = data[BotFeatureHourlyAvgResult.KEY_COUNT]

            data_points[feature][hour] = count
            hr_sum[hour] += count

        if self.avg_calculatable:
            hr_sum = [ct / dm for ct, dm in zip(hr_sum, self.denom)]
            data_points = {ft: [ct / dm for ct, dm in zip(data, self.denom)] for ft, data in data_points.items()}

        self.data = [UsageEntry(feature=ft, data=data, color="#00A14B", hidden="true")
                     for ft, data in data_points.items()]

        if incl_not_used:
            diff = {feature for feature in BotFeature if feature != BotFeature.UNDEFINED}.difference(data_points)
            for diff_ in diff:
                self.data.append(UsageEntry(feature=diff_, data=[0] * 24, color="#9C0000", hidden="true"))

        entry = UsageEntry(feature=StatsResults.CATEGORY_TOTAL, data=hr_sum, color="#323232", hidden="false")
        self.data = [entry] + list(sorted(self.data, key=lambda i: i.feature.code))
