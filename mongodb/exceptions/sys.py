class MongoURLNotFoundError(Exception):
    def __init__(self):
        super(MongoURLNotFoundError, self).__init__("MONGO_URL not defined in system variables.")
