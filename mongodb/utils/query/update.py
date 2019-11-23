import warnings
from functools import lru_cache


class UpdateElement:
    def __init__(self, value: str):
        self.value = value

    def __hash__(self):
        return id(self.value)

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class Set(UpdateElement):
    def __init__(self, set_dict):
        super().__init__(set_dict)


class Increment(UpdateElement):
    def __init__(self, increase_keys):
        super().__init__(increase_keys)


class UpdateOperation:
    def __init__(self, *elements: UpdateElement):
        self._elements = set(elements)

    @lru_cache()
    def tinydb_ops(self):
        def transform(doc):
            for elem in self._elements:
                if isinstance(elem, Set):
                    doc.update(elem.value)
                elif isinstance(elem, Increment):
                    for k in elem.value:
                        doc[k] += 1
                else:
                    warnings.warn(f"Unrecognized `UpdateElement` detected. ({type(elem)})")

        return transform

    @lru_cache()
    def mongo_ops(self):
        d = {}

        for elem in self._elements:
            if isinstance(elem, Set):
                d["$set"] = elem.value
            elif isinstance(elem, Increment):
                d["$inc"] = {k: 1 for k in elem.value}
            else:
                warnings.warn(f"Unrecognized `UpdateElement` detected. ({type(elem)})")

        return d
