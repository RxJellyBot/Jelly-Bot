from typing import Dict

from bson import ObjectId

from flags import Platform
from models import ChannelConfigModel, ChannelModel
from mongodb.factory.channel import ChannelManager
from mongodb.factory.results import WriteOutcome, GetOutcome, UpdateOutcome
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestChannelManager"]


class TestChannelManager(TestModelMixin, TestDatabaseMixin):
    inst = None

    @classmethod
    def setUpTestClass(cls):
        cls.inst = ChannelManager()

    def _add_channels(self) -> Dict[ObjectId, ChannelModel]:
        oids = {}

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="ABCDE"))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234568", BotAccessible=False,
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="ABCDF"))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234569", BotAccessible=False,
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="ABCDG", InfoPrivate=True))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234560",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="BBCDA", InfoPrivate=True))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U123456A",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="AEAEE"))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U123456B",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)
        oids[mdl.id] = mdl

        return oids

    @staticmethod
    def _match_default_name_criteria(w: str, mdl: ChannelModel):
        return w in mdl.token or (mdl.config.default_name and w in mdl.config.default_name)

    def test_register_new(self):
        result = self.inst.ensure_register(Platform.LINE, "U1234567")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567",
                Config=ChannelConfigModel(DefaultProfileOid=result.model.config.default_profile_oid))
        )

    def test_register_exists(self):
        mdl = self.inst.ensure_register(Platform.LINE, "U1234567").model

        result = self.inst.ensure_register(Platform.LINE, "U1234567")

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl)

    def test_register_default_name(self):
        result = self.inst.ensure_register(Platform.LINE, "U1234567", default_name="N")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567",
                Config=ChannelConfigModel(DefaultProfileOid=result.model.config.default_profile_oid, DefaultName="N"))
        )

    def test_deregister_existed(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.deregister(Platform.LINE, "U1234567"), WriteOutcome.O_DATA_UPDATED)

    def test_deregister_not_existed(self):
        self.assertEqual(self.inst.deregister(Platform.LINE, "U1234567"), WriteOutcome.X_CHANNEL_NOT_FOUND)

    def test_mark_accessibility_existed(self):
        doid = ObjectId()

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=doid),
            BotAccessible=False,
        )
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.mark_accessibility(Platform.LINE, "U1234567", True), WriteOutcome.O_DATA_UPDATED)
        self.assertModelEqual(
            self.inst.find_one_casted(
                {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
                parse_cls=ChannelModel),
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567", BotAccessible=True,
                Config=ChannelConfigModel(DefaultProfileOid=doid))
        )

        self.assertEqual(self.inst.mark_accessibility(Platform.LINE, "U1234567", False), WriteOutcome.O_DATA_UPDATED)
        self.assertModelEqual(
            self.inst.find_one_casted(
                {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
                parse_cls=ChannelModel),
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567", BotAccessible=False,
                Config=ChannelConfigModel(DefaultProfileOid=doid))
        )

    def test_mark_accessibility_not_existed(self):
        self.assertEqual(
            self.inst.mark_accessibility(Platform.LINE, "U1234567", True), WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertEqual(
            self.inst.mark_accessibility(Platform.LINE, "U1234567", False), WriteOutcome.X_CHANNEL_NOT_FOUND)

    def test_update_default_name(self):
        doid = ObjectId()

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567",
            Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="N"))
        self.inst.insert_one_model(mdl)

        self.assertTrue(self.inst.update_channel_default_name(Platform.LINE, "U1234567", "O").is_success)

        self.assertModelEqual(
            self.inst.find_one_casted(
                {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
                parse_cls=ChannelModel),
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567",
                Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="O"))
        )

        self.assertTrue(self.inst.update_channel_default_name(Platform.LINE, "U1234567", "N").is_success)

        self.assertModelEqual(
            self.inst.find_one_casted(
                {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
                parse_cls=ChannelModel),
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567",
                Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="N"))
        )

    def test_update_nickname_add(self):
        doid = ObjectId()

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=doid))
        self.inst.insert_one_model(mdl)

        cid = mdl.id
        uid = ObjectId()

        result = self.inst.update_channel_nickname(cid, uid, "N1")
        self.assertTrue(result.outcome, WriteOutcome.O_DATA_UPDATED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567", Name={str(uid): "N1"},
                Config=ChannelConfigModel(DefaultProfileOid=doid))
        )

        cnl = self.inst.find_one_casted(
            {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
            parse_cls=ChannelModel)
        self.assertEqual(cnl.get_channel_name(uid), "N1")

    def test_update_nickname_delete(self):
        doid = ObjectId()

        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567",
            Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="O"))
        self.inst.insert_one_model(mdl)

        cid = mdl.id
        uid = ObjectId()

        # Add the name and ensure it first
        result = self.inst.update_channel_nickname(cid, uid, "N1")
        self.assertTrue(result.outcome, WriteOutcome.O_DATA_UPDATED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567", Name={str(uid): "N1"},
                Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="O"))
        )

        # Delete the name and check
        result = self.inst.update_channel_nickname(cid, uid, "")
        self.assertTrue(result.outcome, WriteOutcome.O_DATA_UPDATED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ChannelModel(
                Platform=Platform.LINE, Token="U1234567", Name={},
                Config=ChannelConfigModel(DefaultProfileOid=doid, DefaultName="O"))
        )

        cnl = self.inst.find_one_casted(
            {ChannelModel.Platform.key: Platform.LINE, ChannelModel.Token.key: "U1234567"},
            parse_cls=ChannelModel)
        self.assertEqual(cnl.get_channel_name(uid), "O")

    def test_update_nickname_not_exists(self):
        uid = ObjectId()

        result = self.inst.update_channel_nickname(ObjectId(), uid, "N1")
        self.assertTrue(result.outcome, WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

    def test_get_token_exists(self):
        mdl_expected = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl_expected)

        mdl_actual = self.inst.get_channel_token(Platform.LINE, "U1234567")

        self.assertModelEqual(mdl_expected, mdl_actual)

    def test_get_token_not_exists(self):
        mdl = self.inst.get_channel_token(Platform.LINE, "U1234567")

        self.assertIsNone(mdl)

    def test_get_token_auto_register(self):
        mdl_expected = ChannelModel(
            Platform=Platform.LINE, Token="U1234567",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), DefaultName="N"))
        mdl_actual = self.inst.get_channel_token(Platform.LINE, "U1234567", auto_register=True, default_name="N")

        # Sync default profile OID
        mdl_expected.config.default_profile_oid = mdl_actual.config.default_profile_oid

        self.assertModelEqual(mdl_expected, mdl_actual)

    def test_get_token_diff_platform_type(self):
        mdl_expected = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl_expected)

        mdl_actual = self.inst.get_channel_token(Platform.LINE, "U1234567")

        self.assertModelEqual(mdl_expected, mdl_actual)

    def test_get_oid_is_private(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567",
            Config=ChannelConfigModel(DefaultProfileOid=ObjectId(), InfoPrivate=True))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.get_channel_oid(mdl.id), mdl)
        self.assertIsNone(self.inst.get_channel_oid(mdl.id, hide_private=True))

    def test_get_oid_not_private(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.get_channel_oid(mdl.id), mdl)
        self.assertEqual(self.inst.get_channel_oid(mdl.id, hide_private=True), mdl)

    def test_get_dict_all(self):
        oids = self._add_channels()

        d = self.inst.get_channel_dict(list(oids))

        self.assertEqual(oids, d)

    def test_get_dict_accessible_only(self):
        expected_d = self._add_channels()

        actual_d = self.inst.get_channel_dict(list(expected_d), accessbible_only=True)

        expected_d = {cid: cmdl for cid, cmdl in expected_d.items() if cmdl.bot_accessible}

        self.assertModelDictEqual(expected_d, actual_d)

    def test_get_default_name_all(self):
        expected_s = set(self._add_channels().values())

        actual_s = set(self.inst.get_channel_default_name("ABCD", hide_private=False))

        expected_s = {cmdl for cmdl in expected_s if self._match_default_name_criteria("ABCD", cmdl)}

        self.assertModelSetEqual(expected_s, actual_s)

    def test_get_default_name_by_token(self):
        expected_s = set(self._add_channels().values())

        actual_s = set(self.inst.get_channel_default_name("U123456", hide_private=False))

        expected_s = {cmdl for cmdl in expected_s if self._match_default_name_criteria("U123456", cmdl)}

        self.assertModelSetEqual(expected_s, actual_s)

    def test_get_default_name_no_private(self):
        expected_s = set(self._add_channels().values())

        actual_s = set(self.inst.get_channel_default_name("U123456"))

        expected_s = {cmdl for cmdl in expected_s if not cmdl.config.info_private}

        self.assertModelSetEqual(expected_s, actual_s)

    def test_get_packed_exists(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        result = self.inst.get_channel_packed(Platform.LINE, "U1234567")

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertEqual(result.model, mdl)

    def test_get_packed_not_exists(self):
        result = self.inst.get_channel_packed(Platform.LINE, "U1234567")

        self.assertEqual(result.outcome, GetOutcome.X_CHANNEL_NOT_FOUND)
        self.assertIsNone(result.model)
        self.assertEqual(self.inst.count_documents({}), 0)

    def test_set_config_exists(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.set_config(mdl.id, ChannelConfigModel.InfoPrivate.key, True),
                         UpdateOutcome.O_UPDATED)

    def test_set_config_incorrect_type(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.set_config(mdl.id, ChannelConfigModel.InfoPrivate.key, object()),
                         UpdateOutcome.X_CONFIG_TYPE_MISMATCH)

    def test_set_config_invalid_value(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.set_config(mdl.id, ChannelConfigModel.VotePromoMod.key, -5),
                         UpdateOutcome.X_CONFIG_VALUE_INVALID)

    def test_set_config_not_exist_channel(self):
        self.assertEqual(self.inst.set_config(ObjectId(), ChannelConfigModel.InfoPrivate.key, True),
                         UpdateOutcome.X_CHANNEL_NOT_FOUND)

    def test_set_config_not_exist_config(self):
        mdl = ChannelModel(
            Platform=Platform.LINE, Token="U1234567", Config=ChannelConfigModel(DefaultProfileOid=ObjectId()))
        self.inst.insert_one_model(mdl)

        self.assertEqual(self.inst.set_config(mdl.id, "AABBCCDDD", 1),
                         UpdateOutcome.X_CONFIG_NOT_EXISTS)