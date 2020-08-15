"""This module contains the function to handle the default/unhandled type event."""
from extline.logger import LINE


def handle_default(event, destination):
    """Method to be called upon receiving an unhandled type event."""
    LINE.log_event("Unhandled event.", event=event, dest=destination)
