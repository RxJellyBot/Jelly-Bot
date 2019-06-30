from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from flags import PermissionCategory, PermissionCategoryDefault
from models import Model, ModelDefaultValueExt
from models.field import ObjectIDField, TextField, ColorField, DictionaryField, BooleanField, ArrayField


class ChannelPermissionProfileModel(Model):
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    Name = TextField("n", default=_("(Unknown)"), must_have_content=True)
    Color = ColorField("col")
    IsMod = BooleanField("m")
    IsAdmin = BooleanField("a")
    NeedsPromo = BooleanField("promo")
    Permission = DictionaryField("perm", default=PermissionCategoryDefault.get_default_preset(), allow_none=False)

    def pre_iter(self):
        if self.is_admin:
            f = PermissionCategoryDefault.get_admin
        elif self.is_mod:
            f = PermissionCategoryDefault.get_mod
        else:
            f = PermissionCategoryDefault.get_default

        for perm_cat in PermissionCategory:
            k = f"_{perm_cat.code}"
            if k not in self.permission:
                self.permission[k] = f(perm_cat)


class ChannelPermissionConnectionModel(Model):
    ChannelOid = ObjectIDField("c", default=ModelDefaultValueExt.Required)
    UserOid = ObjectIDField("u", default=ModelDefaultValueExt.Required)
    ProfileOids = ArrayField("p", ObjectId, default=ModelDefaultValueExt.Required, allow_none=False, allow_empty=False)


class PermissionPromotionRecordModel(Model):
    SupporterOid = ObjectIDField("s")
    TargetOid = ObjectIDField("t")
    ProfileOid = ObjectIDField("p")
