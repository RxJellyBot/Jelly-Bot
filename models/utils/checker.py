"""Implementations of the data checker."""
from abc import ABC, abstractmethod
from threading import Thread
from typing import Optional, List, Tuple, Dict

from pymongo.cursor import Cursor

from mongodb.utils import BulkWriteDataHolder
from models.field import ModelField
from models import ModelDefaultValueExt, OID_KEY
from extutils.flags import FlagCodeEnum
from extutils.emailutils import MailSender
from extutils.logger import LoggerSkeleton

from ..rpdata import PendingRepairDataModel

__all__ = ("ModelFieldChecker",)

logger = LoggerSkeleton("mongo.modelcheck", logger_name_env="MODEL_CHECK")


class DataRepairResult(FlagCodeEnum):
    """Result of the data repairment."""

    REQUIRED_MISSING = 0
    NO_PATCH_NEEDED = 1
    REPAIRED = 2


class FieldCheckerBase(ABC):
    """Base class of the data field checker."""

    def __init__(self, col_inst):
        self._col_inst = col_inst
        self._model_cls = col_inst.get_model_cls()

    def perform_check(self):
        """Method to be called to perform the check."""
        self.pre_execute()
        self.execute()
        self.post_execute()

    def pre_execute(self):
        """Actions to be executed **before** the check."""
        logger.logger.info("Started executing `%s` on <%s>...", self.__class__.__name__, self._col_inst.full_name)

    @abstractmethod
    def execute(self):
        """Actual execution of the check."""
        raise NotImplementedError()

    def post_execute(self):
        """Actions to be executed **after** the check."""
        logger.logger.info("Done executing `%s` on <%s>.", self.__class__.__name__, self._col_inst.full_name)


class ModelFieldChecker:
    """
    Checker to check the if the data stored in the database matches the model defined in the code.

    This checker will attempt to repair the data if it does not match the corresponding model.

    If if fails to repair, the data will be moved to the designated temporary location for manual recovery.
    An email report will be sent to notify the developer at the same time.
    """

    @staticmethod
    def check_async(col_inst):
        """
        Perform the check asynchronously.

        :param col_inst: collection instance to be checked
        """
        Thread(target=ModelFieldChecker.check, args=(col_inst,)).start()

    @staticmethod
    def check(col_inst):
        """
        Method to start the check.

        :param col_inst: collection instance to be checked
        """
        ModelFieldChecker.CheckDefaultValue(col_inst).perform_check()

    class CheckDefaultValue(FieldCheckerBase):
        """
        Check the default values of the fields of a data model.

        If the field does not match its given default value, then try to update it.

        If the update is failed, move that data entry to a specific database for repairment.
        """

        def __init__(self, col_inst):
            super().__init__(col_inst)

            # [(Json Key, Model Class), (Json Key, Model Class), ...]
            self._model_field_mdl_class = []

            for f in self._model_cls.model_fields():
                if isinstance(f, ModelField):
                    self._model_field_mdl_class.append((f.key, f.model_cls))

        def execute(self):
            """
            This checks the default values of the fields of a data model.

            If the field does not match its given default value, then try to update it.

            If the update is failed, move that data entry to a specific database for repairment.
            """
            from mongodb.factory import PendingRepairDataManager  # pylint: disable=import-outside-toplevel

            find_query = self._build_find_query()

            if not find_query:
                self.post_execute()
                return

            potential_repair_needed = self._col_inst.find(find_query)

            if not self._col_inst.find_one(find_query):
                self.post_execute()
                return

            required_write_holder = PendingRepairDataManager.new_bulk_holder(self._col_inst)
            repaired_write_holder = BulkWriteDataHolder(self._col_inst)

            logger.logger.warning("Scanning potential repairments required data "
                                  "in database <%s>...", self._col_inst.full_name)

            self._scan_data(potential_repair_needed, required_write_holder, repaired_write_holder)

            if repaired_write_holder.holding_data:
                logger.logger.warning("Updating repaired data to database <%s>...", self._col_inst.full_name)
                repaired_write_holder.complete()

            if required_write_holder.holding_data:
                logger.logger.warning("Manual repair required in database <%s>.", self._col_inst.full_name)

                result = required_write_holder.complete()
                logger.logger.warning("Sending notification email...")
                self._send_mail_async(result, required_write_holder)

            self.post_execute()

        @staticmethod
        def _build_key_filter(*, prefix: str = None, model_cls=None):
            if prefix is not None:
                prefix = prefix + "."
            else:
                prefix = ""

            or_list = []

            if model_cls:
                for jk, default in map(lambda f: (f.key, f.default_value), model_cls.model_fields()):
                    if default != ModelDefaultValueExt.Optional:
                        or_list.append({f"{prefix}{jk}": {"$exists": False}})

            return or_list

        def _build_find_query(self):
            or_list = self._build_key_filter(model_cls=self._model_cls)

            for key, model_cls in self._model_field_mdl_class:
                or_list.extend(self._build_key_filter(prefix=key, model_cls=model_cls))

            if not or_list:
                return None

            return {"$or": or_list}

        def _scan_data(self, potential_repair_needed: Cursor, required_write_holder: BulkWriteDataHolder,
                       repaired_write_holder: BulkWriteDataHolder):
            counter: Dict[FlagCodeEnum, int] = {k: 0 for k in DataRepairResult}

            for data in potential_repair_needed:
                result, rpdata = self._repair_single_data(required_write_holder, data)

                counter[result] += 1

                if rpdata:
                    repaired_write_holder.replace_single(rpdata)

            self._print_scanning_result(counter)

        def _repair_single_data(self, required_write_holder: BulkWriteDataHolder, data: dict) -> \
                Tuple[DataRepairResult, Optional[dict]]:
            missing = []
            changed = self._repair_fields(data, self._model_cls, missing)

            # Check all fields of the model field
            for key, model_cls in self._model_field_mdl_class:
                # `self.repair_fields()` first so it will always being executed (short circuit)
                changed = self._repair_fields(data[key], model_cls, missing) or changed

            if missing:
                required_write_holder.repsert_single(
                    {f"{PendingRepairDataModel.Data.key}.{OID_KEY}": data[OID_KEY]},
                    PendingRepairDataModel(Data=data, MissingKeys=missing))

                self._col_inst.delete_one({OID_KEY: data[OID_KEY]})
                return DataRepairResult.REQUIRED_MISSING, None

            repair_result = DataRepairResult.REPAIRED if changed else DataRepairResult.NO_PATCH_NEEDED
            repaired_data = data if changed else None

            return repair_result, repaired_data

        def _repair_fields(self, data: dict, model_cls, missing: List[str]) -> bool:
            changed = False

            for json_key, default_val in map(lambda f: (f.key, f.default_value), model_cls.model_fields()):
                if json_key not in data:
                    try:
                        if default_val == ModelDefaultValueExt.Required:
                            missing.append(json_key)
                        elif default_val == ModelDefaultValueExt.Optional:
                            pass  # Optional so no change
                        else:
                            data[json_key] = default_val
                            changed = True
                    except KeyError as ex:
                        raise ValueError(f"Default value rule not set "
                                         f"for json key `{json_key}` in `{self._model_cls.__qualname__}`.") from ex

            return changed

        @staticmethod
        def _print_scanning_result(counter: Dict[FlagCodeEnum, int]):
            if counter[DataRepairResult.NO_PATCH_NEEDED] > 0:
                logger.logger.info("\t%d do not need any patches.", counter[DataRepairResult.NO_PATCH_NEEDED])

            if counter[DataRepairResult.REPAIRED] > 0:
                logger.logger.info("\t%d data repaired.", counter[DataRepairResult.REPAIRED])

            if counter[DataRepairResult.REQUIRED_MISSING] > 0:
                logger.logger.info(
                    "\t%d data missing some required fields.", counter[DataRepairResult.REQUIRED_MISSING])

        def _send_mail_async(self, result_list: list, required_write_holder: BulkWriteDataHolder):
            content = f"<b>{required_write_holder.holded_count} data</b> need manual repairments.<br>" \
                      f"Data are originally stored in <code>{self._col_inst.full_name}</code>.<br>" \
                      f"<br>" \
                      f"Results list:<br><ul>" \
                      f"{''.join(f'<li>{repr(r)}</li>' for r in result_list)}" \
                      f"</ul>"

            MailSender.send_email_async(content, subject="Action Needed: Manual Data repairments required")
