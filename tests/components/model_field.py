import unittest

import pymongo
from bson import ObjectId

from JellyBotAPI.sysconfig import ChannelConfig
from flags import Platform
from models import ChannelConfigModel, OnPlatformUserModel, AutoReplyModuleTagModel
from models.exceptions import IdUnsupportedError
from models.field import TextField, PlatformField, IntegerField
from models.field.exceptions import FieldTypeMismatch, FieldValueInvalid, FieldCastingFailed
from extutils.mongo import get_codec_options

MONGO = pymongo.MongoClient("localhost", 27017)


class TestModel(unittest.TestCase):
    def test_parse(self):
        json = {ChannelConfigModel.VotePromoMod.key: 5,
                ChannelConfigModel.VotePromoAdmin.key: 5,
                ChannelConfigModel.EnableAutoReply.key: False,
                ChannelConfigModel.EnableCreateProfile.key: False, "a": 0}
        inst = ChannelConfigModel(**json, from_db=True)
        self.assertEqual(inst[ChannelConfigModel.VotePromoMod.key], 5)
        self.assertEqual(inst.vote_promo_mod, 5)
        self.assertEqual(inst[ChannelConfigModel.VotePromoAdmin.key], 5)
        self.assertEqual(inst.vote_promo_admin, 5)
        self.assertFalse(inst[ChannelConfigModel.EnableAutoReply.key])
        self.assertFalse(inst.enable_auto_reply)
        self.assertFalse(inst[ChannelConfigModel.EnableCreateProfile.key])
        self.assertFalse(inst.enable_create_profile)

    def test_parse_include_oid(self):
        json = {"_id": ObjectId("5d0aeb64b7e5ba4e71c319eb"),
                OnPlatformUserModel.Token.key: "U1234",
                OnPlatformUserModel.Platform.key: 1}
        inst = OnPlatformUserModel(**json, from_db=True)
        self.assertEqual(inst[OnPlatformUserModel.Token.key], "U1234")
        self.assertEqual(inst.token, "U1234")
        self.assertEqual(inst[OnPlatformUserModel.Platform.key], 1)
        self.assertEqual(inst.platform, 1)
        self.assertEqual(inst["_id"], ObjectId("5d0aeb64b7e5ba4e71c319eb"))
        self.assertEqual(inst.id, ObjectId("5d0aeb64b7e5ba4e71c319eb"))

    def test_init_from_field(self):
        m1 = ChannelConfigModel(
            vote_promo_mod=5, vote_promo_admin=5, enable_auto_reply=False, enable_create_profile=False)

        self.assertEqual(m1.vote_promo_mod, 5)
        self.assertEqual(m1.vote_promo_admin, 5)
        self.assertFalse(m1.enable_auto_reply)
        self.assertFalse(m1.enable_create_profile)

        m2 = ChannelConfigModel(
            VotePromoMod=5, VotePromoAdmin=5, EnableAutoReply=False, EnableCreateProfile=False)

        self.assertEqual(m2.vote_promo_mod, 5)
        self.assertEqual(m2.vote_promo_admin, 5)
        self.assertFalse(m2.enable_auto_reply)
        self.assertFalse(m2.enable_create_profile)

        m3 = ChannelConfigModel()

        self.assertEqual(m3.vote_promo_mod, ChannelConfig.VotesToPromoteMod)
        self.assertEqual(m3.vote_promo_admin, ChannelConfig.VotesToPromoteAdmin)
        self.assertEqual(m3.enable_auto_reply, ChannelConfigModel.EnableAutoReply.default_value)
        self.assertEqual(m3.enable_create_profile, ChannelConfigModel.EnableAutoReply.default_value)

    def test_insert(self):
        col = MONGO.get_database("test").get_collection("test", codec_options=get_codec_options())
        with self.assertRaises(IdUnsupportedError):
            col.insert_one(ChannelConfigModel(
                vote_promo_mod=5, vote_promo_admin=5, enable_auto_reply=False, enable_create_profile=False))

        m1 = AutoReplyModuleTagModel(name="Test")

        inserted = col.find_one({"_id": col.insert_one(m1).inserted_id})

        self.assertTrue(AutoReplyModuleTagModel.Name.key in inserted)
        self.assertTrue(AutoReplyModuleTagModel.Color.key in inserted)
        self.assertEqual(inserted[AutoReplyModuleTagModel.Name.key], "Test")
        self.assertEqual(
            inserted[AutoReplyModuleTagModel.Color.key], AutoReplyModuleTagModel.Color.default_value)


class TestFieldFilter(unittest.TestCase):
    def test_intfield_autocast(self):
        field = IntegerField("n").new()

        field.value = 5
        self.assertEqual(5, field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = None
        field.value = "5"
        self.assertEqual(5, field.value)

    def test_textfield(self):
        field = TextField("n").new()

        field.value = "S"
        self.assertEqual("S", field.value)

        field.value = 5
        self.assertEqual("5", field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = None

        field2 = TextField("email", regex=r"^\w+@\w+").new()
        field2.value = "s@gmail.com"
        self.assertEqual("s@gmail.com", field2.value)
        with self.assertRaises(FieldValueInvalid):
            field2.value = "Lorem"

    def test_platformfield_auto_cast(self):
        field = PlatformField("n").new()

        field.value = Platform.LINE
        self.assertEqual(Platform.LINE, field.value)
        with self.assertRaises(FieldCastingFailed):
            field.value = "LINE"
        with self.assertRaises(FieldTypeMismatch):
            field.value = None
        with self.assertRaises(FieldCastingFailed):
            field.value = 99999

    def test_platformfield_no_cast(self):
        field = PlatformField("n", auto_cast=False).new()

        field.value = Platform.LINE
        self.assertEqual(Platform.LINE, field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = "LINE"
        with self.assertRaises(FieldTypeMismatch):
            field.value = None
        with self.assertRaises(FieldValueInvalid):
            field.value = 99999

    def test_field_allow_none(self):
        with self.assertRaises(FieldValueInvalid):
            _ = TextField("t", allow_none=False, must_have_content=True).new()

        field = TextField("t", allow_none=True).new()
        self.assertEqual(field.value, None)
        field.value = None
        self.assertEqual(field.value, None)


if __name__ == '__main__':
    unittest.main()
