from bson import ObjectId

from extutils.color import Color
from models import ChannelPermissionProfileModel

from ._base import BaseCollection

DB_NAME = "channel"


class PermissionProfileManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "perm"
    model_class = ChannelPermissionProfileModel

    def __init__(self):
        super().__init__(ChannelPermissionProfileModel.UserOid.key)
        self.create_index(
            [(ChannelPermissionProfileModel.UserOid.key, 1), (ChannelPermissionProfileModel.ChannelOid.key, 1)],
            name="Permission Profile Identity", unique=True)

    # INCOMPLETE: Permission - [NOT COMPLETED] Register new permission profile
    def register_new(self, channel_id: ObjectId, user_id: ObjectId, name: str, color: Color,
                     is_mod=False, is_admin=False):
        model, outcome, ex, insert_result = self.insert_one_data(
            ChannelPermissionProfileModel, UserOid=user_id, ChannelOid=channel_id, Name=name, Color=color,
            IsMod=is_mod, IsAdmin=is_admin)

        # If duplicated, check and fill if not set

    # INCOMPLETE: Permission - Ensure mod/admin promotable if the mod/admin to be demoted is the last
    # INCOMPLETE: Permission - Custom permission profile creation (name and color changable only) - create then change
    pass


class PermissionPromotionStatusHolder(BaseCollection):
    # INCOMPLETE: Permission/Promotion - Keeps the promo record for a short period
    # INCOMPLETE: Promote for any role who needs promotion or direct assignment
    pass


_inst = PermissionProfileManager()
