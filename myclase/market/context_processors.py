from .utils import get_user_avatar
from .models import ProductNotification

def user_avatar(request):
    if request.user.is_authenticated:
        avatar_url = get_user_avatar(request.user)
        return {'user_avatar_url': avatar_url}
    return {}

def product_notifications(request):
    user = getattr(request, "user", None)
    count = 0
    if user and user.is_authenticated:
        count = ProductNotification.objects.filter(seller=user, seen=False).count()
    return {"user_products_unread_count": count}