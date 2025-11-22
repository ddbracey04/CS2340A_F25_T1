from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated and request.user.is_recruiter():
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}

from .models import Message

def unread_messages_count(request):
    """Add unread message count to all templates for job seekers."""
    count = 0
    if request.user.is_authenticated and request.user.is_job_seeker():
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
    return {'unread_messages_count': count}