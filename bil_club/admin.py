from django.contrib import admin

from .models import Table, GameSession, Client, GameRoom


@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_name')
    search_fields = ('id',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'type', 'status', 'unavailable_reason', 'unavailable_until')
    search_fields = ('id', 'room', 'type', 'status')


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'start_at', 'end_at', 'is_active')
    search_fields = ('id', 'table', 'is_active')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'skill', 'registered_at')
    search_fields = ('id', 'name')


