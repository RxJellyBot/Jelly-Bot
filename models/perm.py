from flags import PermissionCategory
from models import Model
from models.field import ObjectIDField, BooleanField, TextField, ColorIntField


class ChannelPermissionProfileModel(Model):
    UserID = "u"
    ChannelID = "c"
    Name = "n"
    Color = "col"

    def _init_fields_(self, **kwargs):
        self.user_oid = ObjectIDField(ChannelPermissionProfileModel.UserID, readonly=False)
        self.channel_oid = ObjectIDField(ChannelPermissionProfileModel.ChannelID, readonly=False)
        self.name = TextField(ChannelPermissionProfileModel.Name)
        self.color = ColorIntField(ChannelPermissionProfileModel.Color)
        for perm_cat in PermissionCategory:
            setattr(self, perm_cat.name, BooleanField(str(perm_cat.code)))
