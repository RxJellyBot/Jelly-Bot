from bson import ObjectId
from django.test import TestCase

from datetime import datetime, timedelta, timezone
import time

from JellyBot.systemconfig import Bot
from mongodb.factory import RemoteControlManager

EXPIRY_SEC_ORG = Bot.RemoteControl.IdleDeactivateSeconds
EXPIRY_SEC = 0.01

_now_ = datetime.now()
UID = ObjectId.from_datetime(_now_ - timedelta(days=1))
CID_SRC = ObjectId.from_datetime(_now_)
CID_DEST = ObjectId.from_datetime(_now_ + timedelta(days=1))


class TestRemoteControlHolder(TestCase):
    _expiry_ = Bot.RemoteControl.IdleDeactivateSeconds

    def tearDown(self) -> None:
        self.restore_temp_expiry()

    @staticmethod
    def set_temp_expiry():
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC

    @staticmethod
    def restore_temp_expiry():
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC_ORG

    @staticmethod
    def wait_expiry_fast_lock():
        time.sleep(EXPIRY_SEC)

    def test_get_current_update_expiry(self):
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)
        self.wait_expiry_fast_lock()
        entry = RemoteControlManager.get_current(UID, CID_SRC)
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertAlmostEquals(expiry_expected.timestamp(), entry.expiry.timestamp(), 1, f"Expiry time not match.")
        self.assertNotAlmostEquals(expiry_unexpected.timestamp(), entry.expiry.timestamp(), 2, f"Unexpected expiry.")

    def test_get_current_not_update_expiry(self):
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)

        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)
        self.wait_expiry_fast_lock()
        entry = RemoteControlManager.get_current(UID, CID_SRC, update_expiry=False)
        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertAlmostEquals(expiry_expected.timestamp(), entry.expiry.timestamp(), 1, f"Expiry time not match.")
        self.assertNotAlmostEquals(expiry_unexpected.timestamp(), entry.expiry.timestamp(), 2, f"Unexpected expiry.")

    def test_auto_deactivate(self):
        self.set_temp_expiry()
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)
        self.wait_expiry_fast_lock()
        self.assertIsNone(RemoteControlManager.get_current(UID, CID_SRC), "Entry still inside the holder.")

    def test_manual_deactivate(self):
        RemoteControlManager.activate(UID, CID_SRC, CID_DEST)
        RemoteControlManager.deactivate(UID, CID_SRC)
        self.assertIsNone(RemoteControlManager.get_current(UID, CID_SRC), "Entry still inside the holder.")

    def test_activate(self):
        entry = RemoteControlManager.activate(UID, CID_SRC, CID_DEST)
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Activation returned `None`")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertAlmostEquals(expiry_expected.timestamp(), entry.expiry.timestamp(), 1, f"Expiry time not match.")
