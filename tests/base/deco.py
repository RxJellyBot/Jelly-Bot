from django.test import override_settings

__all__ = ("locale_en", "locale_cht")

locale_en = override_settings(LANGUAGE_CODE="en-us", LANGUAGES=(("en", "English"),), )
locale_cht = override_settings(LANGUAGE_CODE="zh-tw", LANGUAGES=(("zh-tw", "Traditional Chinese"),), )
