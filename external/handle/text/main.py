from ..base_in import TextEventObject


def handle_text_event(e: TextEventObject):
    # FIXME: [HP] handle text and return, it's simple echo for now
    if e.text == "ERRORERROR":
        raise Exception("Custom error for testing purpose.")
    else:
        return e.text

    pass
