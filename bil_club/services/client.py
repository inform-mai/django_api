import uuid
import re
from django.db import transaction
from django.db.models import Count, Sum
from django.core.exceptions import ObjectDoesNotExist

from .errors import (
    ValidationError,
    NotFoundError,
)
from bil_club.models import (
    Client,
    GameSession,
)

FILTER_CLIENT_FIELDS = ('name', 'skill')

CREATE_CLIENT_FIELDS = ('name', 'skill', 'phone')


def _validate_post_name(name):
    if not name:
        raise ValidationError("При создании клиента его имя обязательно")
    if any(symbol.isdigit() for symbol in name):
        raise ValidationError("Имя пользователя не должно содержать цифр")
    if any(not symbol.isalnum() for symbol in name):
        raise ValidationError("Имя пользовтеля не должно содержать специальных символов")


def _validate_post_phone(phone):
    clean_phone = re.sub(r'[\s\-()]', '', phone)
    pattern = r'^\+7|d{10}$'

    if not re.match(pattern, clean_phone):
        raise ValidationError("Телефонный номер клиента должен соответсовать формату: +7XXXXXXXXXX")
    if Client.objects.filter(phone=clean_phone).exists():
        raise ValidationError("Клиент с этим номером телефона уже существует")

    return clean_phone


def _validate_post_skill(skill):
    if not skill:
        raise ValidationError("При создании клиента уровень его навыков обязателен")
    if not skill.isdigit():
        raise ValidationError("Уровень навыков должен быть числом")
    if not 0 <= int(skill) <= 5:
        raise ValidationError("Уровень навыков должен быть от 0 до 5")


def _filter_by_name(clients: Client, choice: str):
    if choice:
        try:
            clients = clients.filter(name__icontains=choice)
            return clients
        except (ValueError, TypeError):
            raise ValidationError("Недопустимый формат значения 'name' для фильтрации клиентов по нему")
    else:
        return clients


def _filter_by_skill(clients: Client, choice: str):
    if choice:
        try:
            clients = clients.filter(skill=int(choice))
            return clients
        except (ValueError, TypeError):
            raise ValidationError("Недопустимый формат значения 'skill' для фильтрации клиентов по нему")
    else:
        return clients


def _get_client_by_id(client_id: uuid.UUID):
    try:
        client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Клиент с полученным идентификатором не найден")
    return client


def get_clients(name=None, skill=None):
    clients = Client.objects.all()

    if name:
        clients = _filter_by_name(clients, name)
    if skill:
        clients = _filter_by_skill(clients, skill)

    clients = clients.order_by('-registered_at')

    result = {"clients": clients}

    return result


def get_client_profile(client_id):
    client = _get_client_by_id(client_id)

    client_stats = GameSession.objects.filter(client=client).aggregate(
        total_sessions=Count('id'),
        total_spent=Sum('total_cost')
    )

    game_sessions = GameSession.objects.filter(
        client=client
    ).select_related('table', 'table__room').order_by('-start_at')[:10]

    result = {
        "client": str(client),
        "stats": {
            "total_sessions": client_stats.get('total_sessions') or 0,
            "total_spent": client_stats.get('total_spent') or 0
        },
        "game_sessions": game_sessions
    }

    return result


@transaction.atomic
def create_client(name, phone, skill):
    _validate_post_name(name)
    phone = _validate_post_phone(phone)
    _validate_post_skill(skill)

    client = Client.objects.create(
        name=name,
        phone=phone,
        skill=skill
    )

    result = {
        "success_create": True,
        "name": client.name,
        "phone": client.phone,
        "skill": client.skill
    }

    return result
