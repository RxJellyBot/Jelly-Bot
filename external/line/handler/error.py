import traceback

from linebot import exceptions

from extutils.gmail import MailSender
from external.line.logger import LINE, ExtraKey


def handle_error(exception: Exception, event, destination):
    if isinstance(exception, exceptions.LineBotApiError):
        # e.status_code, e.error.message, e.error.details
        message = f"LINE API Error. Status code: {exception.status_code} | Message: {exception.error.message}\n" \
                  f"\tDetails: {exception.error.details}"
    else:
        message = "Error occured on LINE webhook."

    __log_error__(message, event, destination)
    __send_email__(message, event, destination)


def __send_email__(msg, event, destination):
    html = f"<h4>{msg}</h4>\n" \
           f"<hr>\n" \
           f"<pre>Traceback:\n" \
           f"{traceback.format_exc()}</pre>\n" \
           f"<hr>\n" \
           f"Event:\n" \
           f"{event}\n" \
           f"Destination: {destination}"
    MailSender.send_email_async(html, subject="Error on LINE webhook")


def __log_error__(msg, event, destination):
    LINE.logger.error(msg, exc_info=True, extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
