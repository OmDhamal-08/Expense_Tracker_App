from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Expense, Income, Budget, FinancialGoal
from api.serializers import ExpenseSerializer, IncomeSerializer


class DashboardView(APIView):
    """GET /api/dashboard/ — Monthly summary, recent transactions, and budget overview."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)

        # Monthly totals
        monthly_expenses = Expense.objects.filter(
            user=user, date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        monthly_income = Income.objects.filter(
            user=user, date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Last month totals for comparison
        last_month_end = month_start - timezone.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        last_expenses = Expense.objects.filter(
            user=user, date__gte=last_month_start, date__lte=last_month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        last_income = Income.objects.filter(
            user=user, date__gte=last_month_start, date__lte=last_month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        def pct_change(current, previous):
            if previous == 0:
                return 0
            return round(float((current - previous) / previous * 100), 1)

        # Active budgets
        budgets = Budget.objects.filter(user=user, is_active=True).select_related('category')
        budget_data = [
            {
                'id': b.id,
                'category': b.category.name,
                'amount': float(b.amount),
                'spent': float(b.spent_amount),
                'percentage': b.spent_percentage,
                'is_over_budget': b.is_over_budget,
                'is_near_limit': b.is_near_limit,
                'period': b.period,
            }
            for b in budgets
        ]

        # Goals in progress
        goals = FinancialGoal.objects.filter(
            user=user, status__in=['in_progress', 'not_started']
        ).order_by('-priority')[:5]
        goal_data = [
            {
                'id': g.id,
                'name': g.name,
                'target': float(g.target_amount),
                'current': float(g.current_amount),
                'progress': g.progress_percentage,
                'deadline': g.deadline,
                'status': g.status,
            }
            for g in goals
        ]

        # Spending by category this month
        category_spending = (
            Expense.objects.filter(user=user, date__gte=month_start)
            .values('category__name', 'category__color')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        # Recent transactions
        recent_expenses = Expense.objects.filter(user=user).select_related('category', 'payment_method').order_by('-date', '-created_at')[:5]
        recent_income = Income.objects.filter(user=user).select_related('category').order_by('-date', '-created_at')[:5]

        return Response({
            'summary': {
                'monthly_income': float(monthly_income),
                'monthly_expenses': float(monthly_expenses),
                'balance': float(monthly_income - monthly_expenses),
                'income_change_pct': pct_change(monthly_income, last_income),
                'expense_change_pct': pct_change(monthly_expenses, last_expenses),
                'currency': user.currency,
            },
            'active_budgets': budget_data,
            'goals_in_progress': goal_data,
            'category_spending': list(category_spending),
            'recent_expenses': ExpenseSerializer(recent_expenses, many=True).data,
            'recent_income': IncomeSerializer(recent_income, many=True).data,
        })
