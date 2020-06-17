from bson import ObjectId

from strres.mongodb import Profile
from tests.base import TestCase

__all__ = ["TestProfile"]


class TestProfile(TestCase):
    def test_dangling_content_empty(self):
        self.assertEqual(Profile.dangling_content({}), "")

    def test_dangling_content_profile(self):
        prof_conn_oid = ObjectId()
        prof_oid = ObjectId()
        prof_oid_2 = ObjectId()

        self.assertEqual(
            Profile.dangling_content({prof_conn_oid: [prof_oid, prof_oid_2]}),
            f"Prof Conn OID <code>{prof_conn_oid}</code><br>"
            f"Profile OID not found: <code>{prof_oid} & {prof_oid_2}</code><br>"
            "<hr>"
        )

    def test_dangling_content_channel(self):
        prof_conn_oid = ObjectId()
        channel_oid = ObjectId()

        self.assertEqual(
            Profile.dangling_content({prof_conn_oid: channel_oid}),
            f"Prof Conn OID <code>{prof_conn_oid}</code><br>"
            f"Channel OID not found: <code>{channel_oid}</code><br>"
            "<hr>"
        )

    def test_dangling_content_multi(self):
        prof_conn_oid = ObjectId()
        prof_conn_oid_2 = ObjectId()
        prof_oid = ObjectId()
        prof_oid_2 = ObjectId()
        channel_oid = ObjectId()

        self.assertEqual(
            Profile.dangling_content({prof_conn_oid: channel_oid, prof_conn_oid_2: [prof_oid, prof_oid_2]}),
            f"Prof Conn OID <code>{prof_conn_oid}</code><br>"
            f"Channel OID not found: <code>{channel_oid}</code><br>"
            "<hr><br>"
            f"Prof Conn OID <code>{prof_conn_oid_2}</code><br>"
            f"Profile OID not found: <code>{prof_oid} & {prof_oid_2}</code><br>"
            "<hr>"
        )
