# https://stackoverflow.com/a/25835403
# https://docs.djangoproject.com/en/2.2/topics/testing/tools/
import json

import django
from django.test import Client, TestCase

from JellyBotAPI.api.static import result as r, param as p
from mongodb.factory import MONGO_CLIENT, InsertOutcome

c = Client(enforce_csrf_checks=True)
django.setup()


class TestAddAutoReply(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        MONGO_CLIENT.get_database("user").get_collection("onplat").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("api").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("mix").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("dict").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("conn").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("ctnt").delete_many({})
        MONGO_CLIENT.get_database("stats").get_collection("api").delete_many({})

    def _add_(self, kw, rep, channel, creator, platform, additional_msg=None):
        data = {
            p.AutoReply.KEYWORD: kw,
            p.AutoReply.RESPONSE: rep,
            p.AutoReply.CHANNEL_TOKEN: channel,
            p.AutoReply.CREATOR_TOKEN: creator,
            p.AutoReply.PLATFORM: platform
        }

        response = c.post("/api/ar/add", data)

        print(f"K: {kw} / R: {rep} / CH: {channel} / CR: {creator} / PL: {platform} - {None or additional_msg}")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("Test - Add")
        print(result)
        print()
        self.assertTrue(result[r.SUCCESS])
        return result

    def test_add(self):
        result = self._add_("ABC", "mno", "channel1", "user1", 1, "All New")
        self.assertEquals(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.SUCCESS_INSERTED)
        self.assertEquals(result[r.RESULT][r.Results.INSERT_CONN_OUTCOME], InsertOutcome.SUCCESS_INSERTED)

        result = self._add_("ABC", "mno", "channel1", "user2", 1, "Diff CR")
        self.assertEquals(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.SUCCESS_DATA_EXISTS)
        self.assertEquals(result[r.RESULT][r.Results.INSERT_CONN_OUTCOME], InsertOutcome.SUCCESS_DATA_EXISTS)

        result = self._add_("ABC", "mno", "channel2", "user2", 1, "Duplicate Conn. New CH.")
        self.assertEquals(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.SUCCESS_INSERTED)
        self.assertEquals(result[r.RESULT][r.Results.INSERT_CONN_OUTCOME], InsertOutcome.SUCCESS_DATA_EXISTS)

        result = self._add_("abc2", "mno2", "channel2", "user1", 1, "New Conn. Same User.")
        self.assertEquals(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.SUCCESS_INSERTED)
        self.assertEquals(result[r.RESULT][r.Results.INSERT_CONN_OUTCOME], InsertOutcome.SUCCESS_INSERTED)

    def test_lack_of_parameter(self):
        response = c.post("/api/ar/add", {p.AutoReply.KEYWORD: "xx"})

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("Test - Lack of Parameter")
        print(result)
        print()
        self.assertTrue(r.REQUIRED in result)

    def test_add_token(self):
        data = {
            p.AutoReply.KEYWORD: "R",
            p.AutoReply.RESPONSE: "X",
            p.AutoReply.CHANNEL_TOKEN: "channel1",
            p.AutoReply.CREATOR_TOKEN: "user1",
            p.AutoReply.PLATFORM: 1
        }

        response = c.post("/api/ar/add/token", data)

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("Test - Add - Token")
        print(result)
        print()
        self.assertTrue(result[r.SUCCESS])
