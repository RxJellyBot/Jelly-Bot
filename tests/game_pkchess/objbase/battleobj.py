from dataclasses import dataclass

from game.pkchess.objbase import BattleObject
from tests.base import TestCase

__all__ = ["TestBattleObject"]


@dataclass
class MockedBattleObject(BattleObject):
    def __post_init__(self):
        self.name = "ABC"

        self.HP = 999
        self.MP = 999

        self.ATK = 0
        self.DEF = 0
        self.CRT = 0

        self.ACC = 0
        self.EVD = 0

        self.MOV = 0


class TestBattleObject(TestCase):
    def test_decrease_hp(self):
        obj = MockedBattleObject()

        self.assertEqual(obj.HP, 999)
        self.assertTrue(obj.is_alive)

        obj.decrease_hp(500)

        self.assertEqual(obj.HP, 499)
        self.assertTrue(obj.is_alive)

    def test_decrease_hp_dead(self):
        obj = MockedBattleObject()

        self.assertEqual(obj.HP, 999)
        self.assertTrue(obj.is_alive)

        obj.decrease_hp(999)

        self.assertEqual(obj.HP, 0)
        self.assertFalse(obj.is_alive)

    def test_decrease_hp_ceil_dmg(self):
        obj = MockedBattleObject()

        self.assertEqual(obj.HP, 999)
        self.assertTrue(obj.is_alive)

        obj.decrease_hp(499.0000001)

        self.assertEqual(obj.HP, 499)
        self.assertTrue(obj.is_alive)

        obj.decrease_hp(498.0000001)

        self.assertEqual(obj.HP, 0)
        self.assertFalse(obj.is_alive)

    def test_is_alive(self):
        obj = MockedBattleObject()

        self.assertTrue(obj.is_alive)

    def test_is_alive_dead(self):
        obj = MockedBattleObject()
        obj.HP = 0

        self.assertFalse(obj.is_alive)
