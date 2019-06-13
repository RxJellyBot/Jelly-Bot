from models import ChannelPermissionProfileModel

from ._base import BaseCollection

DB_NAME = "channel"


class PermissionProfileManager(BaseCollection):
    def __init__(self):
        super().__init__(DB_NAME, "perm", ChannelPermissionProfileModel.UserID)
        self.create_index([(ChannelPermissionProfileModel.UserID, 1), (ChannelPermissionProfileModel.ChannelID, 1)],
                          name="Permission Profile Identity", unique=True)

    # INCOMPLETE: Create Mod/Admin Preset
    # INCOMPLETE: Check mod/admin promotable if the mod/admin to be demoted is the last
    # INCOMPLETE: Custom permission profile creation (name and color changable only)
    # DRAFT: Group control: watcher - handle member left if the member is mod/admin
    pass


class PermissionPromotionStatusHolder(BaseCollection):
    # INCOMPLETE: Keeps the promo record for a short period
    pass


_inst = PermissionProfileManager()
