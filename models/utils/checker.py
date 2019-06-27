from typing import Optional

from pymongo.collection import Collection

from JellyBotAPI.SystemConfig import Database
from mongodb.utils import BulkWriteDataHolder
from models import ModelDefaultValueExt, OID_KEY
from models.field import ModelField
from extutils.flags import FlagCodeEnum
from extutils.gmail import MailSender

from ..rpdata import PendingRepairDataModel


class DataRepairResult(FlagCodeEnum):
    @classmethod
    def default(cls):
        raise ValueError("No default value for `DataRepairResult`.")

    REQUIRED_MISSING = 0
    NO_PATCH_NEEDED = 1
    REPAIRED = 2


class ModelFieldChecker:
    @staticmethod
    def check(col_inst):
        from mongodb.factory import PendingRepairDataManager
        print(f"Scanning `{col_inst.full_name}`...")

        or_list = _build_find_or_list_(col_inst.data_model)

        if len(or_list) > 0:
            potential_repair_needed = col_inst.find({"$or": or_list})

            if potential_repair_needed.count() > 0:
                required_write_holder = PendingRepairDataManager.new_bulk_holder(col_inst.full_name)
                repaired_write_holder = BulkWriteDataHolder(col_inst, Database.BulkWriteCount)

                print("\tScanning potential repair requiring data...")

                _scan_data_(col_inst, potential_repair_needed, required_write_holder, repaired_write_holder)

                if repaired_write_holder.holding_data:
                    print("\tUpdating repaired data to database...")
                    repaired_write_holder.complete()

                if required_write_holder.holding_data:
                    print("\tUpdating manual repairments required database/Sending email notification...")

                    result = required_write_holder.complete()
                    _send_mail_async_(col_inst, result, required_write_holder)

        print(f"Done scanning `{col_inst.full_name}`.")


# noinspection PyUnusedLocal
def _get_dict_models_(model_cls):
    """
    :return: [(Json Key, Default Value), (Json Key, Default Value), ...]
    """
    return [(getattr(model_cls, k).key, getattr(model_cls, k).model_cls) for k in model_cls.model_fields()
            if isinstance(getattr(model_cls, k), ModelField)]


# noinspection PyUnusedLocal
def _get_default_vals_(model_cls):
    """
    :return: [(Json Key, Default Value), (Json Key, Default Value), ...]
    """
    return [(getattr(model_cls, k).key, getattr(model_cls, k).default_value) for k in model_cls.model_fields()]


def _build_find_or_list_(model_cls):
    or_list = _bulid_filter_(model_cls)

    for key, model_cls in _get_dict_models_(model_cls):
        or_list.extend(_bulid_filter_(model_cls, key))

    return or_list


def _bulid_filter_(model_cls, prefix=None):
    if prefix is not None:
        prefix = prefix + "."
    else:
        prefix = ""

    or_list = []

    for key, val in _get_default_vals_(model_cls):
        if val != ModelDefaultValueExt.Optional:
            or_list.append({f"{prefix}{key}": {"$exists": False}})

    return or_list


def _scan_data_(col_inst, potential_repair_needed, required_write_holder, repaired_write_holder):
    counter = {k: 0 for k in DataRepairResult}

    for data in potential_repair_needed:
        result, rpdata = _repair_single_data_(col_inst, required_write_holder, data)

        counter[result] += 1

        if rpdata:
            repaired_write_holder.replace_single(rpdata)

    _print_scanning_result_(counter)


def _repair_single_data_(col_inst: Collection, required_write_holder, data) -> (
        DataRepairResult, Optional[dict]):
    changed = [False]
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


def _repair_fields_(model_cls, data, changed, missing):
    for json_key, default_val in _get_default_vals_(model_cls):
        if json_key not in data:
            try:
                if default_val == ModelDefaultValueExt.Required:
                    missing.append(json_key)
                elif default_val == ModelDefaultValueExt.Optional:
                    pass  # Optional so no change
                else:
                    data[json_key] = default_val
                    changed[0] = True if not changed[0] else changed[0]
            except KeyError:
                raise ValueError(f"Default value rule not set for json key `{json_key}` in `{model_cls.__name__}`.")


def _print_scanning_result_(counter):
    if counter[DataRepairResult.NO_PATCH_NEEDED] > 0:
        print(f"\t{counter[DataRepairResult.NO_PATCH_NEEDED]} do not need any patches.")

    if counter[DataRepairResult.REPAIRED] > 0:
        print(f"\t{counter[DataRepairResult.REPAIRED]} data repaired.")

    if counter[DataRepairResult.REQUIRED_MISSING] > 0:
        print(f"\t{counter[DataRepairResult.REQUIRED_MISSING]} data missing some required fields.")


def _send_mail_async_(col_inst, result_list, required_write_holder):
    content = f"<b>{required_write_holder.holded_count} data</b> need manual repairments.<br>"\
        f"Data are originally stored in <code>{col_inst.full_name}</code>.<br>"\
        f"<br>"\
        f"Results list:<br><ul>"\
        f"{''.join(f'<li>{repr(r)}</li>' for r in result_list)}"\
        f"</ul>"

    MailSender.send_email_async(content, subject="Action Needed: Manual Data repairments required")
