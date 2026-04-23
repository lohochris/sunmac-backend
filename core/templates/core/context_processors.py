"""
Context processors for passing data to all templates
"""
from django.conf import settings

def api_keys(request):
    """
    Pass API keys to all templates securely.
    Available in templates as {{ YOUTUBE_API_KEY }}
    """
    return {
        'YOUTUBE_API_KEY': getattr(settings, 'YOUTUBE_API_KEY', ''),
    }