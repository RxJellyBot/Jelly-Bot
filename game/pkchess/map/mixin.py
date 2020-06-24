from abc import abstractmethod, ABC

__all__ = ["ConvertibleMapMixin"]


class ConvertibleMapMixin(ABC):
    @abstractmethod
    def to_map(self):
        raise NotImplementedError()
