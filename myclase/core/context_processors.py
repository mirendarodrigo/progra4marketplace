# core/context_processors.py
from market.models import ProductNotification
from chat.models import Message

def navbar_notifications(request):
    """
    Contadores globales para el navbar:
    - user_products_unread_count: notificaciones de productos no vistas
    - user_messages_unread_count: mensajes sin leer en conversaciones donde participa
    - user_nav_total_unread: suma de ambos (para el globito del avatar)
    """
    if not request.user.is_authenticated:
        return {}

    # 🛒 Notificaciones de productos (las que ya usabas)
    products_unread = ProductNotification.objects.filter(
        seller=request.user,
        seen=False,
    ).count()

    # 💬 Mensajes no leídos:
    # - conversaciones donde participa el usuario
    # - mensajes marcados como no leídos
    # - que NO fueron enviados por el propio usuario
    messages_unread = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False,
    ).exclude(
        sender=request.user
    ).count()

    return {
        "user_products_unread_count": products_unread,
        "user_messages_unread_count": messages_unread,
        "user_nav_total_unread": products_unread + messages_unread,
    }
