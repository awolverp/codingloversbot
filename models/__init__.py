from .database import (
    db as db,
    Group as Group,
    GroupWarnAction as GroupWarnAction,
    Admin as Admin,
    Participant as Participant,
    initialize_database as initialize_database,
    dispose_database as dispose_database,
)
from sqlalchemy import sql as sql
import cachebox

VOTEKICKS = cachebox.TTLCache[tuple[int, int], list[int]](0, ttl=1 * 60 * 60)
