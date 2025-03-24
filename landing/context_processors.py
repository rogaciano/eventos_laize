from .models import Message

def unread_messages_count(request):
    """
    Context processor to add unread messages count to all templates
    """
    if request.user.is_authenticated:
        count = Message.objects.filter(is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}
