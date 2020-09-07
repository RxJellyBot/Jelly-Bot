"""Implementations of the data/result models related to stats."""
from .base import DailyResult, HourlyResult
from .bot import BotFeatureUsageResult, BotFeatureHourlyAvgResult, BotFeaturePerUserUsageResult
from .main import APIStatisticModel, MessageRecordModel, BotFeatureUsageModel
from .msg import (
    MemberMessageCountEntry, MemberMessageCountResult, HourlyIntervalAverageMessageResult, DailyMessageResult,
    MemberMessageByCategoryEntry, MemberMessageByCategoryResult, MemberDailyMessageResult, MeanMessageResultGenerator,
    CountBeforeTimeResult
)
