# utils.py
def get_user_avatar(user):
    
    try:
        social_account = user.socialaccount_set.first()
        if social_account:
            
            return social_account.get_avatar_url()
    except:
        pass
 
    return '/static/img/default-avatar.png'  
