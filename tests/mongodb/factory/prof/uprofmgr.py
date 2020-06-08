from bson import ObjectId

from models import ChannelProfileConnectionModel
from mongodb.factory.prof import UserProfileManager
from mongodb.factory.results import OperationOutcome, WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin

__all__ = ["TestUserProfileManager"]


class TestUserProfileManager(TestModelMixin, TestTimeComparisonMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()
    PROF_OID_1 = ObjectId()
    PROF_OID_2 = ObjectId()

    inst = None

    @classmethod
    def setUpTestClass(cls):
        cls.inst = UserProfileManager()

    def _sample_channels(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=ObjectId(), UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1])
        ]

        return mdls

    def _sample_channels_insert(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2, ProfileOids=[])
        ]
        self.inst.insert_many(mdls)

        return mdls

    def test_attach_new_one(self):
        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, self.PROF_OID_1)

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 1)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]))

    def test_attach_new_multi(self):
        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, [self.PROF_OID_1, self.PROF_OID_2])

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 1)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]))

    def test_attach_existed(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1])
        self.inst.insert_one_model(mdl)

        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, [self.PROF_OID_2])

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 1)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]))

    def test_attach_diff_user(self):
        self.inst.insert_one_model(ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]))
        self.inst.insert_one_model(ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]))

        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, [self.PROF_OID_2])

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 2)
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]))
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                ProfileOids=[self.PROF_OID_1]))

    def test_attach_diff_channel(self):
        self.inst.insert_one_model(ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]))
        self.inst.insert_one_model(ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]))

        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, [self.PROF_OID_2])

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 2)
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_OID},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]))
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_OID_2},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1]))

    def test_attach_duplicated(self):
        self.inst.insert_one_model(ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1]))

        result = self.inst.user_attach_profile(self.CHANNEL_OID, self.USER_OID, [self.PROF_OID_1])

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertEqual(self.inst.count_documents({}), 1)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                ProfileOids=[self.PROF_OID_1]))

    def test_get_user_conn(self):
        expected_mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1])
        self.inst.insert_one_model(expected_mdl)

        actual_mdl = self.inst.get_user_profile_conn(self.CHANNEL_OID, self.USER_OID)

        self.assertEqual(expected_mdl, actual_mdl)

    def test_get_user_not_exists(self):
        mdl = self.inst.get_user_profile_conn(self.CHANNEL_OID, self.USER_OID)

        self.assertIsNone(mdl)

    def test_get_user_channel_inside_only(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertModelSequenceEqual(self.inst.get_user_channel_profiles(self.USER_OID), [mdls[3], mdls[1]])

    def test_get_user_starred_on_top(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=ObjectId(), UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1], Starred=True),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1], Starred=True)
        ]
        self.inst.insert_many(mdls)

        self.assertModelSequenceEqual(self.inst.get_user_channel_profiles(self.USER_OID), [mdls[2], mdls[0], mdls[1]])

    def test_get_user_channel_all(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertModelSequenceEqual(
            self.inst.get_user_channel_profiles(self.USER_OID, inside_only=False),
            [mdls[3], mdls[1], mdls[0]])

    def test_get_user_channel_no_channel(self):
        self.assertModelSequenceEqual(self.inst.get_user_channel_profiles(self.USER_OID, inside_only=False), [])

    def test_get_user_channel_all_outside(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=ObjectId(), UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1])
        ]
        self.inst.insert_many(mdls)

        self.assertModelSequenceEqual(self.inst.get_user_channel_profiles(self.USER_OID), [])
        self.assertModelSequenceEqual(
            self.inst.get_user_channel_profiles(self.USER_OID, inside_only=False), [mdls[3], mdls[1], mdls[0]])

    def test_get_user_channel_user_not_exists(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertModelSequenceEqual(self.inst.get_user_channel_profiles(ObjectId()), [])

    def test_get_channel_member(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertModelSetEqual(
            set(self.inst.get_channel_members(self.CHANNEL_OID)),
            {mdls[1], mdls[2]})

    def test_get_channel_member_multi(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertModelSetEqual(
            set(self.inst.get_channel_members([self.CHANNEL_OID, self.CHANNEL_OID_2])),
            {mdls[1], mdls[2], mdls[3], mdls[4]})

    def test_get_channel_member_all(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        ]
        self.inst.insert_many(mdls)

        self.assertModelSetEqual(
            set(self.inst.get_channel_members(self.CHANNEL_OID, available_only=False)),
            {mdls[0], mdls[1]})

    def test_get_channel_member_all_out(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[])
        ]
        self.inst.insert_many(mdls)

        self.assertModelSetEqual(
            set(self.inst.get_channel_members(self.CHANNEL_OID)),
            set())
        self.assertModelSetEqual(
            set(self.inst.get_channel_members(self.CHANNEL_OID, available_only=False)),
            set(mdls))

    def test_get_channel_member_empty_param(self):
        mdls = self._sample_channels()
        self.inst.insert_many(mdls)

        self.assertEqual(self.inst.get_channel_members([]), [])

    def test_get_channel_member_not_exists(self):
        self.assertEqual(self.inst.get_channel_members(ObjectId()), [])
        self.assertEqual(self.inst.get_channel_members(ObjectId(), available_only=False), [])

    def test_user_channel_dict(self):
        self._sample_channels_insert()

        self.assertDictEqual(
            self.inst.get_users_exist_channel_dict([self.USER_OID, self.USER_OID_2]),
            {
                self.USER_OID: {self.CHANNEL_OID_2},
                self.USER_OID_2: {self.CHANNEL_OID}
            }
        )

    def test_user_channel_dict_partial(self):
        self._sample_channels_insert()

        self.assertDictEqual(
            self.inst.get_users_exist_channel_dict([self.USER_OID]),
            {self.USER_OID: {self.CHANNEL_OID_2}}
        )

    def test_user_channel_dict_user_not_exists(self):
        self._sample_channels_insert()

        self.assertDictEqual(self.inst.get_users_exist_channel_dict([ObjectId()]), {})

    def test_user_channel_dict_no_channel(self):
        self.assertDictEqual(self.inst.get_users_exist_channel_dict([self.USER_OID]), {})

    def test_user_channel_dict_empty_param(self):
        self._sample_channels_insert()

        self.assertEqual(self.inst.get_users_exist_channel_dict([]), {})

    def test_available_conns(self):
        mdls = self._sample_channels_insert()

        self.assertModelSetEqual(set(self.inst.get_available_connections()), {mdls[1], mdls[2]})

    def test_available_conns_empty(self):
        self.assertModelSequenceEqual(list(self.inst.get_available_connections()), [])

    def test_prof_oids(self):
        self._sample_channels_insert()

        self.assertEqual(set(self.inst.get_profile_user_oids(self.PROF_OID_1)), {self.USER_OID, self.USER_OID_2})

    def test_prof_oids_no_prof(self):
        self.assertEqual(set(self.inst.get_profile_user_oids(self.PROF_OID_1)), set())

    def test_profs_oids(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        self.assertDictEqual(
            self.inst.get_profiles_user_oids([self.PROF_OID_1, self.PROF_OID_2]),
            {
                self.PROF_OID_1: {self.USER_OID, self.USER_OID_2},
                self.PROF_OID_2: {self.USER_OID}
            }
        )

    def test_profs_oids_partial(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        self.assertDictEqual(
            self.inst.get_profiles_user_oids([self.PROF_OID_1]),
            {self.PROF_OID_1: {self.USER_OID, self.USER_OID_2}}
        )

    def test_profs_oids_partial_miss(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        self.assertDictEqual(
            self.inst.get_profiles_user_oids([self.PROF_OID_1, ObjectId()]),
            {self.PROF_OID_1: {self.USER_OID, self.USER_OID_2}}
        )

    def test_profs_oids_no_prof(self):
        self.assertDictEqual(self.inst.get_profiles_user_oids([self.PROF_OID_1]), {})

    def test_profs_oids_empty_param(self):
        self._sample_channels_insert()

        self.assertDictEqual(self.inst.get_profiles_user_oids([]), {})

    def test_user_in_channel(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        self.assertTrue(self.inst.is_user_in_channel(self.CHANNEL_OID, self.USER_OID))

    def test_user_in_channel_user_exists_not_in_channel(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[])
        self.inst.insert_one(mdl)

        self.assertFalse(self.inst.is_user_in_channel(self.CHANNEL_OID, self.USER_OID))

    def test_user_in_channel_no_channel(self):
        self.assertFalse(self.inst.is_user_in_channel(self.CHANNEL_OID, self.USER_OID))

    def test_user_in_channel_user_not_exists(self):
        self.assertFalse(self.inst.is_user_in_channel(self.CHANNEL_OID, ObjectId()))

    def test_user_in_channel_channel_not_exists(self):
        self.assertFalse(self.inst.is_user_in_channel(ObjectId(), self.USER_OID))

    def test_mark_unavailable(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1])
        self.inst.insert_one(mdl)

        self.inst.mark_unavailable(self.CHANNEL_OID, self.USER_OID)

        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[])
        )

    def test_mark_unavailable_has_multi(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        self.inst.mark_unavailable(self.CHANNEL_OID, self.USER_OID)

        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[])
        )

    def test_mark_unavailable_user_not_match(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        self.inst.mark_unavailable(self.CHANNEL_OID, self.USER_OID_2)

        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        )

    def test_mark_unavailable_channel_not_match(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        self.inst.mark_unavailable(self.CHANNEL_OID_2, self.USER_OID)

        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        )

    def test_mark_unavailable_no_channel(self):
        self.assertEqual(self.inst.count_documents({}), 0)
        self.inst.mark_unavailable(self.CHANNEL_OID, self.USER_OID)
        self.assertEqual(self.inst.count_documents({}), 0)

    def test_detach_from_user(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        result = self.inst.detach_profile(self.PROF_OID_2, self.USER_OID)

        self.assertEqual(result, WriteOutcome.O_DATA_UPDATED)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1])
        )

    def test_detach_from_all(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        result = self.inst.detach_profile(self.PROF_OID_1)

        self.assertEqual(result, WriteOutcome.O_DATA_UPDATED)
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_2])
        )
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[])
        )

    def test_detach_profile_not_exists(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        result = self.inst.detach_profile(ObjectId(), self.USER_OID)

        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        )
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1])
        )

    def test_detach_user_not_exists(self):
        mdls = [
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1]),
        ]
        self.inst.insert_many(mdls)

        result = self.inst.detach_profile(self.PROF_OID_1, ObjectId())

        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        )
        self.assertModelEqual(
            self.inst.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                      parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[self.PROF_OID_1])
        )

    def test_change_star(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        changed = self.inst.change_star(self.CHANNEL_OID, self.USER_OID, True)

        self.assertTrue(changed)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2],
                Starred=True
            )
        )

        changed = self.inst.change_star(self.CHANNEL_OID, self.USER_OID, True)

        self.assertFalse(changed)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2],
                Starred=True
            )
        )

        changed = self.inst.change_star(self.CHANNEL_OID, self.USER_OID, False)

        self.assertTrue(changed)
        self.assertModelEqual(
            self.inst.find_one_casted({}, parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(
                ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2]
            )
        )

    def test_change_star_no_channel(self):
        changed = self.inst.change_star(self.CHANNEL_OID, self.USER_OID, True)

        self.assertFalse(changed)

    def test_change_star_miss(self):
        mdl = ChannelProfileConnectionModel(
            ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[self.PROF_OID_1, self.PROF_OID_2])
        self.inst.insert_one(mdl)

        changed = self.inst.change_star(ObjectId(), self.USER_OID, True)
        self.assertFalse(changed)
        changed = self.inst.change_star(self.CHANNEL_OID, ObjectId(), True)
        self.assertFalse(changed)
