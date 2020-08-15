"""
Result implementations of the service US mask finder.
"""
from dataclasses import dataclass


@dataclass
class MaskFindingResult:
    """
    Mask finding result body class.
    """
    name: str
    product_name: str
    amount: int
    distance: float
    address: str
    time: str = None

    @property
    def name_str(self) -> str:
        """
        Get the name of the product.

        :return: name of the product.
        """
        if self.time:
            return f"{self.name} ({self.time})"

        return self.name
