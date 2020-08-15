from game.pkchess.exception import UnhandledSkillDirectionError
from game.pkchess.flags import SkillDirection
from tests.base import TestCase

__all__ = ["TestSkillDirectionRotate"]


class TestSkillDirectionRotate(TestCase):
    """
    Directional sample offset::

        ---------
        ---------
        ---XXX---
        ---XXX---
        ----=----
        -XXX-X---
        -----X---
        -----X---
        ---------

    Undirectional sample offset::

        ---------
        ---------
        ----X----
        ----X----
        --XX=XX--
        ----X----
        ----X----
        ---------
        ---------
    """

    OFFSETS_DIRECTIONAL = {
        (-1, 1), (0, 1), (1, 1), (-1, 2), (0, 2), (1, 2),
        (-1, -1), (-2, -1), (-3, -1),
        (1, -1), (1, -2), (1, -3)
    }

    OFFSETS_UNDIRECTIONAL = {
        (0, 1), (0, 2),
        (1, 0), (2, 0),
        (0, -1), (0, -2),
        (-1, 0), (-2, 0)
    }

    def test_rotate_left(self):
        self.assertEqual(
            SkillDirection.LEFT.rotate_offsets(self.OFFSETS_DIRECTIONAL),
            {
                (-1, -1), (-1, 0), (-1, 1), (-2, -1), (-2, 0), (-2, 1),
                (1, -1), (1, -2), (1, -3),
                (1, 1), (2, 1), (3, 1)
            }
        )

    def test_rotate_right(self):
        self.assertEqual(
            SkillDirection.RIGHT.rotate_offsets(self.OFFSETS_DIRECTIONAL),
            {
                (1, -1), (1, 0), (1, 1), (2, -1), (2, 0), (2, 1),
                (-1, -1), (-2, -1), (-3, -1),
                (-1, 1), (-1, 2), (-1, 3)
            }
        )

    def test_rotate_up(self):
        self.assertEqual(
            SkillDirection.UP.rotate_offsets(self.OFFSETS_DIRECTIONAL),
            self.OFFSETS_DIRECTIONAL
        )

    def test_rotate_down(self):
        self.assertEqual(
            SkillDirection.DOWN.rotate_offsets(self.OFFSETS_DIRECTIONAL),
            {
                (-1, -1), (0, -1), (1, -1), (-1, -2), (0, -2), (1, -2),
                (-1, 1), (-1, 2), (-1, 3),
                (1, 1), (2, 1), (3, 1)
            }
        )

    def test_rotate_left_non_directional(self):
        self.assertEqual(SkillDirection.LEFT.rotate_offsets(self.OFFSETS_UNDIRECTIONAL), self.OFFSETS_UNDIRECTIONAL)

    def test_rotate_right_non_directional(self):
        self.assertEqual(SkillDirection.RIGHT.rotate_offsets(self.OFFSETS_UNDIRECTIONAL), self.OFFSETS_UNDIRECTIONAL)

    def test_rotate_up_non_directional(self):
        self.assertEqual(SkillDirection.UP.rotate_offsets(self.OFFSETS_UNDIRECTIONAL), self.OFFSETS_UNDIRECTIONAL)

    def test_rotate_down_non_directional(self):
        self.assertEqual(SkillDirection.DOWN.rotate_offsets(self.OFFSETS_UNDIRECTIONAL), self.OFFSETS_UNDIRECTIONAL)

    def test_rotate_unhandled(self):
        with self.assertRaises(UnhandledSkillDirectionError):
            SkillDirection.TEST.rotate_offsets(self.OFFSETS_DIRECTIONAL)
