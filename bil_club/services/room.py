import uuid
from django.core.exceptions import ObjectDoesNotExist

from bil_club.models import (
    GameRoom,
    Table,
    TableStatus,
    GameSession,
)
from .errors import NotFoundError


def get_room_detail(room_id: uuid.UUID):
    try:
        room = GameRoom.objects.get(id=room_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Room with passed id not found")

    tables = Table.objects.filter(room=room)
    total_tables = tables.count()
    active_tables = tables.filter(status=TableStatus.ACTIVE).count()
    active_game_sessions = GameSession.objects.filter(table__room=room, is_active=True).count()

    room_stats = {
        "total_tables": total_tables,
        "active_tables": active_tables,
        "active_game_sessions": active_game_sessions
    }

    result = {
        "room": room,
        "stats": room_stats,
        "tables": tables
    }

    return result