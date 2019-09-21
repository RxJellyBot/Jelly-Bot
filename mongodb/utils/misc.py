from pymongo.collation import Collation

case_insensitive_collation = Collation(locale='en', strength=1)
