from .bot import *  # NOQA
from .extutils import *  # NOQA
from .models import *  # NOQA

# region Dropping all test databases
from mongodb.factory import MONGO_CLIENT, is_test_db

for db_name in MONGO_CLIENT.list_database_names():
    if is_test_db(db_name):
        MONGO_CLIENT.drop_database(db_name)
        print(f"Dropped test database <{db_name}>.")
