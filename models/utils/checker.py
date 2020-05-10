from threading import Thread
from typing import Optional, Type, List

from pymongo.collection import Collection
from pymongo.cursor import Cursor

from JellyBot.systemconfig import Database
from mongodb.utils import BulkWriteDataHolder
from models import ModelDefaultValueExt, OID_KEY, Model
from models.field import ModelField
from extutils.flags import FlagCodeEnum
from extutils.emailutils import MailSender
from extutils.logger import LoggerSkeleton

from ..rpdata import PendingRepairDataModel

__all__ = ["ModelFieldChecker"]

logger = LoggerSkeleton("mongo.modelcheck", logger_name_env="MODEL_CHECK")


class DataRepairResult(FlagCodeEnum):
    REQUIRED_MISSING = 0
    NO_PATCH_NEEDED = 1
    REPAIRED = 2


class ModelFieldChecker:
    @staticmethod
    def check_async(col_inst):
        Thread(target=ModelFieldChecker.check, args=(col_inst,)).start()

    @staticmethod
    def check(col_inst):
        from mongodb.factory import PendingRepairDataManager
        logger.logger.info(f"Scanning <{col_inst.full_name}>...")

        or_list = _build_find_or_list_(col_inst.data_model)

        if len(or_list) > 0:
            potential_repair_needed = col_inst.find({"$or": or_list})

            if potential_repair_needed.count() > 0:
                required_write_holder = PendingRepairDataManager.new_bulk_holder(col_inst)
                repaired_write_holder = BulkWriteDataHolder(col_inst, Database.BulkWriteCount)

                logger.logger.warning(f"Scanning potential repairments required data "
                                      f"in database <{col_inst.full_name}>...")

                _scan_data_(col_inst, potential_repair_needed, required_write_holder, repaired_write_holder)

                if repaired_write_holder.holding_data:
                    logger.logger.warning(f"Updating repaired data to database <{col_inst.full_name}>...")
                    repaired_write_holder.complete()

                if required_write_holder.holding_data:
                    logger.logger.warning(f"Manual repair required in database <{col_inst.full_name}>.")

                    result = required_write_holder.complete()
                    logger.logger.warning(f"Sending notification email...")
                    _send_mail_async_(col_inst, result, required_write_holder)

        logger.logger.info(f"Done scanning <{col_inst.full_name}>.")


def _get_dict_models_(model_cls: Type[Model]):
    """
    :return: [(Json Key, Default Value), (Json Key, Default Value), ...]
    """
    return [(getattr(model_cls, k).key, getattr(model_cls, k).model_cls) for k in model_cls.model_fields()
            if isinstance(getattr(model_cls, k), ModelField)]


def _get_default_vals_(model_cls: Type[Model]):
    """
    :return: [(Json Key, Default Value), (Json Key, Default Value), ...]
    """
    return [(getattr(model_cls, k).key, getattr(model_cls, k).default_value) for k in model_cls.model_fields()]


def _build_find_or_list_(model_cls: Type[Model]):
    or_list = _bulid_filter_(model_cls)

    for key, model_cls in _get_dict_models_(model_cls):
        or_list.extend(_bulid_filter_(model_cls, key))

    return or_list


def _bulid_filter_(model_cls: Type[Model], prefix: str = None):
    if prefix is not None:
        prefix = prefix + "."
    else:
        prefix = ""

    or_list = []

    for key, val in _get_default_vals_(model_cls):
        if val != ModelDefaultValueExt.Optional:
            or_list.append({f"{prefix}{key}": {"$exists": False}})

    return or_list


def _scan_data_(col_inst, potential_repair_needed: Cursor,
                required_write_holder: BulkWriteDataHolder, repaired_write_holder: BulkWriteDataHolder):
    counter = {k: 0 for k in DataRepairResult}

    for data in potential_repair_needed:
        result, rpdata = _repair_single_data_(col_inst, required_write_holder, data)

        counter[result] += 1

        if rpdata:
            repaired_write_holder.replace_single(rpdata)

    _print_scanning_result_(counter)


def _repair_single_data_(col_inst: Collection, required_write_holder: BulkWriteDataHolder, data: dict) -> (
        DataRepairResult, Optional[dict]):
    changed = [False]  # Make it a list so the value inside can be referenced as pointer not value
    missing = []

    _repair_fields_(col_inst.data_model, data, changed, missing)

    # Check all fields of the model field
    for key, model_cls in _get_dict_models_(col_inst.data_model):
        _repair_fields_(model_cls, data[key], changed, missing)

    if len(missing) > 0:
        required_write_holder.repsert_single(
            {f"{PendingRepairDataModel.Data.key}.{OID_KEY}": data[OID_KEY]},
            PendingRepairDataModel(Data=data, MissingKeys=missing))

        col_inst.delete_one({OID_KEY: data[OID_KEY]})
        return DataRepairResult.REQUIRED_MISSING, None
    else:
        return DataRepairResult.REPAIRED if changed else DataRepairResult.NO_PATCH_NEEDED, data if changed else None


def _repair_fields_(model_cls: Type[Model], data: dict, changed: List[bool], missing: List[bool]):
    for json_key, default_val in _get_default_vals_(model_cls):
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
                                 f"for json key `{json_key}` in `{model_cls.__qualname__}`.")


def _print_scanning_result_(counter: dict):
    if counter[DataRepairResult.NO_PATCH_NEEDED] > 0:
        logger.logger.info(f"\t{counter[DataRepairResult.NO_PATCH_NEEDED]} do not need any patches.")

    if counter[DataRepairResult.REPAIRED] > 0:
        logger.logger.info(f"\t{counter[DataRepairResult.REPAIRED]} data repaired.")

    if counter[DataRepairResult.REQUIRED_MISSING] > 0:
        logger.logger.info(f"\t{counter[DataRepairResult.REQUIRED_MISSING]} data missing some required fields.")


def _send_mail_async_(col_inst, result_list: list, required_write_holder: BulkWriteDataHolder):
    content = f"<b>{required_write_holder.holded_count} data</b> need manual repairments.<br>" \
              f"Data are originally stored in <code>{col_inst.full_name}</code>.<br>" \
              f"<br>" \
              f"Results list:<br><ul>" \
              f"{''.join(f'<li>{repr(r)}</li>' for r in result_list)}" \
              f"</ul>"

    MailSender.send_email_async(content, subject="Action Needed: Manual Data repairments required")
