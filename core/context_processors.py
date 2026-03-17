from django.utils import timezone
from .models import Notification
from .translations import TRANSLATIONS

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'INR': '₹',
}


def site_settings(request):
    lang = 'en'
    context = {
        'site_name': 'Expense Tracker',
        'current_year': timezone.now().year,
        'currency_symbol': '$',
    }
    if request.user.is_authenticated:
        context['unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        context['currency_symbol'] = CURRENCY_SYMBOLS.get(
            request.user.currency, '$'
        )
        lang = getattr(request.user, 'language', 'en') or 'en'

    context['t'] = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    context['current_lang'] = lang
    return context
