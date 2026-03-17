"""
#7  Management command to send weekly summary emails to all users.
Run: python manage.py send_summary_email
Schedule weekly with cron / django-apscheduler.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
from core.models import Expense, Income
from core.emails import send_weekly_summary_email

User = get_user_model()


class Command(BaseCommand):
    help = 'Send weekly expense summary email to all opted-in users.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        week_start = today - timedelta(days=7)
        sent = 0
        for user in User.objects.filter(email_notifications=True, is_active=True):
            expenses = Expense.objects.filter(user=user, date__gte=week_start, date__lte=today)
            incomes = Income.objects.filter(user=user, date__gte=week_start, date__lte=today)
            total_exp = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')
            total_inc = incomes.aggregate(t=Sum('amount'))['t'] or Decimal('0')
            top_categories = list(
                expenses.values('category__name')
                .annotate(total=Sum('amount'))
                .order_by('-total')[:3]
            )
            summary_data = {
                'week_start': week_start,
                'week_end': today,
                'total_expenses': total_exp,
                'total_income': total_inc,
                'net': total_inc - total_exp,
                'top_categories': top_categories,
            }
            send_weekly_summary_email(user, summary_data)
            sent += 1
        self.stdout.write(self.style.SUCCESS(f'Sent summary emails to {sent} user(s).'))
