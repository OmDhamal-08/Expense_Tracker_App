import csv
import io
import json
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Category, PaymentMethod, Expense, Income,
    Budget, FinancialGoal, Notification,
)
from .forms import (
    CategoryForm, PaymentMethodForm,
    ExpenseForm, IncomeForm, BudgetForm, FinancialGoalForm,
)


def get_user_categories(user, cat_type=None):
    qs = Category.objects.filter(Q(user=user) | Q(user__isnull=True), is_active=True)
    if cat_type:
        qs = qs.filter(type=cat_type)
    return qs


def get_user_payment_methods(user):
    return PaymentMethod.objects.filter(Q(user=user) | Q(user__isnull=True), is_active=True)


def create_notification(user, title, message, notif_type='info', link=''):
    Notification.objects.create(
        user=user, title=title, message=message, type=notif_type, link=link
    )


def check_budget_alerts(user, expense):
    budgets = Budget.objects.filter(
        user=user, category=expense.category, is_active=True
    )
    for budget in budgets:
        pct = budget.spent_percentage
        if budget.is_over_budget:
            create_notification(
                user,
                f'Budget Exceeded: {budget.category.name}',
                f'You have exceeded your {budget.get_period_display().lower()} budget of {budget.amount} for {budget.category.name}.',
                'budget_exceeded',
                '/budgets/'
            )
        elif budget.is_near_limit:
            create_notification(
                user,
                f'Budget Warning: {budget.category.name}',
                f'You have used {pct}% of your {budget.get_period_display().lower()} budget for {budget.category.name}.',
                'budget_warning',
                '/budgets/'
            )


# ── Dashboard ──

@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    monthly_expenses = Expense.objects.filter(
        user=request.user, date__gte=month_start, date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    monthly_income = Income.objects.filter(
        user=request.user, date__gte=month_start, date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    balance = monthly_income - monthly_expenses

    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    prev_expenses = Expense.objects.filter(
        user=request.user, date__gte=prev_month_start, date__lte=prev_month_end
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    prev_income = Income.objects.filter(
        user=request.user, date__gte=prev_month_start, date__lte=prev_month_end
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    def pct_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(float((current - previous) / previous * 100), 1)

    expense_change = pct_change(monthly_expenses, prev_expenses)
    income_change = pct_change(monthly_income, prev_income)

    recent_expenses = Expense.objects.filter(
        user=request.user
    ).select_related('category', 'payment_method')[:5]

    recent_income = Income.objects.filter(
        user=request.user
    ).select_related('category')[:5]

    # Category-wise spending for current month
    category_spending = Expense.objects.filter(
        user=request.user, date__gte=month_start, date__lte=today
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Monthly trend (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        d = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        if d.month == 12:
            next_month = d.replace(year=d.year + 1, month=1, day=1)
        else:
            next_month = d.replace(month=d.month + 1, day=1)

        exp_total = Expense.objects.filter(
            user=request.user, date__gte=d, date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        inc_total = Income.objects.filter(
            user=request.user, date__gte=d, date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_data.append({
            'month': d.strftime('%b %Y'),
            'expenses': float(exp_total),
            'income': float(inc_total),
        })

    active_budgets = Budget.objects.filter(
        user=request.user, is_active=True
    ).select_related('category')[:5]

    active_goals = FinancialGoal.objects.filter(
        user=request.user
    ).exclude(status='completed')[:5]

    # Onboarding Logic
    onboarding_data = None
    if not request.user.has_dismissed_onboarding:
        steps = [
            {'id': 'cat', 'label': 'Add a custom category', 'done': Category.objects.filter(user=request.user).exists()},
            {'id': 'bud', 'label': 'Set a monthly budget', 'done': Budget.objects.filter(user=request.user).exists()},
            {'id': 'goal', 'label': 'Create a financial goal', 'done': FinancialGoal.objects.filter(user=request.user).exists()},
        ]
        done_count = sum(1 for s in steps if s['done'])
        percent = int((done_count / len(steps)) * 100)
        
        if done_count == len(steps) and not request.user.onboarding_completed:
            request.user.onboarding_completed = True
            request.user.save()

        onboarding_data = {
            'steps': steps,
            'percent': percent,
            'completed': request.user.onboarding_completed
        }

    context = {
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'balance': balance,
        'expense_change': expense_change,
        'income_change': income_change,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'category_spending': list(category_spending),
        'monthly_data': json.dumps(monthly_data),
        'active_budgets': active_budgets,
        'active_goals': active_goals,
        'onboarding': onboarding_data,
    }
    return render(request, 'core/dashboard.html', context)


# ── Categories ──

@login_required
def category_list(request):
    expense_categories = get_user_categories(request.user, 'expense')
    income_categories = get_user_categories(request.user, 'income')
    return render(request, 'core/categories/list.html', {
        'expense_categories': expense_categories,
        'income_categories': income_categories,
    })


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created.')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)
    return render(request, 'core/categories/form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)
    return render(request, 'core/categories/form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'core/confirm_delete.html', {
        'object': category, 'cancel_url': 'category_list'
    })


# ── Payment Methods ──

@login_required
def payment_method_list(request):
    methods = get_user_payment_methods(request.user)
    return render(request, 'core/payment_methods/list.html', {'methods': methods})


@login_required
def payment_method_create(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            method = form.save(commit=False)
            method.user = request.user
            method.save()
            messages.success(request, 'Payment method created.')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm()
    return render(request, 'core/payment_methods/form.html', {'form': form, 'title': 'Add Payment Method'})


@login_required
def payment_method_edit(request, pk):
    method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated.')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm(instance=method)
    return render(request, 'core/payment_methods/form.html', {'form': form, 'title': 'Edit Payment Method'})


@login_required
def payment_method_delete(request, pk):
    method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    if request.method == 'POST':
        method.delete()
        messages.success(request, 'Payment method deleted.')
        return redirect('payment_method_list')
    return render(request, 'core/confirm_delete.html', {
        'object': method, 'cancel_url': 'payment_method_list'
    })





# ── Expenses ──

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(
        user=request.user
    ).select_related('category', 'payment_method')

    # Filtering
    category_id = request.GET.get('category')
    payment_method_id = request.GET.get('payment_method')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    search = request.GET.get('search', '').strip()
    tax_deductible = request.GET.get('tax_deductible')
    sort_by = request.GET.get('sort', '-date')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if payment_method_id:
        expenses = expenses.filter(payment_method_id=payment_method_id)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)
    if search:
        expenses = expenses.filter(
            Q(description__icontains=search) |
            Q(location__icontains=search)    |
            Q(category__name__icontains=search)  # #2 category search
        )
    if tax_deductible == '1':
        expenses = expenses.filter(is_tax_deductible=True)

    # #4 Tag filter
    tag = request.GET.get('tag', '').strip()
    if tag:
        expenses = expenses.filter(tags__name__in=[tag])

    allowed_sorts = ['date', '-date', 'amount', '-amount', 'category__name', '-category__name']
    if sort_by in allowed_sorts:
        expenses = expenses.order_by(sort_by)

    paginator = Paginator(expenses, 20)
    page = request.GET.get('page')
    expenses = paginator.get_page(page)

    categories = get_user_categories(request.user, 'expense')
    payment_methods = get_user_payment_methods(request.user)

    return render(request, 'core/expenses/list.html', {
        'expenses': expenses,
        'categories': categories,
        'payment_methods': payment_methods,
        'current_filters': request.GET,
    })


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            check_budget_alerts(request.user, expense)
            messages.success(request, 'Expense added.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'core/expenses/form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'core/expenses/form.html', {'form': form, 'title': 'Edit Expense'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expense_list')
    return render(request, 'core/confirm_delete.html', {
        'object': expense, 'cancel_url': 'expense_list'
    })


# #3 Bulk delete expenses
@login_required
@require_POST
def expense_bulk_delete(request):
    ids = request.POST.getlist('ids')
    if ids:
        Expense.objects.filter(pk__in=ids, user=request.user).delete()
        messages.success(request, f'{len(ids)} expense(s) deleted.')
    else:
        messages.warning(request, 'No expenses selected.')
    return redirect('expense_list')


# ── Income ──

@login_required
def income_list(request):
    incomes = Income.objects.filter(
        user=request.user
    ).select_related('category')

    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', '-date')

    if category_id:
        incomes = incomes.filter(category_id=category_id)
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)
    if search:
        incomes = incomes.filter(
            Q(description__icontains=search) |
            Q(source__icontains=search)      |
            Q(category__name__icontains=search)  # #2 category search
        )

    allowed_sorts = ['date', '-date', 'amount', '-amount']
    if sort_by in allowed_sorts:
        incomes = incomes.order_by(sort_by)

    paginator = Paginator(incomes, 20)
    page = request.GET.get('page')
    incomes = paginator.get_page(page)

    categories = get_user_categories(request.user, 'income')

    return render(request, 'core/income/list.html', {
        'incomes': incomes,
        'categories': categories,
        'current_filters': request.GET,
    })


@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added.')
            return redirect('income_list')
    else:
        form = IncomeForm(user=request.user)
    return render(request, 'core/income/form.html', {'form': form, 'title': 'Add Income'})


@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated.')
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income, user=request.user)
    return render(request, 'core/income/form.html', {'form': form, 'title': 'Edit Income'})


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income deleted.')
        return redirect('income_list')
    return render(request, 'core/confirm_delete.html', {
        'object': income, 'cancel_url': 'income_list'
    })


# #3 Bulk delete income
@login_required
@require_POST
def income_bulk_delete(request):
    ids = request.POST.getlist('ids')
    if ids:
        Income.objects.filter(pk__in=ids, user=request.user).delete()
        messages.success(request, f'{len(ids)} income record(s) deleted.')
    else:
        messages.warning(request, 'No records selected.')
    return redirect('income_list')


# ── Budgets ──

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(
        user=request.user
    ).select_related('category')
    return render(request, 'core/budgets/list.html', {'budgets': budgets})


@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created.')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    return render(request, 'core/budgets/form.html', {'form': form, 'title': 'Create Budget'})


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated.')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, 'core/budgets/form.html', {'form': form, 'title': 'Edit Budget'})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')
    return render(request, 'core/confirm_delete.html', {
        'object': budget, 'cancel_url': 'budget_list'
    })


# ── Financial Goals ──

@login_required
def goal_list(request):
    goals = FinancialGoal.objects.filter(user=request.user)
    return render(request, 'core/goals/list.html', {'goals': goals})


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal created.')
            return redirect('goal_list')
    else:
        form = FinancialGoalForm()
    return render(request, 'core/goals/form.html', {'form': form, 'title': 'Create Goal'})


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST, instance=goal)
        if form.is_valid():
            old_pct = goal.progress_percentage
            goal = form.save()
            new_pct = goal.progress_percentage

            if new_pct >= 100 and old_pct < 100:
                goal.status = 'completed'
                goal.save()
                create_notification(
                    request.user,
                    f'Goal Completed: {goal.name}',
                    f'Congratulations! You have reached your goal of {goal.target_amount}.',
                    'goal_completed',
                    '/goals/'
                )
            elif new_pct >= 50 and old_pct < 50:
                create_notification(
                    request.user,
                    f'Goal Milestone: {goal.name}',
                    f'You are halfway to your goal. Keep going!',
                    'goal_milestone',
                    '/goals/'
                )

            messages.success(request, 'Goal updated.')
            return redirect('goal_list')
    else:
        form = FinancialGoalForm(instance=goal)
    return render(request, 'core/goals/form.html', {'form': form, 'title': 'Edit Goal'})


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goal_list')
    return render(request, 'core/confirm_delete.html', {
        'object': goal, 'cancel_url': 'goal_list'
    })


# ── Reports ──

@login_required
def reports(request):
    today = timezone.now().date()
    date_from = request.GET.get('date_from', today.replace(day=1).isoformat())
    date_to = request.GET.get('date_to', today.isoformat())

    expenses = Expense.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    )
    incomes = Income.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    )

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    category_breakdown = expenses.values(
        'category__name', 'category__color'
    ).annotate(total=Sum('amount')).order_by('-total')

    # Budget vs actual for current period
    budgets = Budget.objects.filter(user=request.user, is_active=True).select_related('category')
    budget_comparison = []
    for budget in budgets:
        spent = expenses.filter(category=budget.category).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        budget_comparison.append({
            'category': budget.category.name,
            'budgeted': float(budget.amount),
            'spent': float(spent),
            'color': budget.category.color,
        })

    # #9 Advanced Analytics – 12-month trend
    twelve_month_data = []
    for i in range(11, -1, -1):
        d = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        if d.month == 12:
            next_m = d.replace(year=d.year + 1, month=1, day=1)
        else:
            next_m = d.replace(month=d.month + 1, day=1)
        exp_t = Expense.objects.filter(user=request.user, date__gte=d, date__lt=next_m).aggregate(t=Sum('amount'))['t'] or 0
        inc_t = Income.objects.filter(user=request.user, date__gte=d, date__lt=next_m).aggregate(t=Sum('amount'))['t'] or 0
        savings = float(inc_t) - float(exp_t)
        savings_rate = round((savings / float(inc_t) * 100), 1) if inc_t else 0
        twelve_month_data.append({
            'month': d.strftime('%b %Y'),
            'expenses': float(exp_t),
            'income': float(inc_t),
            'savings': savings,
            'savings_rate': savings_rate,
        })

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net': total_income - total_expenses,
        'category_breakdown': list(category_breakdown),
        'budget_comparison': json.dumps(budget_comparison),
        'twelve_month_data': json.dumps(twelve_month_data),  # #9
        'savings_rate': round(float((total_income - total_expenses) / total_income * 100), 1) if total_income else 0,  # #9
    }
    return render(request, 'core/reports/index.html', context)


@login_required
def export_csv(request):
    today = timezone.now().date()
    date_from = request.GET.get('date_from') or today.replace(day=1).isoformat()
    date_to = request.GET.get('date_to') or today.isoformat()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description', 'Payment Method', 'Location', 'Tax Deductible'])

    expenses = Expense.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category', 'payment_method').order_by('-date')
    for e in expenses:
        writer.writerow([
            e.date, 'Expense',
            e.category.name if e.category else '',
            e.amount, e.description,
            e.payment_method.name if e.payment_method else '',
            e.location,
            'Yes' if e.is_tax_deductible else 'No',
        ])

    incomes = Income.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category').order_by('-date')
    for i in incomes:
        writer.writerow([
            i.date, 'Income',
            i.category.name if i.category else '',
            i.amount, i.description, '', '', '',
        ])

    return response


@login_required
def export_json(request):
    today = timezone.now().date()
    date_from = request.GET.get('date_from') or today.replace(day=1).isoformat()
    date_to = request.GET.get('date_to') or today.isoformat()

    expenses = Expense.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category', 'payment_method').order_by('-date')
    incomes = Income.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category').order_by('-date')

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    data = {
        'period': {'from': date_from, 'to': date_to},
        'summary': {
            'total_income': str(total_income),
            'total_expenses': str(total_expenses),
            'net': str(total_income - total_expenses),
        },
        'expenses': [
            {
                'date': e.date.isoformat(),
                'amount': str(e.amount),
                'category': e.category.name if e.category else None,
                'payment_method': e.payment_method.name if e.payment_method else None,
                'description': e.description,
                'location': e.location,
                'is_tax_deductible': e.is_tax_deductible,
            }
            for e in expenses
        ],
        'income': [
            {
                'date': i.date.isoformat(),
                'amount': str(i.amount),
                'source': i.source,
                'category': i.category.name if i.category else None,
                'description': i.description,
            }
            for i in incomes
        ],
    }

    response = HttpResponse(
        json.dumps(data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.json"'
    return response


@login_required
def export_pdf(request):
    from io import BytesIO
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa

    today = timezone.now().date()
    date_from = request.GET.get('date_from') or today.replace(day=1).isoformat()
    date_to = request.GET.get('date_to') or today.isoformat()

    expenses = Expense.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category', 'payment_method').order_by('-date')
    incomes = Income.objects.filter(
        user=request.user, date__gte=date_from, date__lte=date_to
    ).select_related('category').order_by('-date')

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    category_breakdown = expenses.values(
        'category__name', 'category__color'
    ).annotate(total=Sum('amount')).order_by('-total')

    currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': 'Rs.'}
    sym = currency_symbols.get(request.user.currency, '$')

    html = render_to_string('core/reports/pdf_report.html', {
        'user': request.user,
        'date_from': date_from,
        'date_to': date_to,
        'expenses': expenses,
        'incomes': incomes,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net': total_income - total_expenses,
        'category_breakdown': category_breakdown,
        'sym': sym,
    })

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result, encoding='utf-8')

    if pdf.err:
        return HttpResponse('PDF generation error', status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.pdf"'
    return response


# ── Notifications ──

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)[:50]
    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')


@login_required
@require_POST
def notification_clear(request):
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('notification_list')


@login_required
@require_POST
def onboarding_dismiss(request):
    request.user.has_dismissed_onboarding = True
    request.user.save()
    return HttpResponse(status=204)


# ── #22 AJAX Quick-Add Expense ──────────────────────────────────────────

@login_required
def quick_add_expense(request):
    """AJAX endpoint – returns JSON. Used by the dashboard quick-add modal."""
    import json as _json
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            form.save_m2m()  # save tags
            check_budget_alerts(request.user, expense)
            return HttpResponse(
                _json.dumps({'success': True, 'id': expense.pk, 'message': 'Expense added!'}),
                content_type='application/json'
            )
        else:
            errors = {f: e.get_json_data() for f, e in form.errors.items()}
            return HttpResponse(
                _json.dumps({'success': False, 'errors': errors}),
                content_type='application/json', status=400
            )
    # GET – return bare form HTML for modal injection
    form = ExpenseForm(user=request.user)
    return render(request, 'core/partials/quick_add_form.html', {'form': form})
