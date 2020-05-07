from bson import ObjectId
from django.test import TestCase

from datetime import datetime, timedelta, timezone
import time

from extutils import exec_timing_result
from JellyBot.systemconfig import Bot
from mongodb.factory import RemoteControlManager

from tests.base import TestTimeComparisonMixin

EXPIRY_SEC_ORG = Bot.RemoteControl.IdleDeactivateSeconds
EXPIRY_SEC = 1  # Recommended not to be < 1 because of the communication lag between the app and the database
SLEEP_SEC = 0.01  # Must be shorter than `EXPIRY_SEC` or the entry will disappear before testing it

# region Test identifiers
_now_ = datetime.now()
UID = ObjectId.from_datetime(_now_ - timedelta(days=1))
CID_SRC = ObjectId.from_datetime(_now_)
CID_DEST = ObjectId.from_datetime(_now_ + timedelta(days=1))


# endregion


class TestRemoteControlHolder(TestTimeComparisonMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC

    @classmethod
    def tearDownClass(cls):
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC_ORG

    def setUp(self) -> None:
        RemoteControlManager.drop()

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
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        self.sleep_lock()

        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        get_current = exec_timing_result(RemoteControlManager.get_current, UID, CID_SRC)
        entry = get_current.return_

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(expiry_expected, entry.expiry, get_current.execution_ms / 1000)
        self.assertTimeDifferenceGreaterEqual(expiry_unexpected, entry.expiry, SLEEP_SEC)

    def test_get_current_not_update_expiry(self):
        # Storing the expiry timestamp before the actual one is created
        # to reduce the time offset caused ny db-app comm lag
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        activate_sec = exec_timing_result(RemoteControlManager.activate, UID, CID_SRC, CID_DEST).execution_ms / 1000

        self.sleep_lock()

        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        entry = RemoteControlManager.get_current(UID, CID_SRC, update_expiry=False)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
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
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC)
        entry = RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        self.assertIsNotNone(entry, "Activation returned `None`")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertTimeDifferenceLessEqual(entry.expiry, expiry_expected, 0.05)
