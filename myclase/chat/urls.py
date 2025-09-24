from django.urls import path
from . import views

app_name = 'chat'  # importante para usar namespaces en {% url %}

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:user_id>/', views.chat_room, name='chat_room'),
    path('send/', views.send_message, name='send_message'),
]
