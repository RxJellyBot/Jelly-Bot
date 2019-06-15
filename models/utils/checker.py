from typing import Optional

from pymongo.collection import Collection

from JellyBotAPI.SystemConfig import Database
from mongodb.utils import BulkWriteDataHolder
from models import ModelDefaultValueExtension, OID_KEY
from extutils.flags import FlagCodeEnum

from ..rpdata import PendingRepairDataModel


class DataRepairResult(FlagCodeEnum):
    @staticmethod
    def default():
        raise ValueError("No default value for `DataRepairResult`.")

    REQUIRED_MISSING = 0
    NO_PATCH_NEEDED = 1
    REPAIRED = 2


class ModelFieldChecker:
    @staticmethod
    def check(col_inst):
        from mongodb.factory import PendingRepairDataManager
        print(f"Scanning `{col_inst.full_name}`...")

        or_list = []

        for key, val in col_inst.data_model.default_vals:
            if val != ModelDefaultValueExtension.Optional:
                or_list.append({key: {"$exists": False}})

        if len(or_list) > 0:
            potential_repair_needed = col_inst.find({"$or": or_list})
            required_write_holder = PendingRepairDataManager.new_bulk_holder(col_inst.full_name)
            repaired_write_holder = BulkWriteDataHolder(col_inst, Database.BulkWriteCount)

            if potential_repair_needed.count() > 0:
                print("\tScanning potential repair requiring data...")

            repaired = ModelFieldChecker.scan_data(
                col_inst, potential_repair_needed, required_write_holder, repaired_write_holder)

            if len(repaired) > 0:
                print("\tUpdating repaired data...")
                repaired_write_holder.complete()

            if required_write_holder.holding_data:
                print("\tUpdating unrepaired data...")
                required_write_holder.complete()

        print(f"Done scanning `{col_inst.full_name}`.")

    @staticmethod
    def scan_data(col_inst, potential_repair_needed, required_write_holder, repaired_write_holder):
        repaired = []
        counter = {k: 0 for k in DataRepairResult}

        for data in potential_repair_needed:
            result, rpdata = ModelFieldChecker.repair_single_data(
                col_inst, required_write_holder, data, col_inst.data_model.get_default_dict())

            counter[result] += 1

            if rpdata:
                repaired_write_holder.replace_single(rpdata)

        ModelFieldChecker.print_scanning_result(counter)

        return repaired

    @staticmethod
    def repair_single_data(col_inst: Collection, required_write_holder, data, default_dict) -> (DataRepairResult, Optional[dict]):
        changed = False
        missing = {}

        for name, key in col_inst.data_model.model_keys().items():
            if key not in data:
                try:
                    default_val = default_dict[key]
                    if default_val == ModelDefaultValueExtension.Required:
                        missing[key] = name
                    elif default_val == ModelDefaultValueExtension.Optional:
                        pass  # Optional so no change
                    else:
                        data[key] = default_val
                        changed = True if not changed else changed
                except KeyError:
                    raise ValueError(f"Default value rule not set for `{name}` in `{col_inst.data_model.__name__}`.")

        if len(missing) > 0:
            required_write_holder.repsert_single(
                {f"{PendingRepairDataModel.Data}.{OID_KEY}": data[OID_KEY]},
                PendingRepairDataModel(data=data, missing_keys=missing, incl_oid=False).serialize())

            col_inst.delete_one({OID_KEY: data[OID_KEY]})
            # FIXME: remove from db, email notify
            return DataRepairResult.REQUIRED_MISSING, None
        else:
            return DataRepairResult.REPAIRED if changed else DataRepairResult.NO_PATCH_NEEDED, data if changed else None

    @staticmethod
    def print_scanning_result(counter):
        if counter[DataRepairResult.NO_PATCH_NEEDED] > 0:
            print(f"\t{counter[DataRepairResult.NO_PATCH_NEEDED]} do not need any patches.")

        if counter[DataRepairResult.REPAIRED] > 0:
            print(f"\t{counter[DataRepairResult.REPAIRED]} data repaired.")

        if counter[DataRepairResult.REQUIRED_MISSING] > 0:
            print(f"\t{counter[DataRepairResult.REQUIRED_MISSING]} data missing some required fields.")
