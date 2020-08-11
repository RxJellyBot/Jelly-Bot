from game.pkchess.character import Character
from game.pkchess.utils.character import get_character_template
from tests.base import TestCase

__all__ = ["TestCharacter"]


class TestCharacter(TestCase):
    def test_character_from_template(self):
        template = get_character_template("Nearnox")

        chara = Character(template)

        self.assertEqual(chara.template, template)
        self.assertEqual(chara.name, template.name)
        self.assertEqual(chara.HP, template.HP)
        self.assertEqual(chara.MP, template.MP)
        self.assertEqual(chara.ATK, template.ATK)
        self.assertEqual(chara.DEF, template.DEF)
        self.assertEqual(chara.CRT, template.CRT)
        self.assertEqual(chara.ACC, template.ACC)
        self.assertEqual(chara.EVD, template.EVD)
        self.assertEqual(chara.MOV, template.MOV)
        self.assertEqual(chara.skill_ids, template.skill_ids)
        self.assertEqual(chara.EXP, 0)
