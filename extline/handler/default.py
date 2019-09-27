import logging

from extline import LINE, ExtraKey, event_dest_fmt


def handle_default(event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled event.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
