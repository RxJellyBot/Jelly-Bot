from bson import ObjectId

from datetime import timedelta
import time

from extutils import exec_timing_result
from extutils.dt import now_utc_aware
from JellyBot.systemconfig import Bot
from models import RemoteControlEntryModel
from mongodb.factory import RemoteControlManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestTimeComparisonMixin, TestDatabaseMixin

__all__ = ["TestRemoteControlHolder"]

EXPIRY_SEC_ORG = Bot.RemoteControl.IdleDeactivateSeconds

EXPIRY_SEC = max(0.3, TestDatabaseMixin.db_ping_ms() / 1000 * 1.5)
"""
Get the database ping to count in the database communication lag while reducing the test speed
Cannot be too short because the actual code execution may not be completed before the expiry
"""

SLEEP_SEC = EXPIRY_SEC * 0.03
"""
Must be shorter than `EXPIRY_SEC` or the entry will disappear before testing it
"""

# region Test identifiers
_now_ = now_utc_aware()
UID = ObjectId.from_datetime(_now_ - timedelta(days=1))
CID_SRC = ObjectId.from_datetime(_now_)
CID_DEST = ObjectId.from_datetime(_now_ + timedelta(days=1))


# endregion


class TestRemoteControlHolder(TestTimeComparisonMixin, TestDatabaseMixin):
    @staticmethod
    def collections_to_reset():
        return [RemoteControlManager]

    @classmethod
    def setUpTestClass(cls):
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC

    def test_add_duplicate(self):
        uid = ObjectId()
        src = ObjectId()

        expiry = now_utc_aware() + timedelta(minutes=999)

        self.assertEqual(
            RemoteControlManager.insert_one_model(
                RemoteControlEntryModel(
                    UserOid=uid, SourceChannelOid=src, TargetChannelOid=ObjectId(), ExpiryUtc=expiry))[0],
            WriteOutcome.O_INSERTED
        )
        self.assertEqual(RemoteControlManager.count_documents({}), 1)
        self.assertEqual(
            RemoteControlManager.insert_one_model(
                RemoteControlEntryModel(
                    UserOid=uid, SourceChannelOid=src, TargetChannelOid=ObjectId(), ExpiryUtc=expiry))[0],
            WriteOutcome.O_DATA_EXISTS
        )
        self.assertEqual(RemoteControlManager.count_documents({}), 1)

    @classmethod
    def tearDownTestClass(cls):
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC_ORG

    @staticmethod
    def wait_expiry_lock():
        time.sleep(EXPIRY_SEC)

    @staticmethod
    def sleep_lock():
        time.sleep(SLEEP_SEC)

    def test_get_current_update_expiry(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused ny db-app comm lag
        expiry_unexpected = now_utc_aware() + timedelta(seconds=EXPIRY_SEC)
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        self.sleep_lock()

        expiry_expected = now_utc_aware() + timedelta(seconds=EXPIRY_SEC)
        get_current = exec_timing_result(RemoteControlManager.get_current, UID, CID_SRC)
        entry = get_current.return_

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(expiry_expected, entry.expiry, get_current.execution_ms / 1000)
        self.assertTimeDifferenceGreaterEqual(expiry_unexpected, entry.expiry, SLEEP_SEC)

    def test_get_current_not_update_expiry(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused by db-app comm lag
        expiry_expected = now_utc_aware() + timedelta(seconds=EXPIRY_SEC)
        activate_sec = exec_timing_result(RemoteControlManager.activate, UID, CID_SRC, CID_DEST).execution_ms / 1000

        self.sleep_lock()

        expiry_unexpected = now_utc_aware() + timedelta(seconds=EXPIRY_SEC)
        entry = RemoteControlManager.get_current(UID, CID_SRC, update_expiry=False)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(expiry_expected, entry.expiry, activate_sec)
        self.assertTimeDifferenceGreaterEqual(expiry_unexpected, entry.expiry, SLEEP_SEC)

    def test_auto_deactivate(self):
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)
        self.wait_expiry_lock()
        self.assertIsNone(RemoteControlManager.get_current(UID, CID_SRC, update_expiry=False),
                          "Entry still inside the holder.")

    def test_manual_deactivate(self):
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)
        RemoteControlManager.deactivate(UID, CID_SRC)
        self.assertIsNone(RemoteControlManager.get_current(UID, CID_SRC, update_expiry=False),
                          "Entry still inside the holder.")

    def test_activate(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused ny db-app comm lag
        expiry_expected = now_utc_aware() + timedelta(seconds=EXPIRY_SEC)
        entry = RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        self.assertIsNotNone(entry, "Activation returned `None`")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(entry.expiry, expiry_expected, 0.05)
