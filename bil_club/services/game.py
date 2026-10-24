import uuid
import math
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q
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

ALLOWED_ORDER_FIELDS = ('-start_at', 'start_at', '-total_cost', 'total_cost')


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


def get_archive_sessions(search=None, room_type=None, ordering='-start_at', page=1):
    game_sessions = GameSession.objects.filter(
        is_active=False
    ).select_related('client', 'table', 'table__room')

    if search:
        game_sessions = game_sessions.filter(Q(client__name__icontains=search))

    if room_type:
        game_sessions = game_sessions.filter(table__room__room_name=room_type)

    if ordering not in ALLOWED_ORDER_FIELDS:
        ordering = '-start_at'

    queryset = game_sessions.order_by(ordering)

    paginator = Paginator(queryset, 10)

    try:
        page_obj = paginator.get_page(page)
    except Exception:
        page_obj = paginator.get_page(1)

    game_sessions_data = []
    for game_session in page_obj:
        duration_minutes = 0
        if game_session.end_at and game_session.start_at:
            duration_minutes = int((game_session.end_at - game_session.start_at).total_seconds() // 60)

        game_sessions_data.append({
            "id": str(game_session.id),
            "client_name": game_session.client.name,
            "table_type": game_session.table.get_type_display(),
            "room_name": game_session.table.room.get_room_name_display() if game_session.table.room else "Не указан",
            "start_at": str(game_session.start_at),
            "end_at": str(game_session.end_at) if game_session.end_at else None,
            "total_cost": float(game_session.total_cost) if game_session.total_cost else 0.00,
            "duration_minutes": duration_minutes
        })

    result = {
        "game_sessions": game_sessions_data,
        "pagination": {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    }
    return result


def get_session_details(session_id):
    try:
        game_session = GameSession.objects.select_related(
            'client', 'table', 'table__room'
        ).get(id=session_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Игровая сессия не найдена")

    duration_minutes = 0
    if game_session.end_at and game_session.start_at:
        duration_minutes = int((game_session.end_at - game_session.start_at).total_seconds() // 60)

    return {
        "id": str(game_session.id),
        "client_name": game_session.client.name,
        "client_phone": game_session.client.phone,
        "client_skill": game_session.client.skill,
        "table_type": game_session.table.get_type_display(),
        "room_name": game_session.table.room.get_room_name_display() if game_session.table.room else "Не указан",
        "price_per_hour": float(game_session.table.price),
        "start_at": str(game_session.start_at),
        "end_at": str(game_session.end_at) if game_session.end_at else None,
        "total_cost": float(game_session.total_cost) if game_session.total_cost else 0.00,
        "duration_minutes": duration_minutes
    }
