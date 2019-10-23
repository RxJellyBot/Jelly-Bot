from datetime import tzinfo

from django.utils.translation import gettext_lazy as _

from dataclasses import dataclass
from datetime import datetime

import pytz


@dataclass
class LocaleInfo:
    description: str
    pytz_code: str

    @property
    def current_utc_hr_offset(self) -> str:
        return self.to_tzinfo().tzname(datetime.utcnow())

    def to_tzinfo(self):
        return PytzInfo(pytz.timezone(self.pytz_code))

    @staticmethod
    def get_tzinfo(tzname: str):
        return PytzInfo(pytz.timezone(tzname))


@dataclass
class LanguageInfo:
    name: str
    abbr: str


class PytzInfo(tzinfo):
    def __init__(self, tz):
        self._base = tz

    def utcoffset(self, dt):
        return self._base.utcoffset(dt.replace(tzinfo=None))

    def dst(self, dt):
        return self._base.dst(dt.replace(tzinfo=None))

    def tzname(self, dt):
        return f"UTC{int(self._base.utcoffset(datetime.utcnow()).total_seconds() // 3600):+d}"


def now_utc_aware():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)


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

default_locale = TWN

locales = [
    HKG, MYS, MAC, KOR, SGP, TWN, JPN,
    GBR,
    USA_CENT, CAN_EAST, USA_EAST, LAX, USA_MNT, NYC, CAN_PACF, USA_PACF, YYZ, YVR,
    ADL, NZL, BNE, MEL, PER, SYD,
    UTC
]

languages = [
    LanguageInfo(_("English (United States)"), "en-us"),
    LanguageInfo(_("Chinese (Taiwan)"), "zh-tw")
]

# OPTIMIZE: Store `language` and `locale` in the database using code(int) instead of string
