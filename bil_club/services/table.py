from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ObjectDoesNotExist

from bil_club.models import (
    Table,
    TableStatus
)
from .errors import (
    ValidationError,
    NotFoundError
)


CHANGING_TABLE_STATUSES = (TableStatus.ACTIVE, TableStatus.FROZEN)


def _validate_changing_status(change_to, table_status):
    if change_to not in CHANGING_TABLE_STATUSES:
        raise ValidationError("Изменить статус стола можно на 'Свободен' или 'На обслуживании'")

    if change_to == table_status:
        raise ValidationError("Изменить статус стола на уже присущий ему статус нельзя")


@transaction.atomic
def update_table_status(table_id, change_to, unavailable_until=None, unavailable_reason=None):
    try:
        table = Table.objects.get(id=table_id)
    except ObjectDoesNotExist:
        raise NotFoundError("Стол не найден")

    change_to = TableStatus(change_to)
    table_status = table.status
    _validate_changing_status(change_to, table_status)
    if unavailable_until:
        unavailable_until = parse_datetime(unavailable_until)

    if change_to == TableStatus.FROZEN:
        if not unavailable_reason:
            raise ValidationError("При измении статуса стола на 'На обслуживании' нужна причина недоступности")
        if not unavailable_until:
            raise ValidationError("Неверный формат даты")

        table.status = TableStatus.FROZEN
        table.unavailable_until = unavailable_until
        table.unavailable_reason = unavailable_reason

        table.save()

    elif change_to == TableStatus.ACTIVE:
        if table.unavailable_until and timezone.now() < table.unavailable_until:
            raise ValidationError("Изменить статус стола на 'Свободен' нельзя до того времени, как он станет доступным")

        table.status = TableStatus.ACTIVE
        table.unavailable_reason = None
        table.unavailable_until = None

        table.save()

    result = {
        "success_update": True,
        "table": str(table),
        "new_status": table.status,
        "unavailable_reason": table.unavailable_reason,
        "unavailable_until": table.unavailable_until
    }

    return result
