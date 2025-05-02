from telegram import OnNewMessage
from core import templates


async def start_private_command(event: OnNewMessage.Event):
    await event._client.send_message(
        event.chat_id,
        templates.texts("welcome"),
        reply_to=event.message.id,
    )
