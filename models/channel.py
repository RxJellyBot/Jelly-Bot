from models import Model
from models.field import PlatformField, TextField, ArrayField, ObjectIDField, PermissionLevelField


class ChannelModel(Model):
    Platform = "p"
    Token = "t"
    ManagerRelationshipIDs = "mgr"

    def _init_fields_(self, **kwargs):
        self.platform = PlatformField(ChannelModel.Platform)
        self.token = TextField(ChannelModel.Token, must_have_content=True)
        self.manager_oids = ArrayField(ChannelModel.ManagerRelationshipIDs, int)


class ChannelManagerRelationshipModel(Model):
    # TODO: Permission - PermissionLevel -> Permission config data Model?

    ChannelID = "c"
    UserID = "u"
    PermissionLevel = "p"

    def _init_fields_(self, **kwargs):
        self.channel_oid = ObjectIDField(ChannelManagerRelationshipModel.ChannelID, readonly=False)
        self.user_oid = ObjectIDField(ChannelManagerRelationshipModel.UserID, readonly=False)
        self.permission = PermissionLevelField(ChannelManagerRelationshipModel.PermissionLevel)
