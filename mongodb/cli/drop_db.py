import os
import sys

import pymongo

mongo_url = os.environ.get("MONGO_URL")
if not mongo_url:
    print("`MONGO_URL` not specified. MongoDB client cannot be initialized.")
    sys.exit(1)

mongo_client = pymongo.MongoClient(mongo_url)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: drop_db.py <DATABASE_NAME>")
        sys.exit(1)

    db_name_to_drop = sys.argv[1]
    mongo_client.drop_database(db_name_to_drop)
    print(f"Database <{db_name_to_drop}> dropped.")
