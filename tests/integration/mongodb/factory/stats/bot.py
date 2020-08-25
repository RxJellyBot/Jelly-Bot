from datetime import datetime, timedelta

import pytz
from bson import ObjectId
from django.conf import settings

from extutils.emailutils import EmailServer
from extutils.locales import TWN
from flags import BotFeature
from models import BotFeatureUsageModel
from mongodb.factory import BotFeatureUsageDataManager
from strres.models import StatsResults
from tests.base import TestCase

__all__ = ("TestBotFeatureUsageDataManager",)


class TestBotFeatureUsageDataManager(TestCase):
    CREATION_TIME = pytz.utc.localize(datetime.utcnow())

    CHANNEL_OID_1 = ObjectId()
    CHANNEL_OID_2 = ObjectId()

    ROOT_OID_1 = ObjectId()
    ROOT_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [BotFeatureUsageDataManager, EmailServer]

    def test_record_usage(self):
        BotFeatureUsageDataManager.record_usage(BotFeature.TXT_AR_ADD, self.CHANNEL_OID_1, self.ROOT_OID_1)

        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_AR_ADD,
                BotFeatureUsageModel.ChannelOid.key: self.CHANNEL_OID_1,
                BotFeatureUsageModel.SenderRootOid.key: self.ROOT_OID_1
            }),
            1
        )

    def test_record_usage_undefined(self):
        BotFeatureUsageDataManager.record_usage(BotFeature.UNDEFINED, self.CHANNEL_OID_1, self.ROOT_OID_1)

        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 1)

    def _insert_usages(self):
        create_time = self.CREATION_TIME
        dup_3_5_oids = [
            str(ObjectId.from_datetime(create_time - timedelta(hours=3.5)))[:8] + "0" * 15 + format(num, "x")
            for num in range(5)
        ]

        BotFeatureUsageDataManager.insert_many([
            BotFeatureUsageModel(Id=ObjectId.from_datetime(self.CREATION_TIME - timedelta(hours=1.5)),
                                 Feature=BotFeature.TXT_AR_ADD,
                                 ChannelOid=self.CHANNEL_OID_1, SenderRootOid=self.ROOT_OID_1),
            BotFeatureUsageModel(Id=ObjectId.from_datetime(self.CREATION_TIME - timedelta(hours=2.5)),
                                 Feature=BotFeature.TXT_PING,
                                 ChannelOid=self.CHANNEL_OID_1, SenderRootOid=self.ROOT_OID_1),
            BotFeatureUsageModel(Id=dup_3_5_oids[0],
                                 Feature=BotFeature.TXT_AR_ADD,
                                 ChannelOid=self.CHANNEL_OID_1, SenderRootOid=self.ROOT_OID_1),
            BotFeatureUsageModel(Id=dup_3_5_oids[1],
                                 Feature=BotFeature.TXT_AR_ADD,
                                 ChannelOid=self.CHANNEL_OID_1, SenderRootOid=self.ROOT_OID_2),
            BotFeatureUsageModel(Id=dup_3_5_oids[2],
                                 Feature=BotFeature.TXT_AR_INFO,
                                 ChannelOid=self.CHANNEL_OID_1, SenderRootOid=self.ROOT_OID_2),
            BotFeatureUsageModel(Id=dup_3_5_oids[3],
                                 Feature=BotFeature.TXT_AR_ADD,
                                 ChannelOid=self.CHANNEL_OID_2, SenderRootOid=self.ROOT_OID_1),
            BotFeatureUsageModel(Id=dup_3_5_oids[4],
                                 Feature=BotFeature.TXT_AR_ADD,
                                 ChannelOid=self.CHANNEL_OID_2, SenderRootOid=self.ROOT_OID_2)
        ])

    def test_get_channel_usage(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_usage(self.CHANNEL_OID_1)

        self.assertEqual(
            result.data,
            [
                (BotFeature.TXT_AR_ADD.key, 3, "1"),
                (BotFeature.TXT_AR_INFO.key, 1, "T2"),
                (BotFeature.TXT_PING.key, 1, "T2")
            ]
        )

    def test_get_channel_usage_limit_time(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_usage(self.CHANNEL_OID_1, hours_within=3)

        self.assertEqual(
            result.data,
            [
                (BotFeature.TXT_AR_ADD.key, 1, "T1"),
                (BotFeature.TXT_PING.key, 1, "T1")
            ]
        )

    def test_get_channel_usage_incl_not_used(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_usage(self.CHANNEL_OID_1, incl_not_used=True)

        self.assertEqual(
            result.data,
            [
                (BotFeature.TXT_AR_ADD.key, 3, "1"),
                (BotFeature.TXT_AR_INFO.key, 1, "T2"),
                (BotFeature.TXT_PING.key, 1, "T2")
            ]
            + [
                (feature.key, 0, "T4")
                for feature in BotFeature
                if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_PING,
                                   BotFeature.TXT_AR_INFO, BotFeature.UNDEFINED)
            ]
        )

    def test_get_channel_usage_channel_miss(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_usage(ObjectId())
        self.assertEqual(result.data, [])

    def test_get_channel_usage_no_data(self):
        result = BotFeatureUsageDataManager.get_channel_usage(self.CHANNEL_OID_1)
        self.assertEqual(result.data, [])

    @classmethod
    def _hourly_avg_gen_arr(cls, data):
        hr_split = cls.CREATION_TIME.hour
        if cls.CREATION_TIME.minute < 30:
            hr_split -= 1

        arr = [0] * 24
        for data_idx, hr_offset in enumerate(range(len(data), 0, -1)):
            arr[(hr_split - hr_offset) % 24] = data[data_idx]

        return arr

    def test_get_channel_hourly_avg(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_hourly_avg(self.CHANNEL_OID_1)

        self.assertEqual(
            result.data,
            [
                (StatsResults.CATEGORY_TOTAL, self._hourly_avg_gen_arr([3, 1, 1]), "#323232", "false"),
                (BotFeature.TXT_AR_ADD, self._hourly_avg_gen_arr([2, 0, 1]), "#00A14B", "true"),
                (BotFeature.TXT_AR_INFO, self._hourly_avg_gen_arr([1, 0, 0]), "#00A14B", "true"),
                (BotFeature.TXT_PING, self._hourly_avg_gen_arr([0, 1, 0]), "#00A14B", "true")
            ]
        )

    def test_get_channel_hourly_avg_limit_range(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_hourly_avg(self.CHANNEL_OID_1, hours_within=3)

        self.assertEqual(
            result.data,
            [
                (StatsResults.CATEGORY_TOTAL, self._hourly_avg_gen_arr([1, 1]), "#323232", "false"),
                (BotFeature.TXT_AR_ADD, self._hourly_avg_gen_arr([0, 1]), "#00A14B", "true"),
                (BotFeature.TXT_PING, self._hourly_avg_gen_arr([1, 0]), "#00A14B", "true")
            ]
        )

    def test_get_channel_hourly_avg_incl_not_used(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_hourly_avg(self.CHANNEL_OID_1, incl_not_used=True)

        expected = [(StatsResults.CATEGORY_TOTAL, self._hourly_avg_gen_arr([3, 1, 1]), "#323232", "false")]
        expected.extend(list(sorted(
            [
                (BotFeature.TXT_AR_ADD, self._hourly_avg_gen_arr([2, 0, 1]), "#00A14B", "true"),
                (BotFeature.TXT_AR_INFO, self._hourly_avg_gen_arr([1, 0, 0]), "#00A14B", "true"),
                (BotFeature.TXT_PING, self._hourly_avg_gen_arr([0, 1, 0]), "#00A14B", "true")
            ]
            + [
                (feature, [0] * 24, "#9C0000", "true") for feature in BotFeature
                if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_AR_INFO,
                                   BotFeature.TXT_PING, BotFeature.UNDEFINED)
            ],
            key=lambda entry: entry[0].code
        )))

        self.assertEqual(result.data, expected)

    def test_get_channel_hourly_avg_with_tzinfo(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_hourly_avg(self.CHANNEL_OID_1, tzinfo_=TWN.to_tzinfo())

        offset = [0] * 16

        self.assertEqual(
            result.data,
            [
                (StatsResults.CATEGORY_TOTAL, self._hourly_avg_gen_arr([3, 1, 1] + offset), "#323232", "false"),
                (BotFeature.TXT_AR_ADD, self._hourly_avg_gen_arr([2, 0, 1] + offset), "#00A14B", "true"),
                (BotFeature.TXT_AR_INFO, self._hourly_avg_gen_arr([1, 0, 0] + offset), "#00A14B", "true"),
                (BotFeature.TXT_PING, self._hourly_avg_gen_arr([0, 1, 0] + offset), "#00A14B", "true")
            ]
        )

    def test_get_channel_hourly_avg_channel_miss(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_hourly_avg(ObjectId())

        self.assertEqual(
            result.data,
            [(StatsResults.CATEGORY_TOTAL, [0] * 24, "#323232", "false")]
        )

    def test_get_channel_hourly_avg_no_data(self):
        result = BotFeatureUsageDataManager.get_channel_hourly_avg(self.CHANNEL_OID_1)

        self.assertEqual(
            result.data,
            [(StatsResults.CATEGORY_TOTAL, [0] * 24, "#323232", "false")]
        )

    def test_get_channel_per_user_usage(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_per_user_usage(self.CHANNEL_OID_1)
        self.assertEqual(
            result.data,
            {
                self.ROOT_OID_1: {
                    **{
                        BotFeature.TXT_AR_ADD: 2,
                        BotFeature.TXT_PING: 1
                    },
                    **{
                        feature: 0 for feature in BotFeature
                        if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_PING)
                    }
                },
                self.ROOT_OID_2: {
                    **{
                        BotFeature.TXT_AR_ADD: 1,
                        BotFeature.TXT_AR_INFO: 1
                    },
                    **{
                        feature: 0 for feature in BotFeature
                        if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_AR_INFO)
                    }
                }
            }
        )

    def test_get_channel_per_user_usage_limit_user(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_per_user_usage(self.CHANNEL_OID_1,
                                                                       member_oid_list=[self.ROOT_OID_1])
        self.assertEqual(
            result.data,
            {
                self.ROOT_OID_1: {
                    **{
                        BotFeature.TXT_AR_ADD: 2,
                        BotFeature.TXT_PING: 1
                    },
                    **{
                        feature: 0 for feature in BotFeature
                        if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_PING)
                    }
                }
            }
        )

    def test_get_channel_per_user_usage_limit_range_no_usage(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_per_user_usage(self.CHANNEL_OID_1, hours_within=3)
        self.assertEqual(
            result.data,
            {
                self.ROOT_OID_1: {
                    **{
                        BotFeature.TXT_AR_ADD: 1,
                        BotFeature.TXT_PING: 1
                    },
                    **{
                        feature: 0 for feature in BotFeature
                        if feature not in (BotFeature.TXT_AR_ADD, BotFeature.TXT_PING)
                    }
                }
            }
        )

    def test_get_channel_per_user_usage_channel_miss(self):
        self._insert_usages()

        result = BotFeatureUsageDataManager.get_channel_per_user_usage(ObjectId())
        self.assertEqual(result.data, {})

    def test_get_channel_per_user_usage_no_data(self):
        result = BotFeatureUsageDataManager.get_channel_per_user_usage(ObjectId())
        self.assertEqual(result.data, {})
