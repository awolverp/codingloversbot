from telegram import OnNewMessage, types
from core import templates


async def _private_start_command(event: OnNewMessage.Event):
    user: types.User = await event._client.get_entity(event.message.sender_id)

    await event._client.send_message(
        event.chat_id,
        templates.texts("welcome", name=user.first_name),
        reply_to=event.message.id,
        buttons=[
            [
                types.KeyboardButtonUrl(
                    templates.buttons("start", "source"),
                    "https://github.com/awolverp/codingloversbot",
                )
            ],
            [types.KeyboardButtonCallback(templates.buttons("start", "help"), "help")],
        ],
    )


async def _public_start_command(event: OnNewMessage.Event):
    pass


async def start_command(event: OnNewMessage.Event):
    if event.message.is_private:
        await _private_start_command(event)
    else:
        await _public_start_command(event)
