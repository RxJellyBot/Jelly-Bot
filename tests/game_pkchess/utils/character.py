from game.pkchess.utils.character import is_character_exists, get_character, get_character_name
from game.pkchess.res import characters

from tests.base import TestCase

__all__ = ["TestCharacterUtils"]


class TestCharacterUtils(TestCase):
    def test_character_existence_exists(self):
        self.assertTrue(is_character_exists("Nearnox"))

    def test_character_existence_not_exists(self):
        self.assertFalse(is_character_exists("ABCDEF"))

    def test_character_existence_empty_string(self):
        self.assertFalse(is_character_exists(""))

    def test_character_name_correct_case(self):
        self.assertEqual(get_character_name("Nearnox"), "Nearnox")

    def test_character_name_weird_case(self):
        self.assertEqual(get_character_name("NeArNoX"), "Nearnox")

    def test_character_name_not_found(self):
        self.assertEqual(get_character_name("NeArNoX"), "Nearnox")

    def test_character_correct_case(self):
        self.assertEqual(get_character("Nearnox"), characters["nearnox"])

    def test_character_weird_case(self):
        self.assertEqual(get_character("NearNox"), characters["nearnox"])

    def test_character_not_found(self):
        self.assertIsNone(get_character("ABCDEF"))

    def test_character_empty_string(self):
        self.assertIsNone(get_character(""))
