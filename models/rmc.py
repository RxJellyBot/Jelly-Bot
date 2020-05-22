from extutils.locales import LocaleInfo
from extutils.dt import localtime
from models import Model, ModelDefaultValueExt
from models.field import DateTimeField, ObjectIDField, TextField


class RemoteControlEntryModel(Model):
    UserOid = ObjectIDField("uid", default=ModelDefaultValueExt.Required, stores_uid=True)
    LocaleCode = TextField("loc", default="Asia/Taipei")
    SourceChannelOid = ObjectIDField("src", default=ModelDefaultValueExt.Required)
    TargetChannelOid = ObjectIDField("dst", default=ModelDefaultValueExt.Required)
    ExpiryUtc = DateTimeField("exp", default=ModelDefaultValueExt.Required)

    @property
    def expiry(self):
        tzinfo = LocaleInfo.get_tzinfo(self.locale_code)

        return localtime(self.expiry_utc, tzinfo)

    @property
    def target_channel(self):
        from mongodb.factory import ChannelManager

        return ChannelManager.get_channel_oid(self.target_channel_oid)

    @property
    def expiry_str(self) -> str:
        return self.expiry.strftime("%Y-%m-%d %H:%M:%S (UTC%Z)")
