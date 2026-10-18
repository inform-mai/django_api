from django.db.models import Count, Avg

from bil_club.models import (
    GameRoom,
    Table,
    TableStatus,
    GameSession,
    Client
)


def get_dashboard():
    rooms = GameRoom.objects.annotate(
        table_count=Count('table'),
        avg_price=Avg('table__price')
    ).prefetch_related('table_set')

    total_tables = Table.objects.count()

    active_tables = Table.objects.filter(status=TableStatus.ACTIVE).count()
    active_game_sessions = GameSession.objects.filter(is_active=True).count()
    total_clients = Client.objects.count()

    stats = {
        "total_tables": total_tables,
        "active_tables": active_tables,
        "active_game_sessions": active_game_sessions,
        "total_clients": total_clients
    }

    result = {
        'rooms': rooms,
        'stats': stats
    }

    return result
