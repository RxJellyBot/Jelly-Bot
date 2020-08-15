from game.pkchess.character import Character, CharacterTemplate
from game.pkchess.controller import Damage, DamageCalculator
from game.pkchess.exception import (
    DamageFalseNegativeError, DamageFalsePositiveError, DamageTypeInvalidError, DamageValueNegativeError,
    SkillPowerNegativeError
)
from game.pkchess.flags import DamageType
from tests.base import TestCase

__all__ = ["TestDamage", "TestDamageCalculator"]


class TestDamage(TestCase):
    SOURCE = Character(CharacterTemplate(
        "Test Source", 9999, 0, 9999, 0, 5000, 0, 9999, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
    ))
    TARGET = Character(CharacterTemplate(
        "Test Target", 9999, 0, 9999, 0, 9999, 0, 5000, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
    ))

    def test_damage_normal_attack(self):
        dmg = Damage(self.SOURCE, self.TARGET, 1, 5)

        self.assertEqual(dmg.damage_type_code, 1)
        self.assertEqual(dmg.damage_dealt, 5)
        for dmg_type in DamageType:
            self.assertEqual(dmg.is_damage_type(dmg_type), dmg_type == DamageType.DEALT)
        self.assertTrue(dmg.is_dealt)
        self.assertFalse(dmg.is_critical)
        self.assertFalse(dmg.is_skill)
        self.assertFalse(dmg.is_missed)
        self.assertFalse(dmg.is_blocked)

    def test_damage_crit_attack(self):
        dmg = Damage(self.SOURCE, self.TARGET, 3, 5)

        self.assertEqual(dmg.damage_type_code, 3)
        self.assertEqual(dmg.damage_dealt, 5)
        for dmg_type in DamageType:
            with self.subTest(dmg_type=dmg_type):
                self.assertEqual(dmg.is_damage_type(dmg_type),
                                 dmg_type in (DamageType.DEALT, DamageType.CRITICAL))
        self.assertTrue(dmg.is_dealt)
        self.assertTrue(dmg.is_critical)
        self.assertFalse(dmg.is_skill)
        self.assertFalse(dmg.is_missed)
        self.assertFalse(dmg.is_blocked)

    def test_damage_normal_skill(self):
        dmg = Damage(self.SOURCE, self.TARGET, 5, 5)

        self.assertEqual(dmg.damage_type_code, 5)
        self.assertEqual(dmg.damage_dealt, 5)
        for dmg_type in DamageType:
            with self.subTest(dmg_type=dmg_type):
                self.assertEqual(dmg.is_damage_type(dmg_type),
                                 dmg_type in (DamageType.DEALT, DamageType.SKILL))
        self.assertTrue(dmg.is_dealt)
        self.assertFalse(dmg.is_critical)
        self.assertTrue(dmg.is_skill)
        self.assertFalse(dmg.is_missed)
        self.assertFalse(dmg.is_blocked)

    def test_damage_crit_skill(self):
        dmg = Damage(self.SOURCE, self.TARGET, 7, 5)

        self.assertEqual(dmg.damage_type_code, 7)
        self.assertEqual(dmg.damage_dealt, 5)
        for dmg_type in DamageType:
            with self.subTest(dmg_type=dmg_type):
                self.assertEqual(dmg.is_damage_type(dmg_type),
                                 dmg_type in (DamageType.DEALT, DamageType.SKILL, DamageType.CRITICAL))
        self.assertTrue(dmg.is_dealt)
        self.assertTrue(dmg.is_critical)
        self.assertTrue(dmg.is_skill)
        self.assertFalse(dmg.is_missed)
        self.assertFalse(dmg.is_blocked)

    def test_damage_invalid(self):
        data = [
            (DamageFalsePositiveError, (self.SOURCE, self.TARGET, DamageType.MISSED.code, 1)),
            (DamageFalsePositiveError, (self.SOURCE, self.TARGET, DamageType.BLOCKED.code, 1)),
            (DamageValueNegativeError, (self.SOURCE, self.TARGET, 1, -1)),
            (DamageTypeInvalidError, (self.SOURCE, self.TARGET, 0, 0)),
            (DamageTypeInvalidError, (self.SOURCE, self.TARGET, 0, 1)),
            (DamageFalseNegativeError, (self.SOURCE, self.TARGET, 2, 1)),
            (DamageFalseNegativeError, (self.SOURCE, self.TARGET, 4, 1)),
            (DamageFalseNegativeError, (self.SOURCE, self.TARGET, 6, 1))
        ]

        for error, args in data:
            with self.subTest(expected_error=error, args=args):
                with self.assertRaises(error):
                    Damage(*args)

    def test_damage_missed(self):
        dmg = Damage(self.SOURCE, self.TARGET, DamageType.MISSED.code, 0)

        self.assertEqual(dmg.damage_type_code, DamageType.MISSED.code)
        self.assertEqual(dmg.damage_dealt, 0)
        for dmg_type in DamageType:
            self.assertEqual(dmg.is_damage_type(dmg_type), dmg_type == DamageType.MISSED)
        self.assertFalse(dmg.is_dealt)
        self.assertFalse(dmg.is_critical)
        self.assertFalse(dmg.is_skill)
        self.assertTrue(dmg.is_missed)
        self.assertFalse(dmg.is_blocked)

    def test_damage_blocked(self):
        dmg = Damage(self.SOURCE, self.TARGET, DamageType.BLOCKED.code, 0)

        self.assertEqual(dmg.damage_type_code, DamageType.BLOCKED.code)
        self.assertEqual(dmg.damage_dealt, 0)
        for dmg_type in DamageType:
            self.assertEqual(dmg.is_damage_type(dmg_type), dmg_type == DamageType.BLOCKED)
        self.assertFalse(dmg.is_dealt)
        self.assertFalse(dmg.is_critical)
        self.assertFalse(dmg.is_skill)
        self.assertFalse(dmg.is_missed)
        self.assertTrue(dmg.is_blocked)


class TestDamageCalculator(TestCase):
    def setUpTestCase(self) -> None:
        DamageCalculator.RANDOM.seed(87)

    def test_deal_damage(self):
        SRC_ATK = 500
        SRC_CRT = 0.15
        TGT_DEF = 100

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, SRC_ATK, 0, 9999, 0, SRC_CRT, 0, 0.8, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, TGT_DEF, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        dmgs = [DamageCalculator.deal_damage(chara_src, chara_tgt) for _ in range(200)]

        expected_content = [
            ("Damage dealt?", lambda dmg: dmg.is_dealt, 168),
            ("Skill damage?", lambda dmg: dmg.is_skill, 0),
            ("Is critical damage?", lambda dmg: dmg.is_critical, 21),
            ("Any missed?", lambda dmg: dmg.is_missed, 32),
            ("Any blocked?", lambda dmg: dmg.is_blocked, 0),
        ]

        for description, filter_cond, expected_count in expected_content:
            with self.subTest(description=description):
                self.assertEqual(sum(map(filter_cond, dmgs)), expected_count)

        lower_bound = (SRC_ATK - TGT_DEF) * DamageCalculator.DMG_LOWER_BOUNCE
        upper_bound = (SRC_ATK - TGT_DEF) * DamageCalculator.DMG_UPPER_BOUNCE

        for dmg_dealt in filter(lambda dmg: dmg.is_dealt and not dmg.is_critical, dmgs):
            self.assertTrue(lower_bound <= dmg_dealt.damage_dealt <= upper_bound,
                            f"Damage {dmg_dealt.damage_dealt} not in expected bound ({lower_bound}~{upper_bound}).")

        lower_bound *= DamageCalculator.CRT_DMG_RATE
        upper_bound *= DamageCalculator.CRT_DMG_RATE

        for dmg_dealt in filter(lambda dmg: dmg.is_dealt and dmg.is_critical, dmgs):
            self.assertTrue(lower_bound <= dmg_dealt.damage_dealt <= upper_bound,
                            f"Damage {dmg_dealt.damage_dealt} not in expected bound ({lower_bound}~{upper_bound}).")

    def test_deal_skill_damage(self):
        SRC_ATK = 500
        SRC_CRT = 0.15
        TGT_DEF = 100

        SKILL_PWR = 350

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, SRC_ATK, 0, 9999, 0, SRC_CRT, 0, 0.8, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, TGT_DEF, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        dmgs = [DamageCalculator.deal_damage(chara_src, chara_tgt, SKILL_PWR) for _ in range(200)]

        expected_content = [
            ("Damage dealt?", lambda dmg: dmg.is_dealt, 168),
            ("Skill damage?", lambda dmg: dmg.is_skill, 168),
            ("Is critical damage?", lambda dmg: dmg.is_critical, 21),
            ("Any missed?", lambda dmg: dmg.is_missed, 32),
            ("Any blocked?", lambda dmg: dmg.is_blocked, 0),
        ]

        for description, filter_cond, expected_count in expected_content:
            with self.subTest(description=description):
                self.assertEqual(sum(map(filter_cond, dmgs)), expected_count)

        lower_bound = (SRC_ATK - TGT_DEF) * (SKILL_PWR / 100) * DamageCalculator.DMG_LOWER_BOUNCE
        upper_bound = (SRC_ATK - TGT_DEF) * (SKILL_PWR / 100) * DamageCalculator.DMG_UPPER_BOUNCE

        for dmg_dealt in filter(lambda dmg: dmg.is_dealt and not dmg.is_critical, dmgs):
            self.assertTrue(lower_bound <= dmg_dealt.damage_dealt <= upper_bound,
                            f"Damage {dmg_dealt.damage_dealt} not in expected bound ({lower_bound}~{upper_bound}).")

        lower_bound *= DamageCalculator.CRT_DMG_RATE
        upper_bound *= DamageCalculator.CRT_DMG_RATE

        for dmg_dealt in filter(lambda dmg: dmg.is_dealt and dmg.is_critical, dmgs):
            self.assertTrue(lower_bound <= dmg_dealt.damage_dealt <= upper_bound,
                            f"Damage {dmg_dealt.damage_dealt} not in expected bound ({lower_bound}~{upper_bound}).")

    def test_deal_to_death(self):
        SRC_ATK = 500
        SRC_CRT = 0.15
        TGT_DEF = 100

        SKILL_PWR = 350

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, SRC_ATK, 0, 9999, 0, SRC_CRT, 0, 1, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 1, 0, 9999, 0, 9999, 0, TGT_DEF, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        DamageCalculator.deal_damage(chara_src, chara_tgt, SKILL_PWR)

        self.assertEqual(chara_tgt.HP, 0)

    def test_deal_blocked(self):
        SRC_ATK = 100
        SRC_CRT = 0.15
        TGT_DEF = 500

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, SRC_ATK, 0, 9999, 0, SRC_CRT, 0, 0.8, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, TGT_DEF, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        dmgs = [DamageCalculator.deal_damage(chara_src, chara_tgt) for _ in range(200)]

        expected_content = [
            ("Damage dealt?", lambda dmg: dmg.is_dealt, 0),
            ("Skill damage?", lambda dmg: dmg.is_skill, 0),
            ("Is critical damage?", lambda dmg: dmg.is_critical, 0),
            ("Any missed?", lambda dmg: dmg.is_missed, 0),
            ("Any blocked?", lambda dmg: dmg.is_blocked, 200),
        ]

        for description, filter_cond, expected_count in expected_content:
            with self.subTest(description=description):
                self.assertEqual(sum(map(filter_cond, dmgs)), expected_count)

    def test_deal_blocked_skill(self):
        SRC_ATK = 100
        SRC_CRT = 0.15
        TGT_DEF = 500

        SKILL_PWR = 350

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, SRC_ATK, 0, 9999, 0, SRC_CRT, 0, 0.8, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, TGT_DEF, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        dmgs = [DamageCalculator.deal_damage(chara_src, chara_tgt, SKILL_PWR) for _ in range(200)]

        expected_content = [
            ("Damage dealt?", lambda dmg: dmg.is_dealt, 0),
            ("Skill damage?", lambda dmg: dmg.is_skill, 0),
            ("Is critical damage?", lambda dmg: dmg.is_critical, 0),
            ("Any missed?", lambda dmg: dmg.is_missed, 0),
            ("Any blocked?", lambda dmg: dmg.is_blocked, 200),
        ]

        for description, filter_cond, expected_count in expected_content:
            with self.subTest(description=description):
                self.assertEqual(sum(map(filter_cond, dmgs)), expected_count)

    def test_negative_skill_power(self):
        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, 9999, 0, 9999, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, 5, 0, 9999, 0, 1, 0, 0, 0, 1, 0, []
        ))

        with self.assertRaises(SkillPowerNegativeError):
            DamageCalculator.deal_damage(chara_src, chara_tgt, -5)

    def test_random_hit(self):
        self.assertEqual([DamageCalculator.random_hit(0.87) for _ in range(200)].count(True), 176)
        self.assertEqual([DamageCalculator.random_hit(0.5) for _ in range(200)].count(True), 97)

    def test_hit_rate_acc_gt_evd(self):
        SRC_ACC = 1.5
        TGT_EVD = 0.7

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, 9999, 0, 9999, 0, 9999, 0, SRC_ACC, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, 5, 0, 9999, 0, 0, 0, TGT_EVD, 0, 1, 0, []
        ))

        self.assertEqual(DamageCalculator.hit_rate(chara_src, chara_tgt), 0.8)
        self.assertEqual(
            [DamageCalculator.deal_damage(chara_src, chara_tgt).is_dealt for _ in range(200)].count(True),
            168
        )

    def test_hit_rate_diff_gt_1(self):
        SRC_ACC = 1.5
        TGT_EVD = 0.5

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, 9999, 0, 9999, 0, 9999, 0, SRC_ACC, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, 5, 0, 9999, 0, 0, 0, TGT_EVD, 0, 1, 0, []
        ))

        self.assertEqual(DamageCalculator.hit_rate(chara_src, chara_tgt), 1)
        self.assertEqual(
            [DamageCalculator.deal_damage(chara_src, chara_tgt).is_dealt for _ in range(200)].count(True),
            200
        )

    def test_hit_rate_diff_neg(self):
        SRC_ACC = 1.4
        TGT_EVD = 1.5

        chara_src = Character(CharacterTemplate(
            "Test Source", 9999, 0, 9999, 0, 9999, 0, 9999, 0, 9999, 0, SRC_ACC, 0, 0, 0, 1, 0, []
        ))
        chara_tgt = Character(CharacterTemplate(
            "Test Target", 9999, 0, 9999, 0, 9999, 0, 5, 0, 9999, 0, 0, 0, TGT_EVD, 0, 1, 0, []
        ))

        self.assertEqual(DamageCalculator.hit_rate(chara_src, chara_tgt), 0)
        self.assertEqual(
            [DamageCalculator.deal_damage(chara_src, chara_tgt).is_dealt for _ in range(200)].count(True),
            0
        )
