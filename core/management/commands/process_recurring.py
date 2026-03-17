"""
#1  Management command to auto-generate recurring transactions.
Run: python manage.py process_recurring
Schedule with cron or django-apscheduler.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from core.models import Expense, Income


class Command(BaseCommand):
    help = 'Create new instances of recurring Expense / Income records for the current period.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        created_exp = self._process_model(Expense, today)
        created_inc = self._process_model(Income, today)
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Created {created_exp} expense(s), {created_inc} income record(s).'
            )
        )

    def _next_date(self, recurrence, ref_date):
        if recurrence == 'daily':
            return ref_date + timedelta(days=1)
        if recurrence == 'weekly':
            return ref_date + timedelta(weeks=1)
        if recurrence == 'monthly':
            return ref_date + relativedelta(months=1)
        if recurrence == 'yearly':
            return ref_date + relativedelta(years=1)
        return None

    def _process_model(self, Model, today):
        created = 0
        qs = Model.objects.exclude(recurrence='none').select_related('user', 'category')
        for obj in qs:
            # Stop if past recurrence_end_date
            if obj.recurrence_end_date and today > obj.recurrence_end_date:
                continue
            next_date = self._next_date(obj.recurrence, obj.date)
            if next_date is None or next_date > today:
                continue
            # Check if one already exists for the next period
            existing = Model.objects.filter(
                user=obj.user,
                category=obj.category,
                date=next_date,
                recurrence=obj.recurrence,
            ).exists()
            if existing:
                continue
            # Clone the record
            obj.pk = None
            obj.date = next_date
            obj.save()
            created += 1
        return created
