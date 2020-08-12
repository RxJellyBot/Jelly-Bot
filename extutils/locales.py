from datetime import tzinfo, timedelta
from typing import Optional

from django.utils.translation import gettext_lazy as _

from dataclasses import dataclass
from datetime import datetime

import pytz


def sec_diff_to_utc_offset(s_diff: float):
    """take ``s_diff`` and translate it into UTC offset string (example: +0500)."""
    is_pos = s_diff >= 0
    s_diff = int(abs(s_diff))
    h = s_diff // 3600
    m = (s_diff - h * 3600) // 60

    return f"{'+' if is_pos else '-'}{h:02}{m:02}"


@dataclass
class LocaleInfo:
    description: str
    pytz_code: str

    @property
    def current_utc_hr_offset(self) -> str:
        return f"UTC{self.to_tzinfo().tzname(datetime.utcnow())}"

    def to_tzinfo(self):
        return LocaleInfo.get_tzinfo(self.pytz_code)

    @staticmethod
    def get_tzinfo(tzname: Optional[str], *, silent_fail: bool = False) -> Optional['PytzInfo']:
        """
        Get the corresponding ``pytz`` tzinfo.

        If ``tzname`` is ``None`` or timezone not found and ``silent_fail`` is ``True``, return ``None``.
        """
        if tzname is None:
            return None

        try:
            return PytzInfo(pytz.timezone(tzname))
        except pytz.exceptions.UnknownTimeZoneError as e:
            if silent_fail:
                return None

            raise e


@dataclass
class LanguageInfo:
    name: str
    code: str


class PytzInfo(tzinfo):
    def __init__(self, tz):
        self._base = tz

    def utcoffset(self, dt):
        if self._base is pytz.UTC:
            # UTC does not accept `is_dst`
            return self._base.utcoffset(dt.replace(tzinfo=None))
        else:
            return self._base.utcoffset(dt.replace(tzinfo=None), is_dst=is_now_dst(self._base))

    def dst(self, dt):
        if self._base is pytz.UTC:
            # UTC does not accept `is_dst`
            return self._base.dst(dt.replace(tzinfo=None))
        else:
            return self._base.dst(dt.replace(tzinfo=None), is_dst=is_now_dst(self._base))

    def tzname(self, dt):
        return sec_diff_to_utc_offset(self.utcoffset(dt).total_seconds())

    def localize(self, tz, *, is_dst: bool = False):
        return self._base.localize(tz, is_dst)

    @property
    def tzidentifier(self):
        return self._base.zone

    def __eq__(self, other):
        return type(self) == type(other) and self.tzidentifier == other.tzidentifier

    def __repr__(self):
        return f"<PytzInfo - {self.tzidentifier}>"


def is_now_dst(tz):
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)


HKG = LocaleInfo(_("Asia: Hong Kong"), "Asia/Hong_Kong")
MYS = LocaleInfo(_("Asia: Kuala Lumpur, Malaysia"), "Asia/Kuala_Lumpur")
MAC = LocaleInfo(_("Asia: Macau"), "Asia/Macau")
KOR = LocaleInfo(_("Asia: Seoul, South Korea"), "Asia/Seoul")
SGP = LocaleInfo(_("Asia: Singapore"), "Asia/Singapore")
TWN = LocaleInfo(_("Asia: Taipei, Taiwan"), "Asia/Taipei")
JPN = LocaleInfo(_("Asia: Tokyo, Japan"), "Asia/Tokyo")
GBR = LocaleInfo(_("Europe: London, UK"), "Europe/London")
USA_CENT = LocaleInfo(_("North America: Central Timezone, USA"), "US/Central")
CAN_EAST = LocaleInfo(_("North America: Eastern Timezone, Canada"), "Canada/Eastern")
USA_EAST = LocaleInfo(_("North America: Eastern Timezone, USA"), "US/Eastern")
LAX = LocaleInfo(_("North America: Los Angeles, USA"), "America/Los_Angeles")
USA_MNT = LocaleInfo(_("North America: Mountain Timezone, USA"), "US/Mountain")
NYC = LocaleInfo(_("North America: New York, USA"), "America/New_York")
CAN_PACF = LocaleInfo(_("North America: Pacific Timezone, Canada"), "Canada/Pacific")
USA_PACF = LocaleInfo(_("North America: Pacific Timezone, USA"), "US/Pacific")
YYZ = LocaleInfo(_("North America: Toronto, Canada"), "America/Toronto")
YVR = LocaleInfo(_("North America: Vancouver, Canada"), "America/Vancouver")
ADL = LocaleInfo(_("Oceania: Adelaide, Australia"), "Australia/Adelaide")
NZL = LocaleInfo(_("Oceania: Auckland, New Zealand"), "Pacific/Auckland")
BNE = LocaleInfo(_("Oceania: Brisbane, Australia"), "Australia/Brisbane")
MEL = LocaleInfo(_("Oceania: Melbourne, Australia"), "Australia/Melbourne")
PER = LocaleInfo(_("Oceania: Perth, Australia"), "Australia/Perth")
SYD = LocaleInfo(_("Oceania: Sydney, Australia"), "Australia/Sydney")
UTC = LocaleInfo(_("Universal Time Coordinated"), "UTC")

locales = [
    HKG, MYS, MAC, KOR, SGP, TWN, JPN,
    GBR,
    USA_CENT, CAN_EAST, USA_EAST, LAX, USA_MNT, NYC, CAN_PACF, USA_PACF, YYZ, YVR,
    ADL, NZL, BNE, MEL, PER, SYD,
    UTC
]

default_locale = TWN

EN_US = LanguageInfo(_("English (United States)"), "en_US")
ZH_TW = LanguageInfo(_("Chinese (Taiwan)"), "zh_TW")

languages = [
    EN_US, ZH_TW
]

default_language = ZH_TW
