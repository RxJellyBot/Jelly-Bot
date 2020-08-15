from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import APICommand
from models import APIStatisticModel
from mongodb.factory import APIStatisticsManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin

__all__ = ["TestAPIStatisticsManager"]


class TestAPIStatisticsManager(TestTimeComparisonMixin, TestModelMixin, TestDatabaseMixin):
    USER_OID = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [APIStatisticsManager]

    def test_record_stats(self):
        ts = now_utc_aware()

        result = APIStatisticsManager.record_stats(
            APICommand.AR_ADD, self.USER_OID, {"A": "B"}, {"C": "D"}, True, {"E": "F"}, "/p", "/p/s")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, APIStatisticModel(
            ApiAction=APICommand.AR_ADD, SenderOid=self.USER_OID, Parameter={"A": "B"},
            Response={"C": "D"}, Success=True, Timestamp=result.model.timestamp,
            PathParameter={"E": "F"}, PathInfo="/p", PathInfoFull="/p/s"))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, ts, self.db_ping_ms() * 5)
