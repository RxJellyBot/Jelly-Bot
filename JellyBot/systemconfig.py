"""Module that contains various system configurations."""
from abc import ABC

import math
import os

# pylint: disable=too-few-public-methods


HostUrl = os.environ.get("HTTP_HOST") or "http://localhost:8000"
if "HTTP_HOST" in os.environ:
    HostUrl = f"http://{HostUrl}"


class System:
    """System configuration."""

    GitHubRepoIDName = "RaenonX/Jelly-Bot"
    GitHubRepoBranch = "master"

    MaxOneTimeResponses = 5
    MaxSendContentLength = 2000
    MaxSendContentLines = 20

    NoUserTokenNotificationSeconds = 72 * 3600  # 12 Hrs

    DDNSUpdateIntervalSeconds = 3600


class PlatformConfig(ABC):
    """Base of the platform-based configuration."""

    max_responses: int = NotImplementedError
    max_content_length: int = NotImplementedError
    max_content_lines: int = NotImplementedError


class LineApi(PlatformConfig):
    """Plaform configuration of LINE."""

    max_responses = System.MaxOneTimeResponses
    max_content_length = System.MaxSendContentLength
    max_content_lines = System.MaxSendContentLines


class Discord(PlatformConfig):
    """Plaform configuration of Discord."""

    max_responses = System.MaxOneTimeResponses
    max_content_length = System.MaxSendContentLength
    max_content_lines = System.MaxSendContentLines


class Website:
    """Website configuration."""

    NewRegisterThresholdDays = 5
    """Messages about user identity integration will appear within this times of days
    counting from new account creation timestamp."""

    class AutoReply:
        """Auto-reply configuration on website."""

        RankingMaxCount = 200

    class RecentActivity:
        """Recent activity configuration on website."""

        MaxMessageCount = 1000

    class Message:
        """Message stats configuration on website."""

        DefaultPeriodCount = 3


class AutoReply:
    """
    Auto-reply configuration.

    This is different from :class:`Website.AutoReply` as this configuration apply to all auto-reply controls while
    the other one is specifically for website only.
    """

    MaxResponses = 5
    MaxContentLength = System.MaxSendContentLength
    TagSplitter = "|"
    CaseInsensitive = True
    BypassMultilineCDThresholdSeconds = 20


class Database:
    """Database configuration."""

    ExecodeExpirySeconds = 86400  # 24 Hrs
    CacheExpirySeconds = 172800  # 2 Days
    ExtraContentExpirySeconds = 2073600  # 30 Days

    BackupIntervalSeconds = 86400  # 24 Hrs

    class PopularityConfig:
        """Configuration specifically for auto-reply tag popularity score."""

        TimeDiffIntersectHr = 168
        TimeFunctionCoeff = 40

        AppearanceIntersect = 100
        AppearanceFunctionCoeff = 1.4
        AppearanceEquivalentWHr = 5

        TimeCoeffA = 2 * TimeDiffIntersectHr
        TimeCoeffB = -1 / TimeFunctionCoeff
        AppearanceCoeffA = 1 / math.pow(AppearanceIntersect, AppearanceFunctionCoeff - 1)

    class MessageStats:
        """Configuration for raw message data."""

        MaxContentCharacter = 3000


class DataQuery:
    """Data query configuration."""

    TagPopularitySearchCount = 10

    UserNameCacheSize = 3000
    UserNameExpirationSeconds = 129600  # 1.5 Days


class ChannelConfig:
    """Configuration for channel config."""

    VotesToPromoteMod = 7
    VotesToPromoteAdmin = 20


class Email:
    """configuration of various email-related controls."""

    EmailCacheExpirySeconds = 3600  # 60 mins
    DefaultSubject = "[BOT] Email Notification"
    DefaultPrefix = "[BOT] "


class ExecodeManager:
    """Execode manager configuration."""

    ChannelRegisterExecodeCooldownSeconds = 60


class Bot:
    """Bot configuration."""

    Prefix = "JC"
    Splitters = [" ", "\n"]

    RandomChoiceSplitter = "  "
    RandomChoiceWeightSplitter = " "
    RandomChoiceOptionLimit = 20
    RandomChoiceCountLimit = 1000

    CaseInsensitive = True
    CaseInsensitivePrefix = True

    class AutoReply:
        """Auto-reply configuration for controls via the bot only."""

        DefaultPinned = False
        DefaultPrivate = False
        DefaultTags = []
        DefaultCooldownSecs = 0

        MaxContentResultLength = 100

        DeleteDataMins = 3

        RankingMaxCount = 10
        RankingMaxContentLength = 35

    class RecentActivity:
        """Recent activity configuration for controls via the bot only."""

        CooldownSeconds = 30
        DefaultLimitCountLink = 100
        DefaultLimitCountDirect = 10

    class Timer:
        """Timer configuration for controls via the bot only."""

        AutoDeletionDays = 7
        MaxNotifyRangeSeconds = 14400
        MessageFrequencyRangeMin = 1440  # 1 Day

    class RemoteControl:
        """Remote control configuration for controls via the bot ony."""

        IdleDeactivateSeconds = 600  # 10 min


class ExtraService:
    """Configuration of various extra services."""

    class Sticker:
        """Sticker configuration for extra service only."""

        MaxStickerTempFileLifeSeconds = 86400  # 1 Day
