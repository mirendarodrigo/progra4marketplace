from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<int:convo_id>/", views.room, name="room"),
    path("start/<int:user_id>/", views.start_chat, name="start"),
    # --- API en “tiempo casi real” ---
    path("api/messages/<int:convo_id>/", views.messages_since, name="messages_since"),
    path("api/send/<int:convo_id>/", views.api_send, name="api_send"),
]
