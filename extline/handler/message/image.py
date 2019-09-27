import logging

from extline import LINE, ExtraKey, event_dest_fmt


def handle_image(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Image event.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
