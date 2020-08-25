"""Result model objects for message stats."""
from collections import namedtuple
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timedelta, date
from time import gmtime, strftime
from typing import Dict, Optional, List

from bson import ObjectId

from extutils.dt import TimeRange
from flags import MessageType
from models import OID_KEY  # pylint: disable=cyclic-import
from strres.models import StatsResults

from .base import HourlyResult, DailyResult

__all__ = ("HourlyIntervalAverageMessageResult", "DailyMessageResult", "MeanMessageResult",
           "MeanMessageResultGenerator", "MemberDailyMessageResult", "CountBeforeTimeResult",
           "MemberMessageCountEntry", "MemberMessageCountResult", "MemberMessageByCategoryEntry",
           "MemberMessageByCategoryResult")


# Fine for result objects to have 2 or less public methods
# pylint: disable=too-few-public-methods


class HourlyIntervalAverageMessageResult(HourlyResult):
    """
    Result object for hourly interval average message count.

    --------

    **Sample data**

    Messages being sent in the following times within 2 days:

    - Day 1 / AM 1 - 1 in TEXT, 2 in IMAGE

    - Day 1 / AM 2 - 3 in TEXT, 4 in IMAGE

    - Day 1 / AM 3 - 5 in TEXT, 6 in IMAGE

    - Day 2 / AM 1 - 7 in TEXT, 8 in IMAGE

    - Day 2 / AM 2 - 9 in TEXT, 0 in IMAGE

    - Day 2 / AM 3 - 1 in TEXT, 2 in IMAGE

    --------

    **Sub-classes**

    ``CountDataEntry`` (:class:`namedtuple`)

    Represents a single entry of the field ``count_data``.

    - ``category_name`` (``str``): name of the message category (``key`` of :class:`MessageType`)

    - ``data`` (``List[float]``): list of average hourly message count

    - ``color`` (``str``): color to be used for webpage output in the format of ``#AAAAAA``

        Default for total count is ``#323232``

        Default for category count is ``#777777``

    - ``hidden`` (``str``): either ``true`` or ``false`` to set the default hidden property of the data

        Default for total count is ``false``

        Default for category count is ``true``

    --------

    **Fields**

    ``label_hr`` (``List[int]``)
        A list of numbers (0 <= n < 24) for webpage rendering.

        Sample data output: ``[0, 1, ..., 23]``

    ``count_data`` (``List[CountDataEntry]``)
        A list of :class:`CountDataEntry` for each category of the stats.
        The first element of this list will be the sum of the message counts among various types of the messages.

        Sample data output::

            [0]: (Name for total count), [0, 9, 8, 7, ..., 0], "#323232", "false"
            [1]: (``key`` of :class:`MessageType.TEXT`), [0, 4, 6, 3, ..., 0], "#777777", "true"
            [2]: (``key`` of :class:`MessageType.IMAGE`), [0, 5, 2, 4, ..., 0], "#777777", "true"

    ``hr_range`` (``float``)
        Time length of the collected data in hours.

        Sample data output: ``48``
    """

    KEY_CATEGORY = "cat"
    KEY_HR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected: float, *, end_time: Optional[datetime] = None):
        """
        Initializing method of :class:`HourlyIntervalAverageMessageResult`.

        :param cursor: cursor of the aggregated data
        :param days_collected: "claimed" days collected of the data
        :param end_time: end time of the data. current time in UTC if not given
        """
        super().__init__(days_collected, end_time=end_time)

        CountDataEntry = namedtuple("CountDataEntry", ["category_name", "data", "color", "hidden"])

        # Create hours label for web page
        self.label_hr = list(range(24))

        count_data = {}
        count_sum = [0 for _ in range(24)]

        for entry in cursor:
            ctg = MessageType.cast(entry[OID_KEY][HourlyIntervalAverageMessageResult.KEY_CATEGORY])
            hour = entry[OID_KEY][HourlyIntervalAverageMessageResult.KEY_HR]

            if ctg not in count_data:
                count_data[ctg] = [0] * 24

            count = entry[HourlyIntervalAverageMessageResult.KEY_COUNT]
            count_data[ctg][hour] = count
            count_sum[hour] += count

        count_sum = [
            CountDataEntry(
                category_name=StatsResults.CATEGORY_TOTAL,
                data=[ct / dm for ct, dm in zip(count_sum, self.denom)] if self.avg_calculatable else count_sum,
                color="#323232",
                hidden="false"  # Will be used in JS so string of bool instead
            )
        ]
        count_data = [
            CountDataEntry(
                category_name=cat.key,
                data=[ct / dm for ct, dm in zip(data, self.denom)] if self.avg_calculatable else data,
                color="#777777",
                hidden="true"  # Will be used in JS so string of bool instead
            )
            for cat, data in sorted(count_data.items(), key=lambda item: item[0].code)
        ]

        self.data = count_sum + count_data

        self.hr_range = round(days_collected * 24)


class DailyMessageResult(DailyResult):
    """
    Result object for daily message count.

    --------

    **Sample data**

    Messages being sent as follows:

    - Day 1: ``10``, where ``3`` at AM 1 and ``7`` at AM 2

    - Day 2: ``20``, where ``11`` at AM 1 and ``9`` at AM 2

    - Day 3: ``30``, where ``15`` at AM 1 and ``15`` at AM 2

    - Day 4: ``40``, where ``28`` at AM 1 and ``12`` at AM 2

    --------

    **Sub-classes**

    ``DataPoint``

    Represents the stats of a certain time.

    - ``count`` (``int``): message count at the certain time

    - ``percentage`` (``float``): count ratio comparing to the count of a day

    - ``is_max`` (``bool``): if the data point has the maximum value in a day

    ``ResultEntry``

    Act as an entry for the field ``data``.

    - ``date`` (``str``): corresponding date in ``str``

    - ``data`` (``DataPoint``): a data point containing the stats at a certain time

    --------

    **Fields**

    ``label_hr`` (``List[int]``)
        A list of numbers (0 <= n < 24) for webpage rendering.

        Sample data output: ``[0, 1, ..., 23]``

    ``label_date`` (``List[str``)
        A list of dates in :class:`str` for webpage rendering.

        Sample data output: ``["Day 1", "Day 2", "Day 3", "Day 4"]``

    ``data_sum`` (``List[int]``)
        A list of daily total message count.

        Sample data output: ``[10, 20, 30, 40]``

    ``data`` (``List[ResultEntry]``)
        List of the detailed stats as :class:`ResultEntry`.

        Sample data output::

            [0]: ("Day 1", [(0, 0, False), (3, 0.3, False), (7, 0.7, True), (0, 0, False), ...])
            [1]: ("Day 2", [(0, 0, False), (11, 0.55, True), (9, 0.45, False), (0, 0, False), ...])
            [2]: ("Day 3", [(0, 0, False), (15, 0.5, True), (15, 0.5, True), (0, 0, False), ...])
            [3]: ("Day 4", [(0, 0, False), (28, 0.7, True), (12, 0.3, False), (0, 0, False), ...])
    """

    KEY_HOUR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *,
                 start: Optional[datetime] = None, end: Optional[datetime] = None):
        """
        Initializing method of :class:`DailyMessageResult`.

        :param cursor: cursor of the aggregated data
        :param days_collected: "claimed" days collected of the data
        :param tzinfo: timezone info to be used for separating the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        """
        # pylint: disable=too-many-locals

        DataPoint = namedtuple("DataPoint", ["count", "percentage", "is_max"])
        ResultEntry = namedtuple("ResultEntry", ["date", "data"])

        self.label_hr = list(range(24))
        self.label_date = self.date_list_str(days_collected, tzinfo, start=start, end=end)

        data_sum = {dt: 0 for dt in self.label_date}
        data = {dt: [0] * 24 for dt in self.label_date}

        for entry in cursor:
            date_ = entry[OID_KEY][DailyMessageResult.KEY_DATE]
            hour = entry[OID_KEY][DailyMessageResult.KEY_HOUR]

            count = entry[DailyMessageResult.KEY_COUNT]

            data[date_][hour] += count
            data_sum[date_] += count

        for dt, pts in data.items():
            sum_ = sum(pts)
            max_ = max(pts)

            if sum_ > 0:
                data[dt] = [DataPoint(count=dp, percentage=dp / sum_ * 100, is_max=max_ == dp) for dp in pts]
            else:
                data[dt] = [DataPoint(count=dp, percentage=0.0, is_max=False) for dp in pts]

        self.data_sum = [data_sum[k] for k in
                         sorted(data_sum, key=lambda x: datetime.strptime(x, DailyResult.FMT_DATE))]
        self.data = [ResultEntry(date=date_, data=data[date_])
                     for date_ in sorted(data, key=lambda x: datetime.strptime(x, DailyResult.FMT_DATE))]

        # pylint: enable=too-many-locals


class MeanMessageResult:
    """
    Result object generated by :class:`MeanMessageResultGenerator`.

    --------

    **Sample data**

    Using the sample data for :class:`MeanMessageResultGenerator`.

    Generated this with ``mean_days`` as ``3`` using ``generate_result()``.

    --------

    **Fields**

    ``date_list`` (``List[date]``)
        List of :class:`date` corresponds to the calculated result in ``data_list``.

        This should have the same length with ``data_list``.

        Sample data output: ``[Day 7, Day 8, Day 9]``

    ``data_list`` (``List[float]``)
        List of the calculated mean message count results.

        This should have the same length with ``date_list``.

        Sample data output: ``[60.0, 70.0, 80.0]``

    ``mean_days`` (``int``)
        Mean days used to request this result.

        Sample data output: ``3``
    """

    def __init__(self, date_list: List[date], data_list: List[float], mean_days: int):
        """
        Initializing method of :class:`MeanMessageResult`.

        :param date_list: list of `date` for webpage rendering
        :param data_list: list of `float` represents the mean days count of the corresponding date
        :param mean_days: count of days used to calculate the mean result
        """
        self.date_list = date_list
        self.data_list = data_list
        self.label = StatsResults.DAYS_MEAN.format(mean_days)


class MeanMessageResultGenerator(DailyResult):
    """
    Result object for mean days message count.

    --------

    **Sample data**

    Assume that the messages were sent as follows, and ``max_mean_days`` are set to ``5``:

    - Day 1: 10

    - Day 2: 20

    ...

    - Day 5: 50

    ...

    - Day 9: 90

    --------

    **Sub-classes**

    :class:`MeanMessageResult`

    Generated result by calling ``generate_result()``. Check the documentation for more details.

    --------

    **Fields**

    ``max_madays`` (``int``)
        Max mean days that the generator could give a result.

        Sample data output: ``5``

    ``trange`` (:class:`TimeRange`)
        Time range of the input data.

        Sample data output: (:class:`TimeRange` that starts 5 days ago and ends at the current time)

    ``dates`` (``List[date]``)
        List of :class:`date` of the data based on ``trange``.

        Sample data output: ``[Day 1, Day 2, ..., Day 9]``

    ``data`` (``Dict[date, int]``)
        Raw data to be used to generate a :class:`MeanMessageResult`.

        Sample data output::

            {
                Day 1: 10,
                Day 2: 20,
                ...
                Day 5: 50,
                ...
                Day 9: 90
            }
    """

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange, max_mean_days: int):
        """
        Initializing method of :class:`MeanMessageResultGenerator`.

        :param cursor: cursor of the aggregated data
        :param days_collected: "claimed" days collected on the data
        :param tzinfo: timezone info to separate the data by their date
        :param trange: time range of the data
        :param max_mean_days: maximum mean days that the generator can generate
        """
        self.max_madays = max_mean_days

        if trange.is_inf:
            self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
            self.trange.set_start_day_offset(-max_mean_days)
        else:
            self.trange = trange

        self.dates = self.date_list(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)
        self.data = {date_: 0 for date_ in self.dates}

        for entry in cursor:
            date_ = datetime.strptime(entry[OID_KEY][MeanMessageResultGenerator.KEY_DATE], DailyResult.FMT_DATE).date()
            count = entry[MeanMessageResultGenerator.KEY_COUNT]

            self.data[date_] += count

    def generate_result(self, mean_days: int) -> MeanMessageResult:
        """
        Generate the mean message count result based on ``mean_days``.

        :param mean_days: days to calculate the mean message count
        :return: a `MeanMessageResult` containing the calculated results
        :raises ValueError: if `mean_days` is greater than the maximum mean days of this generator OR <= 0
        """
        if mean_days > self.max_madays:
            raise ValueError("Max mean average calculation range reached.")
        if mean_days <= 0:
            raise ValueError("`mean_days` should be > 0.")

        date_list = []
        data_list = []

        current_date = self.trange.start_org.date()
        end_date = self.trange.end.date()
        while current_date <= end_date:
            total = 0
            for i in range(mean_days):
                total += self.data.get(current_date - timedelta(days=i), 0)

            date_list.append(current_date)
            data_list.append(total / mean_days)

            current_date += timedelta(days=1)

        return MeanMessageResult(date_list, data_list, mean_days)


class MemberDailyMessageResult(DailyResult):
    """
    Result of daily message count for each members.

    --------

    **Sample data**

    - Day 1: Member A sent 10 messages, Member B sent 20 messages

    - Day 2: Member A sent 30 messages, Member B sent 40 messages

    - Day 3: Member A sent 50 messages, Member B sent 60 messages

    --------

    **Fields**

    ``trange`` (``TimeRange``)
        Time range of the data.

        Sample data output: (Time range from Day 1 to Day 3)

    ``dates`` (``List[str]``)
        List of dates in :class:`str` for webpage output.

        Sample data output: ``["Day 1", "Day 2", "Day 3"]``

    ``data_count`` (``Dict[str, Dict[ObjectId, int]]``)
        Message count of each members at the corresponding date.

        Sample data output::

            {
                "Day 1": {
                    (ID of member A): 10,
                    (ID of member B): 20
                },
                "Day 2": {
                    (ID of member A): 30,
                    (ID of member B): 40
                },
                "Day 3": {
                    (ID of member A): 50,
                    (ID of member B): 60
                }
            }
    """

    KEY_MEMBER = "mbr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange):
        """
        Initializing method of :class:`MemberDailyMessageResult`.

        :param cursor: cursor of the aggregated data
        :param days_collected: "claimed" days collected on the data
        :param tzinfo: timezone info to separate the data by their date
        :param trange: time range of the data
        """
        self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
        self.dates = self.date_list_str(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)
        self.data_count = {date_: {} for date_ in self.dates}
        for entry in cursor:
            _date_ = entry[OID_KEY][MemberDailyMessageResult.KEY_DATE]
            _member_ = entry[OID_KEY][MemberDailyMessageResult.KEY_MEMBER]
            _count_ = entry[MemberDailyMessageResult.KEY_COUNT]
            self.data_count[_date_][_member_] = _count_


class CountBeforeTimeResult(DailyResult):
    """
    Result of daily message count before a certain time.

    --------

    **Sample data**

    3 days of the data were collected as follows:

    - Day 1: 50 messages were sent before 11 PM

    - Day 2: 40 messages were sent before 11 PM

    - Day 3: 30 messages were sent before 11 PM

    --------

    **Fields**

    ``trange`` (``TimeRange``)
        Time range of the data.

        Sample data output: (Time range from Day 1 to Day 3)

    ``dates`` (``List[str]``)
        List of dates in :class:`str` for webpage output.

        Sample data output: ``["Day 1", "Day 2", "Day 3"]``

    ``data_count`` (``List[int]``)
        List of integers represents the total message count before a certain time.

        Sample data output: ``[50, 40, 30]``
    """

    KEY_SEC_OF_DAY = "sd"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange):
        self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
        self.dates = self.date_list_str(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)

        self.data_count = {date_: 0 for date_ in self.dates}
        for entry in cursor:
            _date_ = entry[OID_KEY][CountBeforeTimeResult.KEY_DATE]
            _count_ = entry[CountBeforeTimeResult.KEY_COUNT]
            self.data_count[_date_] = _count_

        self.data_count = list(self.data_count.values())

    @property
    def title(self):
        """
        Get the title of the result in the format or ``%I:%M:%S %p``.

        :return: title of the result
        """
        return StatsResults.COUNT_BEFORE.format(strftime("%I:%M:%S %p", gmtime(self.trange.end_time_seconds)))


# region MemberMessageCountResult


@dataclass
class MemberMessageCountEntry:
    """
    Entry of :class:`MemberMessageCountResult`.

    --------

    **Sample data**

    Member A in the sample data of :class:`MemberMessageCountResult`.

    --------

    **Fields**

    ``count`` (``List[int]``)
        A list of numbers representing the message count in each interval.

        Sample data output: ``[5, 10, 15]``
    """

    intervals: InitVar[int]
    count: List[int] = field(init=False)

    def __post_init__(self, intervals: int):
        """
        Post init method of :class:`MemberMessageCountEntry`.

        :param intervals: count of the intervals
        """
        self.count = [0] * intervals

    @property
    def total(self) -> int:
        """
        Get the total message count.

        :return: total message count
        """
        return sum(self.count)


class MemberMessageCountResult:
    """
    Result of the member message count in different intervals.

    --------

    **Sample data**

    Day 1-2 as interval #1 ; Day 3-4 as interval #2 ; Day 5-6 as interval #3

    - Member A sent 5, 10, 15 messages in interval #1, #2, #3

    - Member B sent 20, 25, 30 messages in interval #1, #2, #3

    --------

    **Sub-classes**

    :class:`MemberMessageCountEntry`

    Represents an entry of the field ``data``. Check the documentation for more details.

    --------

    **Fields**

    ``trange`` (``TimeRange``)
        Time range used to query the data).

        Sample data output: (time range from Day 1 to Day 6 with range multiplier 3 applied)

    ``interval`` (``int``)
        Intervals recorded in the result.

        Sample data output: ``3``

    ``data`` (``Dict[ObjectId, MemberMessageCountEntry]``)
        A :class:`dict` which key is the member OID and value is the data entry.

        Sample data output::

            {
                (ID of member A): (`MemberMessageCountEntry` with `count`: [5, 10, 15]),
                (ID of member B): (`MemberMessageCountEntry` with `count`: [20, 25, 30])
            }
    """

    KEY_MEMBER_ID = "uid"
    KEY_INTERVAL_IDX = "idx"

    KEY_COUNT = "ct"

    def __init__(self, cursor, interval: int, trange: TimeRange):
        self.trange = trange

        self.interval = interval
        self.data: Dict[ObjectId, MemberMessageCountEntry] = {}

        for entry in cursor:
            uid = entry[OID_KEY][MemberMessageCountResult.KEY_MEMBER_ID]
            idx = int(entry[OID_KEY].get(MemberMessageCountResult.KEY_INTERVAL_IDX, interval - 1))

            if uid not in self.data:
                self.data[uid] = MemberMessageCountEntry(interval)

            count = entry[MemberMessageByCategoryResult.KEY_COUNT]

            self.data[uid].count[idx] = count


# endregion


# region MemberMessageByCategoryResult


@dataclass
class MemberMessageByCategoryEntry:
    """
    Entry of :class:`MemberMessageByCategoryResult`.

    --------

    **Sample data**

    Member A in the sample data of :class:`MemberMessageByCategoryResult`.

    --------

    **Fields**

    ``data`` (``Dict[MessageType, int]``)
        A :class:`dict` which key is the message type and value is the message count.

        Sample data output::

            {
                MessageType.TEXT: 5,
                MessageType.IMAGE: 10,
                (Other message types): 0
            }
    """

    label_category: InitVar[List[MessageType]]
    data: Optional[Dict[MessageType, int]] = None
    total: int = field(init=False)

    def __post_init__(self, label_category):
        if not self.data:
            self.data = {lbl: 0 for lbl in label_category}

        self.total = sum(self.data.values())

    def add(self, category: MessageType, count: int):
        """
        Add the message ``count`` to its corresponding ``category`` to ``data``.

        :param category: category of the message count
        :param count: message count to be added
        :raises ValueError: if the given `category` is not initialized in the data dict (unhandled)
        """
        if category not in self.data:
            raise ValueError("Message type not initialized in the data dict.")

        self.data[category] += count
        self.total += count

    def get_count(self, category: MessageType):
        """
        Get the message count of ``category``.

        If the :class:`MessageType` is not defined in ``data``, returns 0.

        :param category: message count of the category to get
        :return: message count of `category`, 0 if not dfefined in `data`
        """
        return self.data.get(category, 0)


class MemberMessageByCategoryResult:
    """
    Result of the member message count categorized by the message count.

    --------

    **Sample data**

    - Member A: 5 ``TEXT``, 10 ``IMAGE`` messages.

    - Member B: 15 ``TEXT``, 20 ``IMAGE`` messages.

    --------

    **Sub-classes**

    :class:`MemberMessageByCategoryEntry`

    Represents an entry of the field ``data``. Check the documentation for more details.

    --------

    **Fields**

    ``data`` (``Dict[ObjectId, MemberMessageCountEntry]``)
        A :class:`dict` which key is the member OID and value is the data entry.

        Sample data output::

            {
                (ID of member A): (`MemberMessageCountEntry` with `count`: [5, 10, 15]),
                (ID of member B): (`MemberMessageCountEntry` with `count`: [20, 25, 30])
            }

    .. note::
        Label categories (``LABEL_CATEGORY``) are manually listed so that the order on the webpage can be customized
        without furthur implementations.
    """

    KEY_MEMBER_ID = "uid"
    KEY_CATEGORY = "cat"

    KEY_COUNT = "ct"

    # Manually listing this to create custom order without additional implementations
    LABEL_CATEGORY = [
        MessageType.TEXT, MessageType.LINE_STICKER, MessageType.IMAGE, MessageType.VIDEO,
        MessageType.AUDIO, MessageType.LOCATION, MessageType.FILE
    ]

    def __init__(self, cursor):
        """
        Initializing method of :class:`MemberMessageByCategoryResult`.

        :param cursor: cursor of the aggregated data
        """
        self.data = {}

        for entry in cursor:
            uid = entry[OID_KEY][MemberMessageByCategoryResult.KEY_MEMBER_ID]
            cat = MessageType.cast(entry[OID_KEY][MemberMessageByCategoryResult.KEY_CATEGORY])

            if uid not in self.data:
                self.data[uid] = self.gen_new_data_entry()

            count = entry[MemberMessageByCategoryResult.KEY_COUNT]

            self.data[uid].add(cat, count)

    def gen_new_data_entry(self):
        """
        Generate a new :class:`MemberMessageByCategoryEntry` and return it.

        The purpose of this is to make sure that the new entry has the defined label categories defined
        in :class:`LABEL_CATEGORY`.

        :return: an initialized `MemberMessageByCategoryEntry`
        """
        return MemberMessageByCategoryEntry(self.LABEL_CATEGORY)

# endregion


# pylint: enable=too-few-public-methods
