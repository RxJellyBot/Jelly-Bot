from dataclasses import dataclass
from typing import List

from bson import ObjectId

from flags import PermissionCategory, PermissionCategoryDefault
from models import Model, ChannelModel, ModelDefaultValueExt
from models.field import ObjectIDField, TextField, ColorField, DictionaryField, BooleanField, ArrayField, IntegerField


class ChannelProfileModel(Model):
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    Name = TextField("n", default="-", must_have_content=True)
    Color = ColorField("col")
    IsMod = BooleanField("m")
    IsAdmin = BooleanField("a")
    PromoVote = IntegerField("promo")
    Permission = DictionaryField("perm", default=PermissionCategoryDefault.get_default_preset_dict(), allow_none=False)

    EmailKeyword = ArrayField("e-kw", str)

    def pre_iter(self):
        if self.is_admin:
            f = PermissionCategoryDefault.get_admin
        elif self.is_mod:
            f = PermissionCategoryDefault.get_mod
        else:
            f = PermissionCategoryDefault.get_default

        for perm_cat in PermissionCategory:
            k = perm_cat.code_str
            if k not in self.permission:
                self.permission[k] = f(perm_cat)


@dataclass
class ChannelProfileListEntry:
    channel_data: ChannelModel
    channel_name: str
    profiles: List[ChannelProfileModel]
    starred: bool


class ChannelProfileConnectionModel(Model):
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    Starred = BooleanField("s", default=False)
    UserOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)
    # ProfileOids will be empty list if the user is not in the channel
    ProfileOids = ArrayField("p", ObjectId, default=ModelDefaultValueExt.Required, allow_none=False, allow_empty=True)


class PermissionPromotionRecordModel(Model):
    SupporterOid = ObjectIDField("s", stores_uid=True)
    TargetOid = ObjectIDField("t", stores_uid=True)
    ProfileOid = ObjectIDField("p")
