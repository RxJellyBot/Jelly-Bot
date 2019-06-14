from flags import PermissionCategory
from models import Model
from models.field import ObjectIDField, BooleanField, TextField, ColorField


class ChannelPermissionProfileModel(Model):
    UserID = "u"
    ChannelID = "c"
    Name = "n"
    Color = "col"

    def _init_fields_(self, **kwargs):
        self.user_oid = ObjectIDField(ChannelPermissionProfileModel.UserID, readonly=False)
        self.channel_oid = ObjectIDField(ChannelPermissionProfileModel.ChannelID, readonly=False)
        self.name = TextField(ChannelPermissionProfileModel.Name)
        self.color = ColorField(ChannelPermissionProfileModel.Color)
        for perm_cat in PermissionCategory:
            setattr(self, f"perm_{perm_cat.name}", BooleanField(f"_{perm_cat.code}"))
