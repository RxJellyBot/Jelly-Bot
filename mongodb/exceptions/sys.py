class MongoURLNotFoundException(Exception):
    def __init__(self):
        super(MongoURLNotFoundException, self).__init__("MONGO_URL not defined in system variables.")
