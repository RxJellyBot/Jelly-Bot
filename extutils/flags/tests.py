"""
Comparison:
    Status code comparison: < = >...
    Same code different parent: False

Repr (toString):
    <PARENT_CLASS.ENUM_NAME: CODE (SHORT_NAME) - DESCRIPTION>

InstanceCheck:
    isInstance(Enum.A, Enum): True

Typecast:
    Cast back from int
"""
from .main import FlagSingleEnum


class SpecEnum(FlagSingleEnum):
    A = (1, "K")
    B = (2, "V")

    @staticmethod
    def default():
        return SpecEnum.A


class SpecEnum2(FlagSingleEnum):
    @staticmethod
    def default():
        return SpecEnum2.C

    C = (2, "K")
    D = (3, "V")


if __name__ == '__main__':
    assert SpecEnum.B != SpecEnum2.C
    assert SpecEnum.A == 1
    assert SpecEnum.B < 3
    assert isinstance(SpecEnum.A, SpecEnum)
    assert SpecEnum.default() == SpecEnum.A
