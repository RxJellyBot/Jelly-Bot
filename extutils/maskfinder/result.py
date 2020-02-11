from dataclasses import dataclass


@dataclass
class Result:
    name: str
    product_name: str
    amount: int
    distance: float
    address: str
    time: str = None

    @property
    def name_str(self) -> str:
        if self.time:
            return f"{self.name} ({self.time})"
        else:
            return self.name

    def __str__(self):
        s = f"{self.product_name}\n"
        s += f"<{self.amount:^7d}> {self.name} (Time: {self.time})\n"
        s += f"{self.distance} mi - {self.address}"
        return s
