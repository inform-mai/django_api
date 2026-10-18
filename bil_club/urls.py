from django.urls import path
from bil_club import views

app_name = 'bil_club'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('rooms/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('clients/', views.clients, name='clients'),
    path('clients/<uuid:client_id>/', views.client_profile, name='client_profile'),
    path('sessions/', views.game_sessions, name='game_sessions'),
    path('api/sessions/start/<uuid:table_id>/', views.start_session, name='start_session'),
    path('api/sessions/end/<uuid:session_id>/', views.end_session, name='end_session'),
    path('api/clients/add/', views.add_client, name='add_client'),
    path('api/tables/<uuid:table_id>/status/', views.update_table, name='update_table'),
]