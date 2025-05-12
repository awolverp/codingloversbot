"""
Here is our database models and ORMs
"""

from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import sqltypes

from core import env


class Model(AsyncAttrs, DeclarativeBase):
    """
    This is our ORM Model
    """

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__qualname__,
            ", ".join(f"{k}={getattr(self, k, None)}" for k in self.__table__.columns.keys()),
        )


class GroupWarnAction:
    MUTE_24H = 0
    " Mute for 24 hours "

    MUTE = 1
    " Mute for forever "

    KICK = 2
    " Kick the user "

    BAN = 3
    " Ban the user "


class Group(Model):
    """
    Groups table

    - id
    - name
    - warn_action
    """

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(sqltypes.BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(sqltypes.VARCHAR(255), nullable=False)
    warn_action: Mapped[int] = mapped_column(sqltypes.SmallInteger, nullable=False)


class Admin(Model):
    """
    Admins table

    - id
    - user_id
    - group_id
    """

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(sqltypes.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sqltypes.BigInteger, nullable=False)

    # Here I decided to don't use ForeignKeys.
    # This project is not very important, and also this can improve the database speed
    group_id: Mapped[int] = mapped_column(sqltypes.BigInteger, nullable=False)


class Participant(Model):
    """
    Participants table

    - id
    - user_id
    - is_trusted
    - warns
    - votekicks
    - group_id
    """

    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(sqltypes.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sqltypes.BigInteger, nullable=False, index=True)
    is_trusted: Mapped[bool] = mapped_column(sqltypes.Boolean, nullable=False)

    warns: Mapped[int] = mapped_column(sqltypes.SmallInteger, nullable=False)
    votekicks: Mapped[int] = mapped_column(sqltypes.SmallInteger, nullable=False)

    # Here I decided to don't use ForeignKeys.
    # This project is not very important, and also this can improve the database speed
    group_id: Mapped[int] = mapped_column(sqltypes.BigInteger, nullable=False, index=True)


if env.DATABASE["type"] == "mysql":
    _engine = create_async_engine(
        "mysql+aiomysql://{}:{}@{}:{}/{}".format(
            env.DATABASE["user"],
            env.DATABASE["password"],
            env.DATABASE["host"],
            env.DATABASE["port"],
            env.DATABASE["name"],
        ),
    )
else:
    _engine = create_async_engine(
        "sqlite+aiosqlite:///{}".format(
            env.DATABASE["name"] + ".sqlite3",
        ),
    )

db = async_sessionmaker(_engine, expire_on_commit=False)


async def initialize_database():
    async with _engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def dispose_database():
    await _engine.dispose()
