"""
#8  Dark-mode server-side persist — saves user.theme via AJAX POST.
#19 Login/register views with rate limiting.
"""
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit


@login_required
@require_POST
def toggle_theme(request):
    """#8 — Save chosen theme to the user's profile."""
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'light')
    except (json.JSONDecodeError, AttributeError):
        theme = request.POST.get('theme', 'light')

    if theme not in ('light', 'dark', 'auto'):
        return JsonResponse({'error': 'Invalid theme'}, status=400)

    request.user.theme = theme
    request.user.save(update_fields=['theme'])
    return JsonResponse({'success': True, 'theme': theme})
