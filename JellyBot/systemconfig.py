from abc import ABC

import math
import os


HostUrl = os.environ.get("HTTP_HOST") or "http://localhost:8000"
if "HTTP_HOST" in os.environ:
    HostUrl = f"http://{HostUrl}"


class System:
    GitHubRepoIDName = "RaenonX/Jelly-Bot"
    GitHubRepoBranch = "master"

    MaxOneTimeResponses = 5
    MaxSendContentLength = 2000
    MaxSendContentLines = 20

    NoUserTokenNotificationSeconds = 72 * 3600  # 12 Hrs

    DDNSUpdateIntervalSeconds = 3600


class PlatformConfig(ABC):
    max_responses: int = NotImplementedError
    max_content_length: int = NotImplementedError
    max_content_lines: int = NotImplementedError


class LineApi(PlatformConfig):
    max_responses = System.MaxOneTimeResponses
    max_content_length = System.MaxSendContentLength
    max_content_lines = System.MaxSendContentLines


class Discord(PlatformConfig):
    max_responses = System.MaxOneTimeResponses
    max_content_length = System.MaxSendContentLength
    max_content_lines = System.MaxSendContentLines


class Website:
    NewRegisterThresholdDays = 5

    class AutoReply:
        RankingMaxCount = 200

    class RecentActivity:
        MaxMessageCount = 1000

    class Message:
        DefaultPeriodCount = 3


class AutoReply:
    MaxResponses = 5
    MaxContentLength = System.MaxSendContentLength
    TagSplitter = "|"
    CaseInsensitive = True
    BypassMultilineCDThresholdSeconds = 20


class Database:
    ExecodeExpirySeconds = 86400  # 24 Hrs
    CacheExpirySeconds = 172800  # 2 Days
    ExtraContentExpirySeconds = 2073600  # 30 Days
    BulkWriteCount = 300

    BackupIntervalSeconds = 86400  # 24 Hrs

    class PopularityConfig:
        TimeDiffIntersectHr = 168
        TimeFunctionCoeff = 40

        AppearanceIntersect = 100
        AppearanceFunctionCoeff = 1.4
        AppearanceEquivalentWHr = 5

        TimeCoeffA = 2 * TimeDiffIntersectHr
        TimeCoeffB = -1 / TimeFunctionCoeff
        AppearanceCoeffA = 1 / math.pow(AppearanceIntersect, AppearanceFunctionCoeff - 1)

    class MessageStats:
        MaxContentCharacter = 3000


class DataQuery:
    TagPopularitySearchCount = 10

    UserNameCacheSize = 3000
    UserNameExpirationSeconds = 129600  # 1.5 Days


class ChannelConfig:
    VotesToPromoteMod = 7
    VotesToPromoteAdmin = 20


class Email:
    EmailCacheExpirySeconds = 3600  # 60 mins
    DefaultSubject = "Email Notification from Jelly BOT"
    DefaultPrefix = "Jelly BOT - "


class ExecodeManager:
    ChannelRegisterExecodeCooldownSeconds = 60


class Bot:
    Prefix = "JC"
    Splitters = [" ", "\n"]

    RandomChoiceSplitter = "  "
    RandomChoiceWeightSplitter = " "
    RandomChoiceOptionLimit = 20
    RandomChoiceCountLimit = 1000

    CaseInsensitive = True
    CaseInsensitivePrefix = True

    class AutoReply:
        DefaultPinned = False
        DefaultPrivate = False
        DefaultTags = []
        DefaultCooldownSecs = 0

        MaxContentResultLength = 100

        DeleteDataMins = 3

        RankingMaxCount = 10
        RankingMaxContentLength = 35

    class RecentActivity:
        CooldownSeconds = 30
        DefaultLimitCountLink = 100
        DefaultLimitCountDirect = 15

    class Timer:
        AutoDeletionDays = 7
        MaxNotifyRangeSeconds = 14400
        MessageFrequencyRangeMin = 1440  # 1 Day

    class RemoteControl:
        IdleDeactivateSeconds = 600  # 10 mins


class ExtraService:
    class Maskfinder:
        TargetRangeMi = 200
