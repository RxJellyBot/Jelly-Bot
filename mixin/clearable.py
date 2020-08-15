from abc import abstractmethod, ABC

__all__ = ("ClearableMixin",)


class ClearableMixin(ABC):
    @abstractmethod
    def clear(self):
        """Method to clear all the data of the collection and its related collection(s)."""
        raise NotImplementedError()
