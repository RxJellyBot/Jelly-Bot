import warnings
from functools import lru_cache

from tinydb import Query as tinyDbQuery, where


class QueryElement:
    def __init__(self, key: str):
        self.key = key

    def __hash__(self):
        return id(self.key)

    def __eq__(self, other):
        return self.key == other.key


class QueryElementOperator:
    def __init__(self, value):
        self.value = value

    def to_tinydb(self, lhs):
        raise NotImplementedError()

    def to_mongodb(self):
        raise NotImplementedError()


class MatchPair(QueryElement):
    def __init__(self, key: str, value):
        super().__init__(key)
        self.value = value


class NotEqual(QueryElementOperator):
    def __init__(self, value):
        super().__init__(value)

    def to_tinydb(self, lhs):
        return lhs != self.value

    def to_mongodb(self):
        return {"$ne": self.value}


class StringContains(QueryElementOperator):
    def __init__(self, value):
        super().__init__(value)

    def to_tinydb(self, lhs):
        return lhs.search(self.value)

    def to_mongodb(self):
        return {"$regex": self.value, "$options": "i"}


class Query:
    def __init__(self, *elements: QueryElement):
        self._elements = set(elements)

    def add_element(self, query_elem: QueryElement, overwrite=True):
        if overwrite:
            try:
                self._elements.remove(query_elem)
            except KeyError:
                pass
        self._elements.add(query_elem)
        self.to_mongo.cache_clear()
        self.to_tinydb.cache_clear()

    @lru_cache()
    def to_mongo(self):
        d = {}

        for elem in self._elements:
            if isinstance(elem, MatchPair):
                if isinstance(elem.value, QueryElementOperator):
                    d[elem.key] = elem.value.to_mongodb()
                else:
                    d[elem.key] = elem.value
            else:
                warnings.warn(f"Unrecognized `QueryElement` detected. ({type(elem)})")

        return d

    @lru_cache()
    def to_tinydb(self):
        q = tinyDbQuery()

        for elem in self._elements:
            if isinstance(elem, MatchPair):
                if isinstance(elem.value, QueryElementOperator):
                    q &= elem.value.to_tinydb(where(elem.key))
                else:
                    q &= (where(elem.key) == elem.value)
            else:
                warnings.warn(f"Unrecognized `QueryElement` detected. ({type(elem)})")

        return q
