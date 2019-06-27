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
from mongodb.factory.results import InsertOutcome, GetOutcome

c = Client(enforce_csrf_checks=True)
django.setup()


class TestAddAutoReply(TestCase):
    TOKEN = None

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

        result = self._add_("ABC", "mno", "channel1", "user2", 1, "Diff CR")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = self._add_("ABC", "mno", "channel2", "user2", 1, "Duplicate Conn. New CH.")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = self._add_("abc2", "mno2", "channel2", "user1", 1, "New Conn. Same User.")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)

    def test_lack_of_parameter(self):
        response = c.post(reverse("api.ar.add"), {p.AutoReply.KEYWORD: "xx"})

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Lack of Parameter ===")
        pprint.pprint(result)
        print()
        self.assertTrue(r.REQUIRED in result)

    def test_add_empty_content(self):
        response = c.post(reverse("api.ar.add"), data={
            p.AutoReply.KEYWORD: "",
            p.AutoReply.RESPONSE: "",
            p.AutoReply.CHANNEL_TOKEN: "channel1",
            p.AutoReply.CREATOR_TOKEN: "user1",
            p.AutoReply.PLATFORM: 1
        })

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Empty Content Module ===")
        pprint.pprint(result)
        print()
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.KEYWORD][r.Results.OUTCOME], GetOutcome.X_NO_CONTENT)
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.RESPONSES][0][r.Results.OUTCOME], GetOutcome.X_NO_CONTENT)
        self.assertFalse(result[r.SUCCESS])

    def test_add_empty_channel_token(self):
        response = c.post(reverse("api.ar.add"), data={
            p.AutoReply.KEYWORD: "A",
            p.AutoReply.RESPONSE: "B",
            p.AutoReply.CHANNEL_TOKEN: "",
            p.AutoReply.CREATOR_TOKEN: "user1",
            p.AutoReply.PLATFORM: 1
        })

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Add - Empty Channel Token ===")
        pprint.pprint(result)
        print()
        self.assertTrue(r.AutoReplyResponse.CHANNEL_OID in result[r.ERRORS])
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.CHANNEL_OID], "")
        self.assertFalse(result[r.SUCCESS])

    def test_add_empty_user_token(self):
        response = c.post(reverse("api.ar.add"), data={
            p.AutoReply.KEYWORD: "A",
            p.AutoReply.RESPONSE: "B",
            p.AutoReply.CHANNEL_TOKEN: "channel1",
            p.AutoReply.CREATOR_TOKEN: "",
            p.AutoReply.PLATFORM: 1
        })

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Add - Empty User Token ===")
        pprint.pprint(result)
        print()
        self.assertTrue(r.AutoReplyResponse.CREATOR_OID in result[r.ERRORS])
        # Creator OID is a Processed value (via `Middleware`)
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.CREATOR_OID], None)
        self.assertFalse(result[r.SUCCESS])

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
        self.assertTrue(r.TokenActionResponse.TOKEN in result[r.RESULT])
        self.__class__.TOKEN = result[r.RESULT][r.TokenActionResponse.TOKEN]

    def test_add_token_complete(self):
        token = self.__class__.TOKEN
        if token is None:
            raise ValueError("Token action not performed yet.")

        data = {
            p.TokenAction.TOKEN: token
        }

        response = c.post(reverse("api.token.complete"), data)

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        print("=== Test - Add - Token Complete ===")
        pprint.pprint(result)
        print()


if __name__ == '__main__':
    unittest.main()
