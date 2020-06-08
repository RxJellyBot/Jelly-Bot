from bson import ObjectId

from datetime import datetime, timedelta, timezone
import time

from extutils import exec_timing_result
from JellyBot.systemconfig import Bot
from mongodb.factory.rmc import RemoteControlManager
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
_now_ = datetime.now()
UID = ObjectId.from_datetime(_now_ - timedelta(days=1))
CID_SRC = ObjectId.from_datetime(_now_)
CID_DEST = ObjectId.from_datetime(_now_ + timedelta(days=1))
# endregion


class TestRemoteControlHolder(TestTimeComparisonMixin, TestDatabaseMixin):
    inst = None

    @classmethod
    def setUpTestClass(cls):
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC
        cls.inst = RemoteControlManager()

    # TEST: Check enforcer unique

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
        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        self.inst.activate(UID, CID_SRC, CID_DEST)

        self.sleep_lock()

        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        get_current = exec_timing_result(self.inst.get_current, UID, CID_SRC)
        entry = get_current.return_

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(expiry_expected, entry.expiry, get_current.execution_ms / 1000)
        self.assertTimeDifferenceGreaterEqual(expiry_unexpected, entry.expiry, SLEEP_SEC)

    def test_get_current_not_update_expiry(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused by db-app comm lag
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        activate_sec = exec_timing_result(self.inst.activate, UID, CID_SRC, CID_DEST).execution_ms / 1000

        self.sleep_lock()

        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        entry = self.inst.get_current(UID, CID_SRC, update_expiry=False)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(expiry_expected, entry.expiry, activate_sec)
        self.assertTimeDifferenceGreaterEqual(expiry_unexpected, entry.expiry, SLEEP_SEC)

    def test_auto_deactivate(self):
        self.inst.activate(UID, CID_SRC, CID_DEST)
        self.wait_expiry_lock()
        self.assertIsNone(self.inst.get_current(UID, CID_SRC, update_expiry=False),
                          "Entry still inside the holder.")

    def test_manual_deactivate(self):
        self.inst.activate(UID, CID_SRC, CID_DEST)
        self.inst.deactivate(UID, CID_SRC)
        self.assertIsNone(self.inst.get_current(UID, CID_SRC, update_expiry=False),
                          "Entry still inside the holder.")

    def test_activate(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused ny db-app comm lag
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        entry = self.inst.activate(UID, CID_SRC, CID_DEST)

        self.assertIsNotNone(entry, "Activation returned `None`")
        self.assertEqual(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(entry.expiry, expiry_expected, 0.05)
