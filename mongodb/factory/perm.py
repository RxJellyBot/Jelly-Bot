from bson import ObjectId

from extutils.custobj import Color
from models import ChannelPermissionProfileModel

from ._base import BaseCollection

DB_NAME = "channel"


class PermissionProfileManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "perm"
    model_class = ChannelPermissionProfileModel

    def __init__(self):
        super().__init__(ChannelPermissionProfileModel.UserID)
        self.create_index([(ChannelPermissionProfileModel.UserID, 1), (ChannelPermissionProfileModel.ChannelID, 1)],
                          name="Permission Profile Identity", unique=True)

    def register_new(self, channel_id: ObjectId, user_id: ObjectId, name: str, color: Color,
                     is_mod=False, is_admin=False):
        model, outcome, ex, insert_result = self.insert_one_data(
            ChannelPermissionProfileModel, user_oid=user_id, channel_oid=channel_id, name=name, color=color,
            is_mod=is_mod, is_admin=is_admin)

        # If duplicated, check and fill if not set

    # FIXME: Starts HERE - PermissionProfileManager

    # INCOMPLETE: Check mod/admin promotable if the mod/admin to be demoted is the last
    # INCOMPLETE: Custom permission profile creation (name and color changable only) - create then change
    # DRAFT: Group control: watcher - handle member left if the member is mod/admin
    pass


class PermissionPromotionStatusHolder(BaseCollection):
    # INCOMPLETE: Keeps the promo record for a short period
    pass


_inst = PermissionProfileManager()
