"""User online status tracking middleware and utilities."""
from django.utils import timezone
from django.core.cache import cache


LAST_SEEN_KEY = 'user_last_seen_{user_id}'
WEBSOCKET_CONNECTIONS_KEY = 'user_ws_connections_{user_id}'


def update_user_status(user):
    """Update user's last seen timestamp."""
    if user.is_authenticated:
        cache_key = LAST_SEEN_KEY.format(user_id=user.id)
        cache.set(cache_key, timezone.now(), 300)  # 5 minutes


def increment_active_socket(user_id):
    """Track active websocket connections for instant online presence."""
    cache_key = WEBSOCKET_CONNECTIONS_KEY.format(user_id=user_id)
    current_count = cache.get(cache_key, 0)
    new_count = current_count + 1
    cache.set(cache_key, new_count, 3600)
    cache.set(LAST_SEEN_KEY.format(user_id=user_id), timezone.now(), 300)
    return new_count


def decrement_active_socket(user_id):
    """Reduce active websocket count and prevent negative values."""
    cache_key = WEBSOCKET_CONNECTIONS_KEY.format(user_id=user_id)
    current_count = cache.get(cache_key, 0)
    new_count = max(current_count - 1, 0)
    if new_count == 0:
        cache.delete(cache_key)
    else:
        cache.set(cache_key, new_count, 3600)
    cache.set(LAST_SEEN_KEY.format(user_id=user_id), timezone.now(), 300)
    return new_count


def is_user_online(user_id):
    """Check if a user currently has at least one active websocket."""
    cache_key = WEBSOCKET_CONNECTIONS_KEY.format(user_id=user_id)
    return cache.get(cache_key, 0) > 0


def get_user_status(user):
    """
    Get user's online status.
    Returns: 'online', 'away', or 'offline'
    """
    if not user.is_authenticated:
        return 'offline'

    if is_user_online(user.id):
        return 'online'
    
    cache_key = LAST_SEEN_KEY.format(user_id=user.id)
    last_seen = cache.get(cache_key)
    
    if not last_seen:
        return 'offline'
    
    time_diff = (timezone.now() - last_seen).total_seconds()
    
    if time_diff < 60:  # Less than 1 minute
        return 'online'
    elif time_diff < 300:  # Less than 5 minutes
        return 'away'
    else:
        return 'offline'


def get_last_seen(user):
    """Get user's last seen timestamp."""
    if not user.is_authenticated:
        return None
    
    cache_key = LAST_SEEN_KEY.format(user_id=user.id)
    return cache.get(cache_key)


class UserStatusMiddleware:
    """Middleware to track user activity."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            update_user_status(request.user)
        
        response = self.get_response(request)
        return response
