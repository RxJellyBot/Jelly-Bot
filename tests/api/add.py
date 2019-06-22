# Request Factory - https://stackoverflow.com/a/25835403
# Testing tools - https://docs.djangoproject.com/en/2.2/topics/testing/tools/
import json
import unittest
import pprint

import django
from django.test import Client, TestCase
from django.urls import reverse

from JellyBotAPI.api.static import result as r, param as p
from mongodb.factory import MONGO_CLIENT
from mongodb.factory.results import InsertOutcome

c = Client(enforce_csrf_checks=True)
django.setup()


class TestAddAutoReply(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        MONGO_CLIENT.get_database("stats").get_collection("api").delete_many({})
        MONGO_CLIENT.get_database("tk_act").get_collection("main").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("onplat").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("root").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("dict").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("conn").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("ctnt").delete_many({})

    def _add_(self, kw, rep, channel, creator, platform, additional_msg=None):
        data = {
            p.AutoReply.KEYWORD: kw,
            p.AutoReply.RESPONSE: rep,
            p.AutoReply.CHANNEL_TOKEN: channel,
            p.AutoReply.CREATOR_TOKEN: creator,
            p.AutoReply.PLATFORM: platform
        }

        response = c.post(reverse("api.ar.add"), data)

        print(f"K: {kw} / R: {rep} / CH: {channel} / CR: {creator} / PL: {platform} - {None or additional_msg}")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Add ===")
        pprint.pprint(result)
        print()
        self.assertTrue(result[r.SUCCESS])
        return result

    def test_add(self):
        # TODO: Test AR: Add test-cleaning work
        result = self._add_("ABC", "mno", "channel1", "user1", 1, "All New")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)
        self.assertEqual(result[r.RESULT][r.AutoReplyResponse.INSERT_CONN_OUTCOME], InsertOutcome.O_INSERTED)

        result = self._add_("ABC", "mno", "channel1", "user2", 1, "Diff CR")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_DATA_EXISTS)
        self.assertEqual(result[r.RESULT][r.AutoReplyResponse.INSERT_CONN_OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = self._add_("ABC", "mno", "channel2", "user2", 1, "Duplicate Conn. New CH.")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)
        self.assertEqual(result[r.RESULT][r.AutoReplyResponse.INSERT_CONN_OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = self._add_("abc2", "mno2", "channel2", "user1", 1, "New Conn. Same User.")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)
        self.assertEqual(result[r.RESULT][r.AutoReplyResponse.INSERT_CONN_OUTCOME], InsertOutcome.O_INSERTED)

    def test_lack_of_parameter(self):
        response = c.post(reverse("api.ar.add"), {p.AutoReply.KEYWORD: "xx"})

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Lack of Parameter ===")
        pprint.pprint(result)
        print()
        self.assertTrue(r.REQUIRED in result)

    def test_add_data_error(self):
        raise NotImplementedError()

    def test_add_token(self):
        data = {
            p.AutoReply.KEYWORD: "R",
            p.AutoReply.RESPONSE: "X",
            p.AutoReply.CHANNEL_TOKEN: "channel1",
            p.AutoReply.CREATOR_TOKEN: "user1",
            p.AutoReply.PLATFORM: 1
        }

        response = c.post(reverse("api.ar.add_token"), data)

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Add - Token ===")
        pprint.pprint(result)
        print()
        self.assertTrue(result[r.SUCCESS])

        raise NotImplementedError("Token completion test not implemented.")


if __name__ == '__main__':
    unittest.main()
