from abc import abstractmethod, ABC


class ClearableCollectionMixin(ABC):
    @abstractmethod
    def clear(self):
        """Method to clear all the data of the collection and its related collection(s)."""
        raise NotImplementedError()
