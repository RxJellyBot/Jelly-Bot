from typing import Optional

from game.pkchess.character import CharacterTemplate
from game.pkchess.res import character_templates

__all__ = ["is_character_exists", "get_character_name", "get_character_template"]


def is_character_exists(name: str) -> bool:
    """
    Check if the character exists using the given name.

    This match is case-insensitive.

    :param name: name of the character to be checked
    :return: if the character exists
    """
    return name.lower() in character_templates


def get_character_name(name: str) -> Optional[str]:
    chara = get_character_template(name)
    if chara:
        return chara.name

    return None


def get_character_template(name: str) -> Optional[CharacterTemplate]:
    return character_templates.get(name.lower())
