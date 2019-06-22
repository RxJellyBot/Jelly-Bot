class AutoReply:
    MAX_RESPONSES = 5
    MAX_CONTENT_LENGTH = 2000


class Database:
    StatisticsExpirySeconds = 15811200  # 183 Days
    TokenActionExpirySeconds = 86400  # 24 Hrs
    CacheExpirySeconds = 172800  # 3 Days
    BulkWriteCount = 300


class ChannelConfig:
    VotesToPromoteMod = 7
    VotesToPromoteAdmin = 20


class Email:
    DefaultSubject = "Email Notification from Jelly BOT"
    DefaultPrefix = "Jelly BOT - "
