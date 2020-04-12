from dataclasses import dataclass
from typing import List

from bson import ObjectId

from flags import ProfilePermission, ProfilePermissionDefault, PermissionLevel
from models import Model, ChannelModel, ModelDefaultValueExt
from models.field import (
    ObjectIDField, TextField, ColorField, DictionaryField, BooleanField, ArrayField, IntegerField, PermissionLevelField
)


class ChannelProfileModel(Model):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!! Check `ProfileManager.process_profile_kwargs` when changing the variable name of this class. !!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    Name = TextField("n", default="-", must_have_content=True)
    Color = ColorField("col")
    PromoVote = IntegerField("promo")
    Permission = DictionaryField("perm",
                                 default=ProfilePermissionDefault.get_default_code_str_dict(), allow_none=False)
    PermissionLevel = PermissionLevelField("plv")

    EmailKeyword = ArrayField("e-kw", str)

    @property
    def is_mod(self):
        return self.permission_level >= PermissionLevel.MOD

    @property
    def is_admin(self):
        return self.permission_level >= PermissionLevel.ADMIN

    @property
    def permission_list(self) -> List[ProfilePermission]:
        ret = set()

        for cat, permitted in self.permission.items():
            if permitted:
                perm = ProfilePermission.cast(cat, silent_fail=True)
                if perm:
                    ret.add(perm)

        ret = ret.union(ProfilePermissionDefault.get_overridden_permissions(self.permission_level))

        return sorted(ret, key=lambda x: x.code)

    def pre_iter(self):
        # Will be used when the data will be passed to MongoDB
        d = [p.code_str for p in ProfilePermissionDefault.get_overridden_permissions(self.permission_level)]

        for perm_cat in ProfilePermission:
            k = perm_cat.code_str
            if k not in self.permission:
                self.permission[k] = k in d


@dataclass
class ChannelProfileListEntry:
    channel_data: ChannelModel
    channel_name: str
    profiles: List[ChannelProfileModel]
    starred: bool
    can_ced_profile: bool
    default_profile_oid: ObjectId


class ChannelProfileConnectionModel(Model):
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    Starred = BooleanField("s", default=False)
    UserOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)
    # ProfileOids will be empty list if the user is not in the channel
    ProfileOids = ArrayField("p", ObjectId, default=ModelDefaultValueExt.Required, allow_none=False, allow_empty=True)

    @property
    def available(self):
        return len(self.profile_oids) > 0


class PermissionPromotionRecordModel(Model):
    SupporterOid = ObjectIDField("s", stores_uid=True)
    TargetOid = ObjectIDField("t", stores_uid=True)
    ProfileOid = ObjectIDField("p")
