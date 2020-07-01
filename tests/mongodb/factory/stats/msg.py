from datetime import datetime

import pytz
from bson import ObjectId

from extutils.locales import LocaleInfo
from flags import MessageType
from models import (
    MessageRecordModel, MemberMessageCountEntry
)
from models.stats import MemberMessageByCategoryEntry
from mongodb.factory import MessageRecordStatisticsManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin
from strres.models import StatsResults

__all__ = ["TestMessageRecordStatisticsManager"]


class TestMessageRecordStatisticsManager(TestTimeComparisonMixin, TestModelMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    CHANNEL_OID_3 = ObjectId()
    CHANNEL_OID_4 = ObjectId()

    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [MessageRecordStatisticsManager]

    def test_record_stats(self):
        self.assertEqual(
            MessageRecordStatisticsManager.record_message(
                self.CHANNEL_OID, self.USER_OID, MessageType.TEXT, "ABC", 2.13),
            WriteOutcome.O_INSERTED
        )

        self.assertModelEqual(
            MessageRecordStatisticsManager.find_one_casted(parse_cls=MessageRecordModel),
            MessageRecordModel(ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID, MessageType=MessageType.TEXT,
                               MessageContent="ABC", ProcessTimeSecs=2.13)
        )

    def _insert_messages(self):
        mdls = [
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="ABC", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="QRS", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.IMAGE, MessageContent="DEF", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="QRS", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.IMAGE, MessageContent="GHI", ProcessTimeSecs=4.15),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 4, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.LINE_STICKER, MessageContent="JKL", ProcessTimeSecs=5.16),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 4, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="MNO", ProcessTimeSecs=6.17),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 4, 1, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.IMAGE, MessageContent="QRS", ProcessTimeSecs=7.18)
        ]

        MessageRecordStatisticsManager.insert_many(mdls)

        return mdls

    def test_get_recent(self):
        mdls = self._insert_messages()

        self.assertModelSequenceEqual(
            MessageRecordStatisticsManager.get_recent_messages(self.CHANNEL_OID),
            list(reversed(mdls[0:6]))
        )
        self.assertModelSequenceEqual(
            MessageRecordStatisticsManager.get_recent_messages(self.CHANNEL_OID_2),
            list(reversed(mdls[6:8]))
        )

    def test_get_recent_limited(self):
        mdls = self._insert_messages()

        self.assertModelSequenceEqual(
            MessageRecordStatisticsManager.get_recent_messages(self.CHANNEL_OID, 2),
            list(reversed(mdls[4:6]))
        )
        self.assertModelSequenceEqual(
            MessageRecordStatisticsManager.get_recent_messages(self.CHANNEL_OID, 1),
            [mdls[5]]
        )

    def test_get_recent_channel_miss(self):
        self._insert_messages()

        self.assertModelSequenceEqual(MessageRecordStatisticsManager.get_recent_messages(ObjectId()), [])

    def test_get_recent_no_data(self):
        self.assertModelSequenceEqual(MessageRecordStatisticsManager.get_recent_messages(self.CHANNEL_OID), [])

    def test_get_msg_freq(self):
        msgs = self._insert_messages()

        self.assertAlmostEqual(
            MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID),
            (3 * 1440) / sum(map(lambda item: item.channel_oid == self.CHANNEL_OID, msgs))
        )
        self.assertAlmostEqual(
            MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID_2),
            60 / sum(map(lambda item: item.channel_oid == self.CHANNEL_OID_2, msgs))
        )

    def test_get_msg_freq_limited(self):
        self._insert_messages()

        self.assertAlmostEqual(MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID, 1440), 0)
        self.assertAlmostEqual(MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID_2, 1440), 0)

    def test_get_msg_freq_no_msg(self):
        self.assertEqual(MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID), 0)
        self.assertEqual(MessageRecordStatisticsManager.get_message_frequency(self.CHANNEL_OID_2), 0)

    def test_get_user_last_ts(self):
        self._insert_messages()

        tzinfo = pytz.timezone("US/Central")

        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                self.CHANNEL_OID, [self.USER_OID, self.USER_OID_2], tzinfo_=tzinfo
            ),
            {
                self.USER_OID: datetime(2020, 6, 4, tzinfo=pytz.utc).astimezone(tzinfo),
                self.USER_OID_2: datetime(2020, 6, 2, 1, tzinfo=pytz.utc).astimezone(tzinfo)
            }
        )

    def test_get_user_last_ts_no_tz(self):
        self._insert_messages()

        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                self.CHANNEL_OID, [self.USER_OID, self.USER_OID_2]
            ),
            {
                self.USER_OID: datetime(2020, 6, 4, tzinfo=pytz.utc),
                self.USER_OID_2: datetime(2020, 6, 2, 1, tzinfo=pytz.utc)
            }
        )

    def test_get_user_last_ts_partial_user_miss(self):
        self._insert_messages()

        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                self.CHANNEL_OID, [self.USER_OID, ObjectId()]
            ),
            {
                self.USER_OID: datetime(2020, 6, 4, tzinfo=pytz.utc)
            }
        )

    def test_get_user_last_ts_user_miss(self):
        self._insert_messages()

        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                self.CHANNEL_OID, [ObjectId(), ObjectId()]
            ),
            {}
        )

    def test_get_user_last_ts_channel_miss(self):
        self._insert_messages()

        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                ObjectId(), [self.USER_OID, self.USER_OID_2]
            ),
            {}
        )

    def test_get_user_last_ts_no_data(self):
        self.assertEqual(
            MessageRecordStatisticsManager.get_user_last_message_ts(
                ObjectId(), [self.USER_OID, self.USER_OID_2]
            ),
            {}
        )

    def test_get_user_total_msg_count_single_channel(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count(self.CHANNEL_OID)

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 4]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 2]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_multi_channel(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count([self.CHANNEL_OID, self.CHANNEL_OID_2])

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 5]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 3]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_start_before_first(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count(
            self.CHANNEL_OID, start=datetime(2020, 5, 1))

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 4]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 2]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_start_after_first(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count(
            self.CHANNEL_OID, start=datetime(2020, 6, 2, tzinfo=pytz.utc))

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 1, 3]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 1, 1]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_with_tz(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count(
            self.CHANNEL_OID, start=datetime(2020, 5, 1, tzinfo=pytz.utc), tzinfo_=pytz.utc)

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 4]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 2]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_partial_channel_miss(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count([self.CHANNEL_OID, ObjectId()])

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 4]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 2]
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_total_msg_count_channel_miss(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_total_count(
            ObjectId(), start=datetime(2020, 5, 1, tzinfo=pytz.utc), tzinfo_=pytz.utc)

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 0]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 0]
        self.assertEqual(result.data, {})

    def test_get_user_total_msg_count_no_data(self):
        result = MessageRecordStatisticsManager.get_user_messages_total_count(
            self.CHANNEL_OID, start=datetime(2020, 5, 1, tzinfo=pytz.utc), tzinfo_=pytz.utc)

        self.assertEqual(result.interval, 3)

        u1 = MemberMessageCountEntry(3)
        u1.count = [0, 0, 0]
        u2 = MemberMessageCountEntry(3)
        u2.count = [0, 0, 0]
        self.assertEqual(result.data, {})

    def test_get_user_msg_by_category_single_channel(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category(self.CHANNEL_OID)

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.TEXT, 1)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 2)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_multi_channel(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category([self.CHANNEL_OID, self.CHANNEL_OID_2])

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.TEXT, 2)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 2)
        u2.add(MessageType.IMAGE, 1)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_start_before_first(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category(
            self.CHANNEL_OID, start=datetime(2020, 5, 1))

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.TEXT, 1)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 2)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_start_after_first(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category(
            self.CHANNEL_OID, start=datetime(2020, 6, 2))

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 1)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_with_tz(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category(
            self.CHANNEL_OID, start=datetime(2020, 5, 1, tzinfo=pytz.utc), tzinfo_=pytz.utc)

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.TEXT, 1)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 2)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_partial_channel_miss(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category([self.CHANNEL_OID, ObjectId()])

        u1 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u1.add(MessageType.TEXT, 1)
        u1.add(MessageType.IMAGE, 2)
        u1.add(MessageType.LINE_STICKER, 1)

        u2 = MemberMessageByCategoryEntry(result.LABEL_CATEGORY)
        u2.add(MessageType.TEXT, 2)

        self.assertEqual(result.data[self.USER_OID], u1)
        self.assertEqual(result.data[self.USER_OID_2], u2)

    def test_get_user_msg_by_category_channel_miss(self):
        self._insert_messages()

        result = MessageRecordStatisticsManager.get_user_messages_by_category(ObjectId())

        self.assertEqual(result.data, {})

    def test_get_user_msg_by_category_no_data(self):
        result = MessageRecordStatisticsManager.get_user_messages_by_category(ObjectId())

        self.assertEqual(result.data, {})

    def _insert_messages_2(self):
        mdls = [
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="ABC", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="BCD", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_3, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="CDE", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_4, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="DEF", ProcessTimeSecs=7.18)
        ]

        MessageRecordStatisticsManager.insert_many(mdls)

        return mdls

    def test_get_msg_distinct_channel(self):
        self._insert_messages_2()

        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("ABC"),
            {self.CHANNEL_OID}
        )
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("BC"),
            {self.CHANNEL_OID, self.CHANNEL_OID_2}
        )
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("C"),
            {self.CHANNEL_OID, self.CHANNEL_OID_2, self.CHANNEL_OID_3}
        )

    def test_get_msg_distinct_channel_case_insensitive(self):
        self._insert_messages_2()

        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("abc"),
            {self.CHANNEL_OID}
        )
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("bc"),
            {self.CHANNEL_OID, self.CHANNEL_OID_2}
        )
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("c"),
            {self.CHANNEL_OID, self.CHANNEL_OID_2, self.CHANNEL_OID_3}
        )

    def test_get_msg_distinct_channel_no_match(self):
        self._insert_messages_2()

        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("z"),
            set()
        )

    def test_get_msg_distinct_channel_no_data(self):
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("ABC"),
            set()
        )
        self.assertEqual(
            MessageRecordStatisticsManager.get_messages_distinct_channel("abc"),
            set()
        )

    def _insert_messages_3(self):
        mdls = [
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M1", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 2, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="M2", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 2, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.IMAGE, MessageContent="M3", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.IMAGE, MessageContent="M4", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 1, 3, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M5", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="M6", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 2, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M7", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M8", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 3, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M9", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 3, 2, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.IMAGE, MessageContent="M10", ProcessTimeSecs=7.18)
        ]

        MessageRecordStatisticsManager.insert_many(mdls)

        return mdls

    def test_get_hr_avg_msg_single_channel(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID, start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 48)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 1, 1.5, 1.5] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 1, 1, 1] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 0.5, 0.5] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_multi_channel(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            [self.CHANNEL_OID, self.CHANNEL_OID_2],
            start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 48)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 1, 1.5, 2.5] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 1, 1, 1.5] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 0.5, 1] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_start_before_first(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID, start=datetime(2020, 5, 31, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 72)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 2 / 3, 1, 1] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 2 / 3, 2 / 3, 2 / 3] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 1 / 3, 1 / 3] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_start_after_first(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID, start=datetime(2020, 6, 2, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 24)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 1, 1, 1] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 1, 1, 1] + [0] * 20, "#777777", "true"),
            ]
        )

    def test_get_hr_avg_msg_end_at_middle(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID,
            start=datetime(2020, 6, 1, 2, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 46)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 0.5, 1.5, 1.5] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 0.5, 1, 1] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 0.5, 0.5] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_lt_24_hr(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID,
            start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 1, 23, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 23)
        self.assertFalse(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 1, 2, 2] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 1, 1, 1] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 1, 1] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_with_tz(self):
        self._insert_messages_3()

        tz = LocaleInfo.get_tzinfo("Asia/Taipei")

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID,
            start=datetime(2020, 6, 1, 8), end=datetime(2020, 6, 2, 8), tzinfo_=tz
        )

        self.assertEqual(result.hr_range, 24)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0] * 8 + [0, 1, 2, 2] + [0] * 12, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0] * 8 + [0, 1, 1, 1] + [0] * 12, "#777777", "true"),
                (MessageType.IMAGE.key, [0] * 8 + [0, 0, 1, 1] + [0] * 12, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_ts_with_tz(self):
        self._insert_messages_3()

        tz_8 = LocaleInfo.get_tzinfo("Asia/Taipei")
        tz_9 = LocaleInfo.get_tzinfo("Asia/Seoul")

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID,
            start=datetime(2020, 6, 1, 9, tzinfo=tz_9), end=datetime(2020, 6, 2, 9, tzinfo=tz_9), tzinfo_=tz_8
        )

        self.assertEqual(result.hr_range, 24)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0] * 8 + [0, 1, 2, 2] + [0] * 12, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0] * 8 + [0, 1, 1, 1] + [0] * 12, "#777777", "true"),
                (MessageType.IMAGE.key, [0] * 8 + [0, 0, 1, 1] + [0] * 12, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_partial_channel_miss(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            [self.CHANNEL_OID, ObjectId()],
            start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 48)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0, 1, 1.5, 1.5] + [0] * 20, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            [
                (MessageType.TEXT.key, [0, 1, 1, 1] + [0] * 20, "#777777", "true"),
                (MessageType.IMAGE.key, [0, 0, 0.5, 0.5] + [0] * 20, "#777777", "true")
            ]
        )

    def test_get_hr_avg_msg_channel_miss(self):
        self._insert_messages_3()

        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            ObjectId(),
            start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 48)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0] * 24, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            []
        )

    def test_get_hr_avg_msg_no_data(self):
        result = MessageRecordStatisticsManager.hourly_interval_message_count(
            self.CHANNEL_OID,
            start=datetime(2020, 6, 1, tzinfo=pytz.utc), end=datetime(2020, 6, 3, tzinfo=pytz.utc))

        self.assertEqual(result.hr_range, 48)
        self.assertTrue(result.avg_calculatable)
        self.assertEqual(
            result.data[0],
            (StatsResults.CATEGORY_TOTAL, [0] * 24, "#323232", "false")
        )
        self.assertEqual(
            result.data[1:],
            []
        )

    # TODO: Stats - daily_message_count / mean_message_count / message_count_before_time / member_daily_message_count

    def test_get_daily_msg_count(self):
        pass
