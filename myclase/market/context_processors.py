
from .utils import get_user_avatar

def user_avatar(request):
    if request.user.is_authenticated:
        avatar_url = get_user_avatar(request.user)
        return {'user_avatar_url': avatar_url}
    return {}
