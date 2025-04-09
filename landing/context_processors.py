from .models import Message, SiteSettings

def unread_messages_count(request):
    """
    Context processor to add unread messages count to all templates
    """
    if request.user.is_authenticated:
        count = Message.objects.filter(is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}

def site_settings(request):
    """
    Context processor to add site settings to all templates
    """
    settings, created = SiteSettings.objects.get_or_create(pk=1)
    return {'site_settings': settings}
