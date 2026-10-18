from django.shortcuts import render
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from bil_club.services.errors import (
    NotFoundError,
    ValidationError
)
from bil_club.services import (
    dashboard as dashboard_service,
    room as room_service,
    client as client_service,
    game as game_service,
    table as table_service
)


def dashboard(request):
    context = dashboard_service.get_dashboard()
    return render(request, 'bil_club/dashboard.html', context)


def room_detail(request, room_id):
    try:
        context = room_service.get_room_detail(room_id)
    except NotFoundError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    return render(request, 'bil_club/rooms.html', context)


def clients(request):
    try:
        name = request.GET.get('name')
        skill = request.GET.get('skill')
        context = client_service.get_clients(name=name, skill=skill)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    return render(request, 'bil_club/clients.html', context)


def client_profile(request, client_id):
    try:
        context = client_service.get_client_profile(client_id)
    except NotFoundError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    return render(request, 'bil_club/client_profile.html', context)


def game_sessions(request):
    context = game_service.get_active_game_sessions()
    return render(request, 'bil_club/sessions.html', context)


@require_POST
def start_session(request, table_id):
    try:
        client_id = request.POST.get('client_id')
        result = game_service.start_session(table_id, client_id)
        return JsonResponse(result)
    except NotFoundError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)


@require_POST
def end_session(request, session_id):
    try:
        client_id = request.POST.get('client_id')
        result = game_service.end_session(session_id, client_id)
        return JsonResponse(result)
    except NotFoundError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)


@require_POST
def add_client(request):
    try:
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        skill = request.POST.get('skill')
        result = client_service.create_client(name, phone, skill)
        return JsonResponse(result)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)


@require_POST
def update_table(request, table_id):
    try:
        change_to = request.POST.get('change_to')
        unavailable_until = request.POST.get('unavailable_until')
        unavailable_reason = request.POST.get('unavailable_reason')

        result = table_service.update_table_status(
            table_id,
            change_to,
            unavailable_until=unavailable_until,
            unavailable_reason=unavailable_reason
        )

        return JsonResponse(result)
    except NotFoundError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)
    except ValidationError as error:
        response = {"code": error.code, "detail": error.detail}
        return JsonResponse(response)