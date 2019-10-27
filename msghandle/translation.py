current_lang = None


def update_current_lang(domain, lang_code):
    global current_lang
    import gettext
    try:
        lang = gettext.translation(domain, localedir='locale/', languages=[lang_code])
        lang.install()
    except FileNotFoundError:
        lang = None

    current_lang = lang


def deactivate_lang():
    global current_lang
    current_lang = None


def gettext(message):
    if current_lang:
        return current_lang.gettext(message)
    else:
        import gettext
        return gettext.gettext(message)
