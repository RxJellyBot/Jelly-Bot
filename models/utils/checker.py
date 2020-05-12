from abc import ABC, abstractmethod
from threading import Thread
from typing import Optional, List, Tuple

from pymongo.cursor import Cursor

from mongodb.utils import BulkWriteDataHolder
from models.field import ModelField
from models import ModelDefaultValueExt, OID_KEY
from extutils.flags import FlagCodeEnum
from extutils.emailutils import MailSender
from extutils.logger import LoggerSkeleton

from ..rpdata import PendingRepairDataModel

__all__ = ["ModelFieldChecker"]

logger = LoggerSkeleton("mongo.modelcheck", logger_name_env="MODEL_CHECK")


# TODO: #285 and related tests


class DataRepairResult(FlagCodeEnum):
    REQUIRED_MISSING = 0
    NO_PATCH_NEEDED = 1
    REPAIRED = 2


class FieldCheckerBase(ABC):
    def __init__(self, col_inst):
        self._col_inst = col_inst
        self._model_cls = col_inst.data_model

    def perform_check(self):
        """Method to be called to perform the check."""
        self.pre_execute()
        self.execute()
        self.post_execute()

    def pre_execute(self):
        logger.logger.info(f"Started executing `{self.__class__.__name__}` on <{self._col_inst.full_name}>...")

    @abstractmethod
    def execute(self):
        raise NotImplementedError()

    def post_execute(self):
        logger.logger.info(f"Done executing `{self.__class__.__name__}` on <{self._col_inst.full_name}>.")


class ModelFieldChecker:
    @staticmethod
    def check_async(col_inst):
        Thread(target=ModelFieldChecker.check, args=(col_inst,)).start()

    @staticmethod
    def check(col_inst):
        ModelFieldChecker.CheckDefaultValue(col_inst).perform_check()

    class CheckDefaultValue(FieldCheckerBase):
        """
        Checks the default values of the fields of a data model.

        If the field does not match its given default value, then try to update it.

        If the update is failed, move that data entry to a specific database for repairment.
        """

        def __init__(self, col_inst):
            super().__init__(col_inst)

            # [(Json Key, Default Value), (Json Key, Default Value), ...]
            self._model_default_vals = []
            # [(Json Key, Model Class), (Json Key, Model Class), ...]
            self._model_field_mdl_class = []

            for f in self._model_cls.model_fields().values():
                self._model_default_vals.append((f.key, f.default_value))

                if isinstance(f, ModelField):
                    self._model_field_mdl_class.append((f.key, f.model_cls))

        def execute(self):
            """
            This checks the default values of the fields of a data model.

            If the field does not match its given default value, then try to update it.

            If the update is failed, move that data entry to a specific database for repairment.
            """
            from mongodb.factory import PendingRepairDataManager

            find_query = self.build_find_query()

            if not find_query:
                self.post_execute()
                return

            potential_repair_needed = self._col_inst.find(find_query)

            if potential_repair_needed.count() == 0:
                self.post_execute()
                return

            required_write_holder = PendingRepairDataManager.new_bulk_holder(self._col_inst)
            repaired_write_holder = BulkWriteDataHolder(self._col_inst)

            logger.logger.warning(f"Scanning potential repairments required data "
                                  f"in database <{self._col_inst.full_name}>...")

            self.scan_data(potential_repair_needed, required_write_holder, repaired_write_holder)

            if repaired_write_holder.holding_data:
                logger.logger.warning(f"Updating repaired data to database <{self._col_inst.full_name}>...")
                repaired_write_holder.complete()

            if required_write_holder.holding_data:
                logger.logger.warning(f"Manual repair required in database <{self._col_inst.full_name}>.")

                result = required_write_holder.complete()
                logger.logger.warning(f"Sending notification email...")
                self.send_mail_async(result, required_write_holder)

            self.post_execute()

        @staticmethod
        def build_key_filter(*, prefix: str = None, model_cls=None):
            if prefix is not None:
                prefix = prefix + "."
            else:
                prefix = ""

            or_list = []

            if model_cls:
                for jk, default in map(lambda f: (f.key, f.default_value), model_cls.model_fields().values()):
                    if default != ModelDefaultValueExt.Optional:
                        or_list.append({f"{prefix}{jk}": {"$exists": False}})

            return or_list

        def build_find_query(self):
            or_list = self.build_key_filter(model_cls=self._model_cls)

            for key, model_cls in self._model_field_mdl_class:
                or_list.extend(self.build_key_filter(prefix=key, model_cls=model_cls))

            if or_list:
                return {"$or": or_list}
            else:
                return None

        def scan_data(self, potential_repair_needed: Cursor, required_write_holder: BulkWriteDataHolder,
                      repaired_write_holder: BulkWriteDataHolder):
            counter = {k: 0 for k in DataRepairResult}

            for data in potential_repair_needed:
                result, rpdata = self.repair_single_data(required_write_holder, data)

                counter[result] += 1

                if rpdata:
                    repaired_write_holder.replace_single(rpdata)

            self.print_scanning_result(counter)

        def repair_single_data(self, required_write_holder: BulkWriteDataHolder, data: dict) -> \
                Tuple[DataRepairResult, Optional[dict]]:
            changed = [False]  # Make it a list so the value inside can be referenced as pointer not value
            missing = []

            self.repair_fields(data, changed, missing)

            # Check all fields of the model field
            for key, model_cls in self._model_field_mdl_class:
                self.repair_fields(data[key], changed, missing)

            if len(missing) > 0:
                required_write_holder.repsert_single(
                    {f"{PendingRepairDataModel.Data.key}.{OID_KEY}": data[OID_KEY]},
                    PendingRepairDataModel(Data=data, MissingKeys=missing))

                self._col_inst.delete_one({OID_KEY: data[OID_KEY]})
                return DataRepairResult.REQUIRED_MISSING, None
            else:
                return DataRepairResult.REPAIRED if changed else DataRepairResult.NO_PATCH_NEEDED, \
                       data if changed else None

        def repair_fields(self, data: dict, changed: List[bool], missing: List[bool]):
            for json_key, default_val in self._model_default_vals:
                if json_key not in data:
                    try:
                        if default_val == ModelDefaultValueExt.Required:
                            missing.append(json_key)
                        elif default_val == ModelDefaultValueExt.Optional:
                            pass  # Optional so no change
                        else:
                            data[json_key] = default_val
                            changed[0] = True
                    except KeyError:
                        raise ValueError(f"Default value rule not set "
                                         f"for json key `{json_key}` in `{self._model_cls.__qualname__}`.")

        @staticmethod
        def print_scanning_result(counter: dict):
            if counter[DataRepairResult.NO_PATCH_NEEDED] > 0:
                logger.logger.info(f"\t{counter[DataRepairResult.NO_PATCH_NEEDED]} do not need any patches.")

            if counter[DataRepairResult.REPAIRED] > 0:
                logger.logger.info(f"\t{counter[DataRepairResult.REPAIRED]} data repaired.")

            if counter[DataRepairResult.REQUIRED_MISSING] > 0:
                logger.logger.info(
                    f"\t{counter[DataRepairResult.REQUIRED_MISSING]} data missing some required fields.")

        def send_mail_async(self, result_list: list, required_write_holder: BulkWriteDataHolder):
            content = f"<b>{required_write_holder.holded_count} data</b> need manual repairments.<br>" \
                      f"Data are originally stored in <code>{self._col_inst.full_name}</code>.<br>" \
                      f"<br>" \
                      f"Results list:<br><ul>" \
                      f"{''.join(f'<li>{repr(r)}</li>' for r in result_list)}" \
                      f"</ul>"

            MailSender.send_email_async(content, subject="Action Needed: Manual Data repairments required")
