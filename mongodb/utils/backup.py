import os
import time
from datetime import datetime
from threading import Thread

import pymongo
from pymongo import errors

from extutils.logger import LoggerSkeleton

__all__ = ["backup_collection"]

logger = LoggerSkeleton("mongo.backup", logger_name_env="MONGO_BACKUP")

target_mongo_url = os.environ.get("MONGO_BACKUP_URL")
if not target_mongo_url:
    logger.logger.error("MongoDB Backup service not activated.")
    logger.logger.error("Specify `MONGO_BACKUP_URL` in the environment variables "
                        "with the connection string of the target instance.")

target_client = None
if target_mongo_url:
    target_client = pymongo.MongoClient(target_mongo_url)


def backup_collection(
        org_client: pymongo.MongoClient, db_name: str, col_name: str, is_single_db: bool, backup_interval: int):
    if not target_client:
        logger.logger.warning("Attempted to backup the data while the backup service is not activated.")
        logger.logger.warning(f"DB Name: {db_name} / Collection Name: {col_name} / Is single DB: {is_single_db}.")
        return

    Thread(target=backup_collection_thread,
           args=(org_client, db_name, col_name, is_single_db, backup_interval)).start()


def backup_collection_thread(
        org_client: pymongo.MongoClient, db_name: str, col_name: str, is_single_db: bool, backup_interval: int):
    while True:
        if is_single_db:
            target_db_name, target_col_name = col_name.split(".", 1)
        else:
            target_db_name, target_col_name = db_name, col_name

        origin_col = org_client.get_database(db_name).get_collection(col_name)
        target_col = target_client.get_database(target_db_name).get_collection(target_col_name)
        target_col_backup = target_client.get_database(target_db_name).get_collection("_backup_")
        target_col.drop()

        logger.logger.info(f"Backup of `{db_name}.{col_name}` in progress...")
        try:
            target_col.insert_many(origin_col.find())
            target_col_backup.update_one({"col": col_name},
                                         {"$set": {"ts": datetime.utcnow()}}, upsert=True)
        except pymongo.errors.InvalidOperation as e:
            logger.logger.info(f"Backup of `{db_name}.{col_name}` yielded `InvalidOperation`. ({e})")
        except pymongo.errors.BulkWriteError as e:
            logger.logger.error(f"Backup of `{db_name}.{col_name}` yielded `BulkWriteError`. ({e.details})")
        except Exception as e:
            logger.logger.error(f"Backup of `{db_name}.{col_name}` failed. Error: {e} ({type(e)})")

        logger.logger.info(f"Backup of `{db_name}.{col_name}` completed on {datetime.now()}.`")

        time.sleep(backup_interval)
