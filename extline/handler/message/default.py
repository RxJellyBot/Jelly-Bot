import logging

from extline import LINE, ExtraKey, event_dest_fmt


# noinspection PyUnusedLocal
def handle_msg_default(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled LINE message event.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
