from django import template
from decimal import Decimal

register = template.Library()

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'INR': '₹',
}


@register.filter
def currency(value, user=None):
    if value is None:
        return ''
    try:
        amount = Decimal(str(value))
    except Exception:
        return value
    symbol = '$'
    if user and hasattr(user, 'currency'):
        symbol = CURRENCY_SYMBOLS.get(user.currency, '$')
    formatted = f'{amount:,.2f}'
    return f'{symbol}{formatted}'


@register.simple_tag(takes_context=True)
def format_currency(context, value):
    if value is None:
        return ''
    try:
        amount = Decimal(str(value))
    except Exception:
        return value
    user = context.get('request', None)
    symbol = '$'
    if user and hasattr(user, 'user') and hasattr(user.user, 'currency'):
        symbol = CURRENCY_SYMBOLS.get(user.user.currency, '$')
    formatted = f'{amount:,.2f}'
    return f'{symbol}{formatted}'
