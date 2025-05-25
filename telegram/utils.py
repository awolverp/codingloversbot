from telethon.tl.custom import Conversation
from telethon.tl import types
from telethon.tl.patched import Message
from telethon.utils import get_peer_id
import datetime
from os.path import splitext
import typing


_R = typing.TypeVar("_R")


def get_extension(file: types.TypeMessageMedia) -> str:
    """
    Returns a media extension

    Example::

        message = await client.get_messages(chat, ids=1337)
        extension = get_extension(message.media)
        print(extension)
        # .txt
    """
    if not isinstance(file, types.MessageMediaDocument):
        return ""

    name = None

    for i in file.document.attributes:
        if isinstance(i, types.DocumentAttributeFilename):
            name = i.file_name
            break

    if name is None:
        return ""

    _, ext = splitext(name)
    return ext


async def read_conversation(
    conv: Conversation,
    condition: typing.Callable[[types.Message], bool],
    invalid_response_text: str,
    prompt: str = "",
    last_message_id: typing.Optional[int] = None,
    timeout: typing.Optional[float] = 5 * 60,
    deserializer: typing.Callable[[types.Message], _R] = lambda x: x.message,
    cancel_by_slash: bool = True,
    accept_media: bool = False,
    extensions: typing.List[str] = [],
    force_document: bool = False,
) -> typing.Optional[_R]:
    """
    Helper to input from user by `client.conversation(chat)`

    - conv (`Conversation`): the created conversation from `client.conversation(chat)`
    - condition (`(Message) -> bool`): an condition for user response
    - invalid_response_text (`str`): if user response is not acceptable,
                                        this message will send to user and user can try again.
    - prompt (`str`): Prompt. can be empty.
    - last_message_id (`int | None`): You have to set this if you don't want to set `prompt`.
    - timeout (`float | None`): timeout
    - deserializer (`(Message) -> Any`): deserialize user response. on default returns message text.
    - cancel_by_slash (`bool`): cancel by slash?
    - accept_media (`bool`): Is media acceptable?
    - extensions (`list[str]`): allowed extensions for media. empty means no matter.
    - force_document (`bool`): Is media has to document?

    Example::

        async with client.conversation(chat_id) as conv:
            name = await read_conversation(
                conv,
                lambda x: True, # no condition
                "Your response is invalid, send your name again (or send /cancel):",
                prompt="Send your name (or send /cancel):"
            )
            if name is None: # this means user cancelled the conversation
                await conv.send_message("Ok, cancelled.")
            else:
                assert isinstance(name, str)
                await conv.send_message("Hello, %s" % name)

            age = await read_conversation(
                conv,
                lambda x: x.message.isdigit(), # `x` type is `types.Message`
                "Please send number! try again (or send /cancel):",
                prompt="Send your age (or send /cancel):",
                deserializer=lambda x: int(x.message), # `x` type is `types.Message`
            )
            if age is None: # this means user cancelled the conversation
                await conv.send_message("Ok, cancelled.")
            else:
                assert isinstance(age, int)
                await conv.send_message("Your age is %d" % age)
    """
    if prompt:
        await conv.send_message(prompt)
        last_message_id = None

    while True:
        response: types.Message = await conv.get_response(last_message_id, timeout=timeout)

        if response.media and not isinstance(response.media, types.MessageMediaWebPage):
            if not accept_media:
                await conv.send_message(invalid_response_text, reply_to=response.id)
                continue

            if force_document and not isinstance(response.media, types.MessageMediaDocument):
                await conv.send_message(invalid_response_text, reply_to=response.id)
                continue

            if extensions and get_extension(response.media) not in extensions:
                await conv.send_message(invalid_response_text, reply_to=response.id)
                continue

        if response.message == "/cancel":
            return None

        if cancel_by_slash and response.message.startswith("/"):
            return None

        if not condition(response):
            await conv.send_message(invalid_response_text, reply_to=response.id)
            continue

        return deserializer(response)


class ParsedCommand:
    __slots__ = ("replied", "user_id", "duration")

    def __init__(self, replied: bool, user_id: int, duration: int):
        self.replied = replied
        self.user_id = user_id
        self.duration = duration

    @property
    def until_date(self) -> datetime.datetime | None:
        if not self.duration:
            return None

        return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=self.duration
        )


async def _resolve_user_id(
    message: Message, intext_allowed: bool = True, reply_allowed: bool = True
):
    if reply_allowed and message.reply_to_msg_id:
        _msg: Message = await message.get_reply_message()

        if isinstance(_msg.from_id, types.PeerUser):
            return _msg.sender_id, True

    if not intext_allowed:
        return 0, False

    print(message.entities)

    try:
        tg = message.message.split(" ")[1]
    except IndexError:
        return 0, False

    if tg.startswith("@"):
        return tg, False

    try:
        return int(tg), False
    except ValueError:
        return 0, False


async def parse_command_message(
    message: Message,
    intext_allowed: bool = True,
    reply_allowed: bool = True,
    duration_allowed: bool = False,
) -> ParsedCommand:
    target, is_replied = await _resolve_user_id(
        message, reply_allowed=reply_allowed, intext_allowed=intext_allowed
    )

    if isinstance(target, str):
        try:
            entity = await message._client.get_input_entity(target)
        except ValueError:
            raise KeyError(target) from None

        if not isinstance(entity, types.InputPeerUser):
            raise KeyError(target) from None

        target = entity.user_id

    if target == message._client.me.id:
        target = None

    if not target:
        raise ValueError

    if not duration_allowed:
        return ParsedCommand(is_replied, target, 0)

    try:
        dur = message.message.split(" ")[1 if is_replied else 2]
    except IndexError:
        return ParsedCommand(is_replied, target, 0)

    if dur[-1] == "s":
        _mul = 1
    elif dur[-1] == "m":
        _mul = 60
    elif dur[-1] == "h":
        _mul = 60 * 60
    elif dur[-1] == "d":
        _mul = 60 * 60 * 24
    else:
        return ParsedCommand(is_replied, target, 0)

    try:
        return ParsedCommand(is_replied, target, int(dur[:-1]) * _mul)
    except ValueError:
        return ParsedCommand(is_replied, target, 0)
