"""
Tests for core/models.py

Covers:
- Category model (predefined vs user-owned, unique_together)
- PaymentMethod model (default-switching logic)
- Expense model (string repr, ordering)
- Income model (string repr)
- Budget model (spent_amount, spent_percentage, is_over_budget, is_near_limit)
- FinancialGoal model (progress_percentage, remaining_amount)
- Notification model (string repr)
"""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from core.models import (
    Budget, Category, Expense, FinancialGoal,
    Income, Notification, PaymentMethod,
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_user(email="test@example.com", password="TestPass123!"):
    return User.objects.create_user(email=email, password=password)


def make_category(user=None, name="Food", cat_type="expense"):
    return Category.objects.create(name=name, type=cat_type, user=user)


def make_expense(user, category, amount="50.00"):
    return Expense.objects.create(
        user=user,
        category=category,
        amount=Decimal(amount),
        date=timezone.now().date(),
    )


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────

class CategoryModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_str_representation(self):
        cat = make_category(user=self.user)
        self.assertIn("Food", str(cat))
        self.assertIn("Expense", str(cat))

    def test_predefined_category_has_no_user(self):
        cat = make_category(user=None)
        self.assertTrue(cat.is_predefined)

    def test_user_category_is_not_predefined(self):
        cat = make_category(user=self.user)
        self.assertFalse(cat.is_predefined)

    def test_unique_together_constraint(self):
        """Same name + type + user should raise IntegrityError."""
        make_category(user=self.user, name="Rent", cat_type="expense")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name="Rent", type="expense", user=self.user
            )

    def test_is_active_default_true(self):
        cat = make_category(user=self.user)
        self.assertTrue(cat.is_active)


# ─────────────────────────────────────────────
# PaymentMethod
# ─────────────────────────────────────────────

class PaymentMethodModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def _make_method(self, name, is_default=False):
        return PaymentMethod.objects.create(
            name=name, user=self.user, is_default=is_default
        )

    def test_str_representation(self):
        method = self._make_method("Cash")
        self.assertEqual(str(method), "Cash")

    def test_only_one_default_per_user(self):
        """Setting a new default should unset the previous one."""
        m1 = self._make_method("Cash", is_default=True)
        m2 = self._make_method("Card", is_default=True)
        m1.refresh_from_db()
        self.assertFalse(m1.is_default)
        self.assertTrue(m2.is_default)


# ─────────────────────────────────────────────
# Expense
# ─────────────────────────────────────────────

class ExpenseModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category(user=self.user)

    def test_str_representation_with_description(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("100.00"),
            date=timezone.now().date(),
            description="Groceries",
        )
        self.assertIn("Groceries", str(expense))

    def test_str_representation_without_description(self):
        expense = make_expense(self.user, self.category)
        self.assertIn("50.00", str(expense))

    def test_ordering_most_recent_first(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        e1 = make_expense(self.user, self.category, "10.00")
        e2 = Expense.objects.create(
            user=self.user, category=self.category,
            amount=Decimal("20.00"), date=yesterday
        )
        expenses = list(Expense.objects.filter(user=self.user))
        self.assertEqual(expenses[0], e1)  # most recent first


# ─────────────────────────────────────────────
# Income
# ─────────────────────────────────────────────

class IncomeModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category(user=self.user, cat_type="income")

    def test_str_with_source(self):
        income = Income.objects.create(
            user=self.user, category=self.category,
            amount=Decimal("3000.00"), date=timezone.now().date(),
            source="Salary",
        )
        self.assertIn("Salary", str(income))


# ─────────────────────────────────────────────
# Budget
# ─────────────────────────────────────────────

class BudgetModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category(user=self.user)
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("500.00"),
            period="monthly",
            alert_threshold=80,
        )

    def test_str_representation(self):
        self.assertIn("500", str(self.budget))
        self.assertIn("Monthly", str(self.budget))

    def test_spent_amount_is_zero_when_no_expenses(self):
        self.assertEqual(self.budget.spent_amount, 0)

    def test_spent_amount_counts_current_month_expenses(self):
        make_expense(self.user, self.category, "200.00")
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.spent_amount, Decimal("200.00"))

    def test_spent_percentage(self):
        make_expense(self.user, self.category, "250.00")
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.spent_percentage, 50.0)

    def test_is_over_budget_false(self):
        make_expense(self.user, self.category, "400.00")
        self.assertFalse(self.budget.is_over_budget)

    def test_is_over_budget_true(self):
        make_expense(self.user, self.category, "600.00")
        self.assertTrue(self.budget.is_over_budget)

    def test_is_near_limit_true(self):
        # 80% of 500 = 400
        make_expense(self.user, self.category, "420.00")
        self.assertTrue(self.budget.is_near_limit)

    def test_is_near_limit_false_when_under_threshold(self):
        make_expense(self.user, self.category, "100.00")
        self.assertFalse(self.budget.is_near_limit)

    def test_spent_percentage_capped_at_100(self):
        make_expense(self.user, self.category, "1000.00")
        self.assertEqual(self.budget.spent_percentage, 100)


# ─────────────────────────────────────────────
# FinancialGoal
# ─────────────────────────────────────────────

class FinancialGoalModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def _make_goal(self, target=1000, current=0):
        return FinancialGoal.objects.create(
            user=self.user,
            name="Emergency Fund",
            goal_type="emergency",
            target_amount=Decimal(str(target)),
            current_amount=Decimal(str(current)),
        )

    def test_str_representation(self):
        goal = self._make_goal()
        self.assertEqual(str(goal), "Emergency Fund")

    def test_progress_percentage_zero(self):
        goal = self._make_goal(target=1000, current=0)
        self.assertEqual(goal.progress_percentage, 0)

    def test_progress_percentage_half(self):
        goal = self._make_goal(target=1000, current=500)
        self.assertEqual(goal.progress_percentage, 50.0)

    def test_progress_percentage_capped_at_100(self):
        goal = self._make_goal(target=1000, current=1500)
        self.assertEqual(goal.progress_percentage, 100)

    def test_remaining_amount(self):
        goal = self._make_goal(target=1000, current=300)
        self.assertEqual(goal.remaining_amount, Decimal("700"))

    def test_remaining_amount_zero_when_exceeded(self):
        goal = self._make_goal(target=1000, current=1500)
        self.assertEqual(goal.remaining_amount, 0)


# ─────────────────────────────────────────────
# Notification
# ─────────────────────────────────────────────

class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_str_representation(self):
        n = Notification.objects.create(
            user=self.user,
            title="Budget Warning",
            message="You are close to your limit.",
            type="budget_warning",
        )
        self.assertEqual(str(n), "Budget Warning")

    def test_is_read_defaults_to_false(self):
        n = Notification.objects.create(
            user=self.user,
            title="Info",
            message="Welcome!",
        )
        self.assertFalse(n.is_read)
