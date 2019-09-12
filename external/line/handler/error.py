from linebot import exceptions


# FIXME: Handle Error (Send error report to email or provide link to website to view the error?)
def handle_error(exception, event, destination):
    if isinstance(exception, exceptions.LineBotApiError):
        # e.status_code, e.error.message, e.error.details
        pass
