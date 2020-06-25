from datetime import datetime

import pytz
from bson import ObjectId

from flags import MessageType
from models import MessageRecordModel
from mongodb.factory import MessageRecordStatisticsManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin

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
                               MessageType=MessageType.TEXT, MessageContent="DEF", ProcessTimeSecs=3.14),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 2, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="QRS", ProcessTimeSecs=7.18),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="GHI", ProcessTimeSecs=4.15),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 6, 4, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="JKL", ProcessTimeSecs=5.16),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 4, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="MNO", ProcessTimeSecs=6.17),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 4, 1, 1, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_OID_2, UserRootOid=self.USER_OID_2,
                               MessageType=MessageType.TEXT, MessageContent="QRS", ProcessTimeSecs=7.18)
        ]

        MessageRecordStatisticsManager.insert_many(mdls)

        return mdls

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

    # FIXME: Stats - Starts here

    def test_get_user_total_msg_count(self):
        pass

    def test_get_user_total_msg_count_timerange(self):
        pass

    def test_get_user_total_msg_count_param(self):
        pass

    def test_get_user_total_msg_count_timerange_start_before_channel(self):
        pass

    def test_get_user_total_msg_count_param_start_before_channel(self):
        pass

    def test_get_user_total_msg_count_with_tz(self):
        pass

    def test_get_user_total_msg_count_partial_channel_miss(self):
        pass

    def test_get_user_total_msg_count_channel_miss(self):
        pass
