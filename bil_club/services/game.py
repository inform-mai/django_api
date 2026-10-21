import uuid
import math
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from bil_club.models import (
    GameSession,
    Client,
    Table,
    TableStatus
)
from .errors import (
    NotFoundError,
    ValidationError,
    ForbiddenError
)


def _formatting_time_spent(time_spent):
    hours = Decimal(str(time_spent.total_seconds() / 3600))
    hours_rounded = Decimal(math.ceil(float(hours) * 2)) / 2

    if hours_rounded < Decimal('0.5'):
        hours_rounded = Decimal('0.5')

    return hours_rounded


def get_active_game_sessions():
    game_sessions = GameSession.objects.filter(is_active=True).select_related(
        'table',
        'client',
        'table__room'
    ).order_by('-start_at')

    result = {"active_game_sessions": game_sessions}

    return result


@transaction.atomic
def start_session(table_id: uuid.UUID, client_id: uuid.UUID):
    try:
        table = Table.objects.select_for_update().get(id=table_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Стол не найден")

    if table.status != TableStatus.ACTIVE:
        raise ValidationError(f"Стол недоступен: {table.get_status_display()}")

    try:
        client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Клиент не найден")

    game_session = GameSession.objects.create(
        table=table,
        client=client,
        start_at=timezone.now(),
        is_active=True
    )

    table.status = TableStatus.UNAVAILABLE
    table.save()

    result = {
        "start_success": True,
        "game_session": str(game_session.id),
        "table": str(table),
        "start_at": game_session.start_at.isoformat(),
        "client_name": client.name
    }

    return result


@transaction.atomic
def end_session(session_id: uuid.UUID, client_id: uuid.UUID):
    try:
        game_session = GameSession.objects.select_for_update().get(id=session_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Игра не найдена")

    if not game_session.client or str(game_session.client_id) != str(client_id):
        raise ForbiddenError("Клиент, не участвующий в игре, не может её завершить!")

    client = game_session.client

    table = game_session.table

    if not game_session.is_active:
        raise ValidationError("Нельзя завершить игру, которая ещё не началась или уже была закончена!")

    game_session.end_at = timezone.now()
    time_spent = game_session.end_at - game_session.start_at
    hours_spent = _formatting_time_spent(time_spent)
    total_cost = hours_spent * table.price

    game_session.total_cost = total_cost
    game_session.is_active = False

    table.status = TableStatus.ACTIVE

    game_session.save()
    table.save()

    result = {
        "end_success": True,
        "game_session": str(game_session),
        "table": str(table),
        "start_at": game_session.start_at.isoformat(),
        "end_at": game_session.end_at.isoformat(),
        "time_spent": str(time_spent),
        "total_cost": total_cost,
        "client_name": client.name
    }

    return result
