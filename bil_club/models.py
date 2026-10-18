from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

import uuid


class GameRoomName(models.TextChoices):
    COMMON = 'common', 'Обычный'
    PREMIUM = 'premium', 'Премиум'
    GOLD = 'gold', 'Золотой'


class TableType(models.TextChoices):
    RUSSIAN = 'ru', 'Русский'
    AMERICAN = 'us', 'Американка'
    SNOOKER = 'sn', 'Снукер'


class TableStatus(models.TextChoices):
    ACTIVE = 'active', 'Свободен'
    UNAVAILABLE = 'unavailable', 'Занят'
    FROZEN = 'frozen', 'На обслуживании'


class GameRoom(models.Model):

    class Meta:
        verbose_name = 'Игровой зал'
        verbose_name_plural = 'Игровые залы'

    id = models.UUIDField(
        verbose_name='Идентификатор зала',
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        null=False
    )

    room_name = models.CharField(
        verbose_name='Название зала',
        null=False,
        choices=GameRoomName.choices,
        default=GameRoomName.COMMON
    )

    def __str__(self):
        return self.get_room_name_display()


class Table(models.Model):

    class Meta:
        verbose_name = 'Бильярдный стол'
        verbose_name_plural = 'Бильярдные столы'

    room = models.ForeignKey(
        GameRoom,
        verbose_name='Тип зала',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    id = models.UUIDField(
        verbose_name='Идентификатор стола',
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        null=False
    )
    type = models.CharField(
        verbose_name='Тип стола',
        choices=TableType.choices,
        null=False,
        default=TableType.RUSSIAN
    )
    status = models.CharField(
        verbose_name='Статус стола',
        choices=TableStatus.choices,
        null=False,
        default=TableStatus.FROZEN
    )
    unavailable_reason = models.CharField(
        verbose_name='Причина недоступности',
        default=None,
        null=True,
        blank=True,
    )
    unavailable_until = models.DateTimeField(
        verbose_name='Недоступен до',
        null=True,
        blank=True,
        default=None
    )
    price = models.DecimalField(
        verbose_name='Стоимость игры',
        max_digits=7,
        decimal_places=2,
        null=False,
        default=0.00
    )

    def __str__(self):
        return f'Стол №{self.id} [{self.get_type_display()}]'


class Client(models.Model):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    phone_validator = RegexValidator(
        regex=r'^\+7\d{10}$',
        code='invalid_phone_number',
        message="Введите номер телефона в формате: +79991234567"
    )

    skill_validator_min = MinValueValidator(
        limit_value=0,
        message="Уровень навыка должен быть больше либо равен нулю"
    )

    skill_validator_max = MaxValueValidator(
        limit_value=5,
        message="Уровень навыка не должен превосходить пяти"
    )

    id = models.UUIDField(
        verbose_name='Идентификатор пользователя',
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        null=False
    )
    name = models.CharField(
        verbose_name='Имя пользователя',
        null=False
    )

    phone = models.CharField(
        verbose_name='Телефон',
        max_length=12,
        validators=[phone_validator]
    )
    skill = models.IntegerField(
        verbose_name='Уровень навыков',
        null=False,
        default=0,
        validators=[skill_validator_min, skill_validator_max]
    )
    registered_at = models.DateTimeField(
        verbose_name='Дата регистрации',
        null=False,
        auto_now_add=True
    )

    def __str__(self):
        return f'Пользователь [{self.id}]'


class GameSession(models.Model):
    class Meta:
        verbose_name = 'Игровая сессия'
        verbose_name_plural = 'Игровые сессии'

    table = models.ForeignKey(
        Table,
        verbose_name='Идентификатор стола',
        on_delete=models.CASCADE)

    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions'
    )

    id = models.UUIDField(
        verbose_name='Идентификатор игры',
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        null=False
    )
    start_at = models.DateTimeField(
        verbose_name='Начало игры',
        null=False,
        auto_now_add=True
    )
    end_at = models.DateTimeField(
        verbose_name='Конец игры',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name='Статус игры',
        null=False,
        default=True
    )

    total_cost = models.DecimalField(
        verbose_name='Итоговая стоимость',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'Игровая сессия [{self.id}] на столе: {self.table}'

