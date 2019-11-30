from models import Model, ModelDefaultValueExt
from models.field import DateTimeField, BooleanField, IntegerField, TextField, ObjectIDField


class TimerModel(Model):
    KeywordOid = ObjectIDField("kw")
    Title = TextField("t", default=ModelDefaultValueExt.Required)
    TargetTime = DateTimeField("tt", default=ModelDefaultValueExt.Required)
    ContinueOnTimeUp = BooleanField("c", default=False)
    PeriodSeconds = IntegerField("p", default=ModelDefaultValueExt.Optional)

    @property
    def is_periodic(self) -> bool:
        return self.period_seconds > 0
