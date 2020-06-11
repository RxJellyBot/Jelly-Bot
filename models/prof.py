from dataclasses import dataclass
from typing import List

from bson import ObjectId

from flags import ProfilePermission, ProfilePermissionDefault, PermissionLevel
from models import Model, ChannelModel, ModelDefaultValueExt
from models.field import (
    ObjectIDField, TextField, ColorField, DictionaryField, BooleanField, ArrayField, IntegerField, PermissionLevelField
)


class ChannelProfileModel(Model):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!! Check `ProfileManager.process_create_profile_kwargs` when changing the variable name of this class. !!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required, readonly=True)
    Name = TextField("n", default="-", must_have_content=True)
    Color = ColorField("col")
    # 0 means no need to vote, > 0 means # votes needed to get this profile
    PromoVote = IntegerField("promo", positive_only=True)
    # TODO: #307 change to set field
    Permission = DictionaryField("perm",
                                 default=ProfilePermissionDefault.get_default_code_str_dict(), allow_none=False)
    PermissionLevel = PermissionLevelField("plv")

    EmailKeyword = ArrayField("e-kw", str)

    def __init__(self, *, from_db=False, **kwargs):
        super().__init__(from_db=from_db, **kwargs)
        self._complete_permission()

    def _complete_permission(self):
        d = [p.code_str for p in ProfilePermissionDefault.get_overridden_permissions(self.permission_level)]

        # Deep copy the variable so the original dict used to construct the model will not be modified
        d_to_set = dict(self.permission)

        for perm_cat in ProfilePermission:
            k = perm_cat.code_str
            d_to_set[k] = k in d or self.permission.get(k, False)

        self.permission = d_to_set

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

        return list(sorted(ret, key=lambda x: x.code))


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
    ProfileOids = ArrayField("p", ObjectId, default=ModelDefaultValueExt.Required)

    @property
    def available(self):
        return len(self.profile_oids) > 0


class PermissionPromotionRecordModel(Model):
    SupporterOid = ObjectIDField("s", default=ModelDefaultValueExt.Required, stores_uid=True)
    TargetOid = ObjectIDField("t", default=ModelDefaultValueExt.Required, stores_uid=True)
    ProfileOid = ObjectIDField("p", default=ModelDefaultValueExt.Required)
