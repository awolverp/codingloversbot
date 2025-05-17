from telegram import OnNewMessage, types
from core import templates, env, utils
import cachebox
import asyncio
import models


_last_reconfigure = cachebox.TTLCache[int, object](100, 15)


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
    if event.message.chat_id not in env.GROUPS:
        await event._client.send_message(
            event.message.chat_id,
            templates.texts("group_is_not_allowed"),
            reply_to=event.message.id,
        )
        await event._client.delete_dialog(event.message.chat_id)
        return

    if event.message.chat_id in _last_reconfigure:
        await event._client.send_message(
            event.message.chat_id, templates.texts("reconfigure_2"), reply_to=event.message.id
        )
        return

    # We have to reconfigure the group
    to_edit = await event._client.send_message(
        event.message.chat_id, templates.texts("loading"), reply_to=event.message.id
    )

    await asyncio.sleep(0.2)

    admin_ids = []
    async for admin in event._client.iter_participants(
        event.message.chat_id, filter=types.ChannelParticipantsAdmins()
    ):
        admin: types.User

        if admin.bot:
            continue

        admin_ids.append(admin.id)

    async with models.db.begin() as session:
        group_is_exists = await session.scalar(models.sql.select(models.Group.id))

        if group_is_exists is None:
            chat_info = await event._client.get_entity(event.message.chat_id)

            await session.execute(
                models.sql.insert(models.Group).values(
                    id=event.message.chat_id,
                    name=chat_info.first_name
                    if hasattr(chat_info, "first_name")
                    else chat_info.title,
                    warn_action=models.GroupWarnAction.BAN,
                )
            )

        await session.execute(
            models.sql.delete(models.Admin).where(models.Admin.group_id == event.message.chat_id)
        )

        for i in admin_ids:
            await session.execute(
                models.sql.insert(models.Admin).values(user_id=i, group_id=event.message.chat_id)
            )

        await session.execute(
            models.sql.delete(models.Participant).where(
                models.Participant.group_id == event.message.chat_id,
                models.Participant.user_id.in_(admin_ids),
                models.Participant.is_trusted == True,
            )
        )

        trust_count = await session.scalar(
            models.sql.select(models.sql.func.count(models.Participant.id)).where(
                models.Participant.group_id == event.message.chat_id,
                models.Participant.is_trusted == True,
            )
        )

    _last_reconfigure[event.message.chat_id] = object()

    await event._client.edit_message(
        to_edit,
        templates.texts(
            "reconfigure_1", admins=len(admin_ids), trusts=trust_count, date=utils.format_datetime()
        ),
    )
    await event._client.send_message(event.message.chat_id, templates.texts("reconfigure_2"))


async def start_command(event: OnNewMessage.Event):
    if event.message.is_private:
        await _private_start_command(event)
    else:
        await _public_start_command(event)
