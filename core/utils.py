from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils.timezone import now
from . import models

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

def modified_times_ago(timestamp):
    delta = now() - timestamp
    if delta < timedelta(minutes=1):
        return f"{delta.seconds} seconds ago"
    elif delta < timedelta(hours=1):
        return f"{delta.seconds // 60} minutes ago"
    elif delta < timedelta(days=1):
        return f"{delta.seconds // 3600} hours ago"
    else:
        return f"{delta.days} days ago"

def notify_followers(user, name, content):
    followers = models.User.objects.filter(username__in=user.follows)
    for follower in followers:
        follower.notifications.append({
            "name": user.name,
            "category_name": name,
            "category_content": content
        })
        follower.save()
    
    user.modified_at = now()
    user.save(update_fields=["modified_at"])
