"""
#12 API — Statistics endpoint: monthly summaries, savings rate, category breakdown.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
from core.models import Expense, Income, Budget, FinancialGoal, Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        from core.models import Notification
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'is_read', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']


class MonthlyStatsView(APIView):
    """Returns 12-month income/expense trend + savings rate for mobile clients."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        data = []
        for i in range(11, -1, -1):
            d = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if d.month == 12:
                next_m = d.replace(year=d.year + 1, month=1, day=1)
            else:
                next_m = d.replace(month=d.month + 1, day=1)

            exp = Expense.objects.filter(
                user=request.user, date__gte=d, date__lt=next_m
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
            inc = Income.objects.filter(
                user=request.user, date__gte=d, date__lt=next_m
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0')

            savings = float(inc) - float(exp)
            data.append({
                'month': d.strftime('%b %Y'),
                'expenses': float(exp),
                'income': float(inc),
                'savings': savings,
                'savings_rate': round(savings / float(inc) * 100, 1) if inc else 0,
            })
        return Response({'monthly_trend': data})


class NotificationListView(APIView):
    """#12 List and mark-read notifications via the API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import Notification
        notifs = Notification.objects.filter(user=request.user)[:50]
        s = NotificationSerializer(notifs, many=True)
        return Response(s.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from core.models import Notification
        from django.shortcuts import get_object_or_404
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({'success': True})
