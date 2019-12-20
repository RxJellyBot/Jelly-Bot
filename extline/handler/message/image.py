from flags import Platform
from msghandle import handle_message_main
from msghandle.models import MessageEventObjectFactory


# noinspection PyUnusedLocal
def handle_image(request, event, destination):
    e = MessageEventObjectFactory.from_line(event)

    handle_message_main(e).to_platform(Platform.LINE).send_line(event.reply_token)
