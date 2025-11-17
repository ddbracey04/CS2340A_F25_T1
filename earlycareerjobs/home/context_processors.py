from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated and request.user.is_recruiter():
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
