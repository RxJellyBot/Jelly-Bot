import pymongo

from django.test import TestCase

from models import ChannelConfigModel, AutoReplyModuleTagModel
from models.exceptions import IdUnsupportedError
from extutils.mongo import get_codec_options

MONGO = pymongo.MongoClient("localhost", 27017)


class TestModel(TestCase):
    def test_insert(self):
        col = MONGO.get_database("test").get_collection("test", codec_options=get_codec_options())
        with self.assertRaises(IdUnsupportedError):
            col.insert_one(ChannelConfigModel(
                vote_promo_mod=5, vote_promo_admin=5, enable_auto_reply=False))

        m1 = AutoReplyModuleTagModel(name="Test")

        inserted = col.find_one({"_id": col.insert_one(m1).inserted_id})

        self.assertTrue(AutoReplyModuleTagModel.Name.key in inserted)
        self.assertTrue(AutoReplyModuleTagModel.Color.key in inserted)
        self.assertEqual(inserted[AutoReplyModuleTagModel.Name.key], "Test")
        self.assertEqual(
            inserted[AutoReplyModuleTagModel.Color.key], AutoReplyModuleTagModel.Color.default_value)
