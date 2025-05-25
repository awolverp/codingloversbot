from telethon.events.common import EventCommon
from telethon.tl.custom.sendergetter import SenderGetter
from telethon.tl import types, custom
from telethon import utils, functions, TelegramClient as _BaseTelegramClient

import cachebox
import struct
import typing
import abc
import re

from core.utils import is_admin


_spam_cache = cachebox.TTLCache(500, 0.6)


def is_spam(id: int) -> bool:
    if _spam_cache.get(id, 0):
        return True

    _spam_cache[id] = 1
    return False


class TelegramClient(_BaseTelegramClient):
    me: types.User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_request = functions.InitConnectionRequest(
            api_id=self.api_id,
            device_model="POCO X6 Pro",
            system_version="12",
            app_version="11.1.0",
            system_lang_code="en",
            lang_pack="en",
            lang_code="en",
            query=None,
            proxy=None,
            params=types.JsonNull(),
        )

    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)
        self.me = await self.get_me()


class EventBuilder(abc.ABC):
    def __init__(self):
        self.resolved = False

    @classmethod
    @abc.abstractmethod
    def build(cls, update, others=None, self_id=None):
        pass

    async def resolve(self, _):
        if self.resolved:
            return

        self.resolved = True

    def filter(self, _):
        if not self.resolved:
            return

        return True


class _EventCommon(EventCommon):
    _client: TelegramClient


class OnNewMessage(EventBuilder):
    def __init__(
        self,
        pattern: typing.Union[str, re.Pattern, None] = None,
        private: bool = False,
        public: bool = False,
        admin_required: bool = False,
    ):
        super().__init__()

        if private and public:
            raise ValueError(
                "What are you doing? a message can't be in both of private and public chats!"
            )

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            self.pattern = pattern
        elif pattern is None:
            self.pattern = None
        else:
            raise TypeError(
                "The `pattern` argument should be string, re.Pattern, or None. got %r"
                % (type(pattern).__name__)
            )

        self.private = private
        self.public = public
        self.admin_required = admin_required

    @classmethod
    def build(cls, update, others=None, self_id=None):
        if isinstance(update, (types.UpdateNewMessage, types.UpdateNewChannelMessage)):
            if not isinstance(update.message, types.Message):
                return  # We don't care about MessageService's here
            event = cls.Event(update.message)
        elif isinstance(update, types.UpdateShortMessage):
            event = cls.Event(
                types.Message(
                    out=update.out,
                    mentioned=update.mentioned,
                    media_unread=update.media_unread,
                    silent=update.silent,
                    id=update.id,
                    peer_id=types.PeerUser(update.user_id),
                    from_id=types.PeerUser(self_id if update.out else update.user_id),
                    message=update.message,
                    date=update.date,
                    fwd_from=update.fwd_from,
                    via_bot_id=update.via_bot_id,
                    reply_to=update.reply_to,
                    entities=update.entities,
                    ttl_period=update.ttl_period,
                )
            )
        elif isinstance(update, types.UpdateShortChatMessage):
            event = cls.Event(
                types.Message(
                    out=update.out,
                    mentioned=update.mentioned,
                    media_unread=update.media_unread,
                    silent=update.silent,
                    id=update.id,
                    from_id=types.PeerUser(self_id if update.out else update.from_id),
                    peer_id=types.PeerChat(update.chat_id),
                    message=update.message,
                    date=update.date,
                    fwd_from=update.fwd_from,
                    via_bot_id=update.via_bot_id,
                    reply_to=update.reply_to,
                    entities=update.entities,
                    ttl_period=update.ttl_period,
                )
            )
        else:
            return

        return event

    def filter(self, event: "OnNewMessage.Event"):
        if (
            (event.message.out)
            or (self.private and not event.is_private)
            or (self.public and not (event.is_group or event.is_channel))
        ):
            return

        if self.pattern:
            match = self.pattern.match(event.message.message or "")
            if not match:
                return

        if self.admin_required and not is_admin(event.message.sender_id):
            return

        if is_spam(event.message.sender_id):
            return

        return super().filter(event)

    class Event(_EventCommon):
        def __init__(self, message):
            self.__dict__["_init"] = False
            super().__init__(
                chat_peer=message.peer_id,
                msg_id=message.id,
                broadcast=bool(message.post),
            )

            self.message: custom.Message = message

        def _set_client(self, client):
            super()._set_client(client)
            m = self.message
            m._finish_init(client, self._entities, None)
            self.__dict__["_init"] = True  # No new attributes can be set

        def __getattr__(self, item):
            return self.__dict__[item]

        def __setattr__(self, name, value):
            if not self.__dict__["_init"] or name in self.__dict__:
                self.__dict__[name] = value


class OnCommand(OnNewMessage):
    def __init__(
        self,
        command: typing.Union[typing.List[str], str],
        private: bool = False,
        public: bool = False,
        admin_required: bool = False,
    ):
        if isinstance(command, str):
            self.command = [command.replace("/", "", 1)]

        elif isinstance(command, list):
            self.command = [i.replace("/", "", 1) for i in command]

        else:
            raise TypeError(
                "The `command` argument should be string, or list. got %r"
                % (type(command).__name__)
            )

        super().__init__(
            None,
            private=private,
            public=public,
            admin_required=admin_required,
        )

    def filter(self, event: "OnCommand.Event"):
        if (
            (event.message.out)
            or (self.private and not event.is_private)
            or (self.public and not (event.is_group or event.is_channel))
        ):
            return

        if (
            (not event.message.entities)
            or (not isinstance(event.message.entities[0], types.MessageEntityBotCommand))
            or (event.message.entities[0].offset != 0)
        ):
            return

        _entity_command = event.message.message[
            event.message.entities[0].offset + 1 : event.message.entities[0].offset
            + event.message.entities[0].length
        ].split("@")

        if _entity_command.pop(0) not in self.command:
            return

        if _entity_command and (_entity_command[0] != event._client.me.username):
            return
        
        if self.admin_required and not is_admin(event.message.sender_id):
            return
        
        if is_spam(event.message.sender_id):
            return

        # we don't need to call OnNewMessage.filter, so we couldn't use `super` here.
        return EventBuilder.filter(self, event)


class OnCallbackQuery(EventBuilder):
    def __init__(
        self,
        data: typing.Union[str, bytes, None] = None,
        split: typing.Union[
            typing.Tuple[typing.Union[str, bytes, None], int], typing.Union[str, bytes, None]
        ] = None,
        admin_required: bool = False,
    ):
        super().__init__()

        if isinstance(data, str):
            data = data.encode("utf-8")

        self.data = data

        if isinstance(split, tuple):
            self.split_char = split[0]
            self.split_char_count = split[1]
        else:
            self.split_char = split
            self.split_char_count = None

        if isinstance(self.split_char, str):
            self.split_char = self.split_char.encode("utf-8")

        self.admin_required = admin_required

    @classmethod
    def build(cls, update, others=None, self_id=None):
        if isinstance(update, types.UpdateBotCallbackQuery):
            return cls.Event(update, update.peer, update.msg_id)
        elif isinstance(update, types.UpdateInlineBotCallbackQuery):
            # See https://github.com/LonamiWebs/Telethon/pull/1005
            # The long message ID is actually just msg_id + peer_id
            mid, pid = struct.unpack("<ii", struct.pack("<q", update.msg_id.id))
            peer = types.PeerChannel(-pid) if pid < 0 else types.PeerUser(pid)
            return cls.Event(update, peer, mid)

    def filter(self, event: "OnCallbackQuery.Event"):
        # We can't call super().filter(...) because it ignores chat_instance
        if self.data:
            # This structure is very faster than regexp
            if (not self.split_char) and self.data != event.query.data:
                return

            else:
                if (
                    self.split_char_count
                    and event.query.data.count(self.split_char) != self.split_char_count
                ):
                    return

                if self.data != event.query.data.split(self.split_char, 2)[0]:
                    return

        if self.admin_required and not is_admin(event.query.user_id):
            return

        if is_spam(event.query.user_id):
            return

        return True

    class Event(_EventCommon, SenderGetter):
        def __init__(self, query, peer, msg_id):
            super().__init__(peer, msg_id=msg_id)
            SenderGetter.__init__(self, query.user_id)
            self.query: typing.Union[
                types.UpdateBotCallbackQuery, types.UpdateInlineBotCallbackQuery
            ] = query

            self._message = None
            self._answered = False

        def _set_client(self, client):
            super()._set_client(client)
            self._sender, self._input_sender = utils._get_entity_pair(
                self.sender_id, self._entities, client._mb_entity_cache
            )

        @property
        def id(self):
            """
            Returns the query ID. The user clicking the inline
            button is the one who generated this random ID.
            """
            return self.query.query_id

        @property
        def message_id(self):
            """
            Returns the message ID to which the clicked inline button belongs.
            """
            return self._message_id

        @property
        def data(self):
            """
            Returns the data payload from the original inline button.
            """
            return self.query.data

        @property
        def chat_instance(self):
            """
            Unique identifier for the chat where the callback occurred.
            Useful for high scores in games.
            """
            return self.query.chat_instance

        async def get_message(self):
            """
            Returns the message to which the clicked inline button belongs.
            """
            if self._message is not None:
                return self._message

            try:
                chat = await self.get_input_chat() if self.is_channel else None
                self._message = await self._client.get_messages(chat, ids=self._message_id)
            except ValueError:
                return

            return self._message

        async def _refetch_sender(self):
            self._sender = self._entities.get(self.sender_id)
            if not self._sender:
                return

            self._input_sender = utils.get_input_peer(self._chat)
            if not getattr(self._input_sender, "access_hash", True):
                # getattr with True to handle the InputPeerSelf() case
                try:
                    self._input_sender = self._client._mb_entity_cache.get(
                        utils.resolve_id(self._sender_id)[0]
                    )._as_input_peer()
                except AttributeError:
                    m = await self.get_message()
                    if m:
                        self._sender = m._sender
                        self._input_sender = m._input_sender

        async def answer(self, message=None, cache_time=0, *, url=None, alert=False):
            """
            Answers the callback query (and stops the loading circle).

            Args:
                message (`str`, optional):
                    The toast message to show feedback to the user.

                cache_time (`int`, optional):
                    For how long this result should be cached on
                    the user's client. Defaults to 0 for no cache.

                url (`str`, optional):
                    The URL to be opened in the user's client. Note that
                    the only valid URLs are those of games your bot has,
                    or alternatively a 't.me/your_bot?start=xyz' parameter.

                alert (`bool`, optional):
                    Whether an alert (a pop-up dialog) should be used
                    instead of showing a toast. Defaults to `False`.
            """
            if self._answered:
                return

            self._answered = True
            return await self._client(
                functions.messages.SetBotCallbackAnswerRequest(
                    query_id=self.query.query_id,
                    cache_time=cache_time,
                    alert=alert,
                    message=message,
                    url=url,
                )
            )

        @property
        def via_inline(self):
            """
            Whether this callback was generated from an inline button sent
            via an inline query or not. If the bot sent the message itself
            with buttons, and one of those is clicked, this will be `False`.
            If a user sent the message coming from an inline query to the
            bot, and one of those is clicked, this will be `True`.

            If it's `True`, it's likely that the bot is **not** in the
            chat, so methods like `respond` or `delete` won't work (but
            `edit` will always work).
            """
            return isinstance(self.query, types.UpdateInlineBotCallbackQuery)

        async def respond(self, *args, **kwargs):
            """
            Responds to the message (not as a reply). Shorthand for
            `telethon.client.messages.MessageMethods.send_message` with
            ``entity`` already set.

            This method also creates a task to `answer` the callback.

            This method will likely fail if `via_inline` is `True`.
            """
            self._client.loop.create_task(self.answer())
            return await self._client.send_message(await self.get_input_chat(), *args, **kwargs)

        async def reply(self, *args, **kwargs):
            """
            Replies to the message (as a reply). Shorthand for
            `telethon.client.messages.MessageMethods.send_message` with
            both ``entity`` and ``reply_to`` already set.

            This method also creates a task to `answer` the callback.

            This method will likely fail if `via_inline` is `True`.
            """
            self._client.loop.create_task(self.answer())
            kwargs["reply_to"] = self.query.msg_id
            return await self._client.send_message(await self.get_input_chat(), *args, **kwargs)

        async def edit(self, *args, **kwargs):
            """
            Edits the message. Shorthand for
            `telethon.client.messages.MessageMethods.edit_message` with
            the ``entity`` set to the correct :tl:`InputBotInlineMessageID` or :tl:`InputBotInlineMessageID64`.

            Returns `True` if the edit was successful.

            This method also creates a task to `answer` the callback.

            .. note::

                This method won't respect the previous message unlike
                `Message.edit <telethon.tl.custom.message.Message.edit>`,
                since the message object is normally not present.
            """
            self._client.loop.create_task(self.answer())
            if isinstance(
                self.query.msg_id, (types.InputBotInlineMessageID, types.InputBotInlineMessageID64)
            ):
                return await self._client.edit_message(self.query.msg_id, *args, **kwargs)
            else:
                return await self._client.edit_message(
                    await self.get_input_chat(), self.query.msg_id, *args, **kwargs
                )

        async def delete(self, *args, **kwargs):
            """
            Deletes the message. Shorthand for
            `telethon.client.messages.MessageMethods.delete_messages` with
            ``entity`` and ``message_ids`` already set.

            If you need to delete more than one message at once, don't use
            this `delete` method. Use a
            `telethon.client.telegramclient.TelegramClient` instance directly.

            This method also creates a task to `answer` the callback.

            This method will likely fail if `via_inline` is `True`.
            """
            self._client.loop.create_task(self.answer())
            if isinstance(
                self.query.msg_id, (types.InputBotInlineMessageID, types.InputBotInlineMessageID64)
            ):
                raise TypeError(
                    "Inline messages cannot be deleted as there is no API request available to do so"
                )
            return await self._client.delete_messages(
                await self.get_input_chat(), [self.query.msg_id], *args, **kwargs
            )
