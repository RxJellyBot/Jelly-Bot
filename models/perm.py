from extutils.custobj import ColorFactory
from flags import PermissionCategory, PermissionCategoryDefault
from models import Model, ModelDefaultValueExtension
from models.field import ObjectIDField, TextField, ColorField, DictionaryField, BooleanField


class ChannelPermissionProfileModel(Model):
    UserID = "u"
    ChannelID = "c"
    Name = "n"
    Color = "col"
    IsMod = "m"
    IsAdmin = "a"
    Permissions = "p"

    default_vals = (
        (UserID, ModelDefaultValueExtension.Required),
        (ChannelID, ModelDefaultValueExtension.Required),
        (Name, ModelDefaultValueExtension.Required),
        (Color, ColorFactory.BLACK),
        (IsMod, False),
        (IsAdmin, False),
        (Permissions, PermissionCategoryDefault.get_default_preset())
    )

    def _init_fields_(self, **kwargs):
        self.user_oid = ObjectIDField(ChannelPermissionProfileModel.UserID, readonly=False)
        self.channel_oid = ObjectIDField(ChannelPermissionProfileModel.ChannelID, readonly=False)
        self.name = TextField(ChannelPermissionProfileModel.Name)
        self.color = ColorField(ChannelPermissionProfileModel.Color)
        self.is_mod = BooleanField(ChannelPermissionProfileModel.IsMod)
        self.is_admin = BooleanField(ChannelPermissionProfileModel.IsAdmin)
        self.permission = DictionaryField(ChannelPermissionProfileModel.Permissions, allow_none=False)

    def pre_serialize(self):
        if self.is_admin.value:
            f = PermissionCategoryDefault.get_admin
        elif self.is_mod.value:
            f = PermissionCategoryDefault.get_mod
        else:
            f = PermissionCategoryDefault.get_default

        for perm_cat in PermissionCategory:
            k = f"_{perm_cat.code}"
            if k not in self.permission.value:
                self.permission.value[k] = f(perm_cat)
