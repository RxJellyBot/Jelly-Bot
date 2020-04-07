from bson import ObjectId
from django.test import TestCase

from datetime import datetime, timedelta, timezone
import time

from JellyBot.systemconfig import Bot
from bot.rmc import RemoteControl


EXPIRY_SEC_ORG = Bot.RemoteControl.IdleDeactivateSeconds
EXPIRY_SEC_FAST = 0.01


_now_ = datetime.now()
UID = ObjectId.from_datetime(_now_ - timedelta(days=1))
CID_SRC = ObjectId.from_datetime(_now_)
CID_DEST = ObjectId.from_datetime(_now_ + timedelta(days=1))


class TestRemoteControlHolder(TestCase):
    _expiry_ = Bot.RemoteControl.IdleDeactivateSeconds

    @classmethod
    def setUpClass(cls):
        cls.rmc = RemoteControl()

    @classmethod
    def tearDown(cls):
        cls.restore_temp_expiry()

    @classmethod
    def tearDownClass(cls):
        cls.restore_temp_expiry()

    @staticmethod
    def set_temp_expiry():
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC_FAST

    @staticmethod
    def restore_temp_expiry():
        Bot.RemoteControl.IdleDeactivateSeconds = EXPIRY_SEC_ORG

    @staticmethod
    def wait_expiry_fast_lock():
        time.sleep(EXPIRY_SEC_FAST)

    def test_get_current_update_expiry(self):
        self.rmc.activate(UID, CID_SRC, CID_DEST)

        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)
        time.sleep(EXPIRY_SEC_FAST)
        entry = self.rmc.get_current(UID, CID_SRC)
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertEquals(expiry_expected, entry.expiry, f"Expiry time not match.")
        self.assertNotEquals(expiry_unexpected, entry.expiry, f"Unexpected expiry.")

    def test_get_current_not_update_expiry(self):
        self.rmc.activate(UID, CID_SRC, CID_DEST)

        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)
        time.sleep(EXPIRY_SEC_FAST)
        entry = self.rmc.get_current(UID, CID_SRC, update_expiry=False)
        expiry_unexpected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Entry not found in the holder.")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertEquals(expiry_expected, entry.expiry, f"Expiry time not match.")
        self.assertNotEquals(expiry_unexpected, entry.expiry, f"Unexpected expiry.")

    def test_auto_deactivate(self):
        self.set_temp_expiry()
        self.rmc.activate(UID, CID_SRC, CID_DEST)
        self.wait_expiry_fast_lock()
        self.assertIsNone(self.rmc.get_current(UID, CID_SRC), "Entry still inside the holder.")

    def test_manual_deactivate(self):
        self.rmc.activate(UID, CID_SRC, CID_DEST)
        self.rmc.deactivate(UID, CID_SRC)
        self.assertIsNone(self.rmc.get_current(UID, CID_SRC), "Entry still inside the holder.")

    def test_activate(self):
        entry = self.rmc.activate(UID, CID_SRC, CID_DEST)
        expiry_expected = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=EXPIRY_SEC_ORG)

        self.assertIsNotNone(entry, "Activation returned `None`")
        self.assertEquals(CID_DEST, entry.target_channel_oid, "Target channel not match.")
        self.assertEquals(expiry_expected, entry.expiry, f"Expiry time not match.")
