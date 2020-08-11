"""
This module contains the function to handle the default/unhandled message type event.
"""
from extline.logger import LINE


def handle_msg_unhandled(_, event, destination):
    """Method to be called upon receiving an unhandled message type event."""
    LINE.log_event("Unhandled LINE message event.", event=event, dest=destination)
