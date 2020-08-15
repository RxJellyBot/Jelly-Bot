"""Module containing the operations related to locale."""
from dataclasses import dataclass
from datetime import datetime, tzinfo, timedelta
from typing import Optional, List

from django.utils.translation import gettext_lazy as _
import pytz


def sec_diff_to_utc_offset(s_diff: float):
    """
    Takes second difference ``s_diff`` and translate it into UTC offset string (example: +0500).

    :param s_diff: utc offset second difference
    :return: translated offset string in either for example, +0500 or -0500
    """
    # pylint: disable=C0103

    is_pos = s_diff >= 0
    s_diff = int(abs(s_diff))
    h = s_diff // 3600
    m = (s_diff - h * 3600) // 60

    return f"{'+' if is_pos else '-'}{h:02}{m:02}"


@dataclass
class LocaleInfo:
    """Class representing a locale info."""

    description: str
    pytz_code: str

    @property
    def utc_offset_str(self) -> str:
        """
        Get the UTC offset string (for example, UTC+0500) of this locale info.

        :return: UTC offset string
        """
        return f"UTC{self.to_tzinfo().tzname(datetime.utcnow())}"

    def to_tzinfo(self) -> tzinfo:
        """
        Get the :class:`tzinfo` of this :class:`LocaleInfo`.

        :return: a corresponding `tzinfo` of this `LocaleInfo`
        """
        return LocaleInfo.get_tzinfo(self.pytz_code)

    @staticmethod
    def get_tzinfo(tzidentifier: Optional[str], *, silent_fail: bool = False) -> Optional['PytzInfo']:
        """
        Get the corresponding ``pytz`` :class:`tzinfo`.

        If ``tzname`` is ``None`` or timezone not found and ``silent_fail`` is ``True``, returns ``None``.

        Reference: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

        :param tzidentifier: timezone identifier defined in IANA timezone database
        :param silent_fail: if to silently fail if not found
        :return: a `PytzInfo` if timezone found
        """
        if tzidentifier is None:
            return None

        try:
            return PytzInfo(pytz.timezone(tzidentifier))
        except pytz.exceptions.UnknownTimeZoneError as ex:
            if silent_fail:
                return None

            raise ex


@dataclass
class LanguageInfo:
    """Class representing a language info."""

    name: str
    code: str


class PytzInfo(tzinfo):
    """A customized :class:`tzinfo` based on the :class:`tzinfo` from ``pytz``."""

    def __init__(self, tz):
        self._base = tz

    def utcoffset(self, dt):
        if self._base is pytz.UTC:
            # UTC does not accept `is_dst`
            return self._base.utcoffset(dt.replace(tzinfo=None))

        return self._base.utcoffset(dt.replace(tzinfo=None), is_dst=is_now_dst(self._base))

    def dst(self, dt):
        if self._base is pytz.UTC:
            # UTC does not accept `is_dst`
            return self._base.dst(dt.replace(tzinfo=None))

        return self._base.dst(dt.replace(tzinfo=None), is_dst=is_now_dst(self._base))

    def tzname(self, dt):
        return sec_diff_to_utc_offset(self.utcoffset(dt).total_seconds())

    def localize(self, dt: datetime, *, is_dst: bool = False) -> datetime:
        """
        Localize the datetime ``dt``.

        ``dt`` must be tz-naive.

        Uses ``is_dst`` to determine whether DST is in effect if unable to determine.

        :param dt: datetime to be localized
        :param is_dst: default setting of DST if unable to determine
        :return: a localized `datetime`
        :raises ValueError: if `dt` is not tz-naive
        """
        return self._base.localize(dt, is_dst)

    @property
    def tzidentifier(self):
        """
        Returns the ``pytz`` timezone identifier of this :class:`tzinfo`.

        :return: pytz timezone identifier
        """
        return self._base.zone

    def __eq__(self, other):
        return type(self) == type(other) and self.tzidentifier == other.tzidentifier  # pylint: disable=C0123

    def __repr__(self):
        return f"<PytzInfo - {self.tzidentifier}>"


def is_now_dst(tz) -> bool:
    """
    Check if DST is in effect in ``tz`` currently.

    :param tz: timezone to check DST
    :return: if DST is in effect
    """
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)


# region Locale info


AUS_ADL = LocaleInfo(_("Oceania: Adelaide, Australia"), "Australia/Adelaide")
AUS_BNE = LocaleInfo(_("Oceania: Brisbane, Australia"), "Australia/Brisbane")
AUS_MEL = LocaleInfo(_("Oceania: Melbourne, Australia"), "Australia/Melbourne")
AUS_PER = LocaleInfo(_("Oceania: Perth, Australia"), "Australia/Perth")
AUS_SYD = LocaleInfo(_("Oceania: Sydney, Australia"), "Australia/Sydney")
CAN_EAST = LocaleInfo(_("North America: Eastern Timezone, Canada"), "Canada/Eastern")
CAN_PACF = LocaleInfo(_("North America: Pacific Timezone, Canada"), "Canada/Pacific")
CAN_YYZ = LocaleInfo(_("North America: Toronto, Canada"), "America/Toronto")
CAN_YVR = LocaleInfo(_("North America: Vancouver, Canada"), "America/Vancouver")
HKG = LocaleInfo(_("Asia: Hong Kong"), "Asia/Hong_Kong")
JPN = LocaleInfo(_("Asia: Tokyo, Japan"), "Asia/Tokyo")
KOR = LocaleInfo(_("Asia: Seoul, South Korea"), "Asia/Seoul")
MAC = LocaleInfo(_("Asia: Macau"), "Asia/Macau")
MYS = LocaleInfo(_("Asia: Kuala Lumpur, Malaysia"), "Asia/Kuala_Lumpur")
NZL = LocaleInfo(_("Oceania: Auckland, New Zealand"), "Pacific/Auckland")
SGP = LocaleInfo(_("Asia: Singapore"), "Asia/Singapore")
TWN = LocaleInfo(_("Asia: Taipei, Taiwan"), "Asia/Taipei")
GBR = LocaleInfo(_("Europe: London, UK"), "Europe/London")
USA_CENT = LocaleInfo(_("North America: Central Timezone, USA"), "US/Central")
USA_EAST = LocaleInfo(_("North America: Eastern Timezone, USA"), "US/Eastern")
USA_LAX = LocaleInfo(_("North America: Los Angeles, USA"), "America/Los_Angeles")
USA_MNT = LocaleInfo(_("North America: Mountain Timezone, USA"), "US/Mountain")
USA_NYC = LocaleInfo(_("North America: New York, USA"), "America/New_York")
USA_PACF = LocaleInfo(_("North America: Pacific Timezone, USA"), "US/Pacific")
UTC = LocaleInfo(_("Universal Time Coordinated"), "UTC")

_LOCALES = [
    AUS_ADL, AUS_BNE, AUS_MEL, AUS_PER, AUS_SYD,
    CAN_EAST, CAN_PACF, CAN_YYZ, CAN_YVR,
    HKG, JPN, KOR, MAC, MYS, NZL, SGP, TWN, GBR,
    USA_CENT, USA_EAST, USA_LAX, USA_MNT, USA_NYC, USA_PACF,
    UTC
]


def get_locales() -> List[LocaleInfo]:
    """
    Get the list of the available locales.

    Currently available locales:

    - Australia (Adelaide)

    - Australia (Brisbane)

    - Australia (Melbourne)

    - Australia (Perth)

    - Australia (Sydney)

    - Canada (Eastern)

    - Canada (Pacific)

    - Canada (Toronto)

    - Canada (Vancouver)

    - Hong Kong

    - Japan

    - Korea

    - Macau

    - Malaysia

    - New Zealand (Auckland)

    - Singapore

    - Taiwan

    - UK

    - USA (Central)

    - USA (Eastern)

    - USA (Los Angeles)

    - USA (Mountain)

    - USA (NYC)

    - USA (Pacific)

    - UTC

    :return: list of available locales
    """
    return _LOCALES


DEFAULT_LOCALE = TWN

# endregion


# region Language info


EN_US = LanguageInfo(_("English (United States)"), "en_US")
ZH_TW = LanguageInfo(_("Chinese (Taiwan)"), "zh_TW")

_LANGUAGES = [
    EN_US, ZH_TW
]


def get_languages() -> List[LanguageInfo]:
    """
    Get the list of the available languages.

    Currently available languages:

    - ``en-US`` - English (US)

    - ``zh-TW`` - Traditional Chinese (Taiwan)

    :return: list of available languages
    """
    return _LANGUAGES


DEFAULT_LANGUAGE = ZH_TW

# endregion
