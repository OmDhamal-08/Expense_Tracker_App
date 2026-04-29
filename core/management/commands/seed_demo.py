"""
Management command: seed_demo

Creates (or resets) the demo user account with realistic sample data
so recruiters can explore the app without signing up.

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --reset   # wipe & re-seed
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from core.models import (
    Budget, Category, Expense, FinancialGoal,
    Income, Notification, PaymentMethod,
)

DEMO_EMAIL    = "demo@expensetracker.com"
DEMO_PASSWORD = "Demo@1234"

# ── Sample data ────────────────────────────────────────────

EXPENSE_CATEGORIES = [
    ("Food & Dining",    "#f72585", "fa-utensils"),
    ("Transport",        "#7209b7", "fa-bus"),
    ("Shopping",         "#3a0ca3", "fa-shopping-bag"),
    ("Bills & Utilities","#4361ee", "fa-bolt"),
    ("Entertainment",    "#4cc9f0", "fa-film"),
    ("Health",           "#2dc653", "fa-heartbeat"),
    ("Education",        "#f48c06", "fa-graduation-cap"),
    ("Travel",           "#e36414", "fa-plane"),
]

INCOME_CATEGORIES = [
    ("Salary",    "#06d6a0", "fa-briefcase"),
    ("Freelance", "#118ab2", "fa-laptop-code"),
    ("Investment","#ffd166", "fa-chart-line"),
]

PAYMENT_METHODS = [
    ("Cash",          "fa-money-bill"),
    ("Credit Card",   "fa-credit-card"),
    ("UPI / GPay",    "fa-mobile-alt"),
    ("Bank Transfer", "fa-university"),
]

GOALS = [
    ("Emergency Fund",  "emergency", 50000,  32000, "high",   "in_progress"),
    ("New Laptop",      "purchase",  80000,  15000, "medium", "in_progress"),
    ("Vacation to Goa", "savings",   30000,  30000, "low",    "completed"),
]

# (description, category_name, amount_range)
EXPENSE_SEEDS = [
    ("Lunch at Cafe",         "Food & Dining",    (120, 350)),
    ("Groceries",             "Food & Dining",    (500, 1800)),
    ("Uber ride",             "Transport",        (80,  250)),
    ("Monthly metro pass",    "Transport",        (500, 500)),
    ("Amazon order",          "Shopping",         (300, 3000)),
    ("Electricity bill",      "Bills & Utilities",(800, 1500)),
    ("Internet bill",         "Bills & Utilities",(600, 600)),
    ("Movie tickets",         "Entertainment",    (250, 600)),
    ("Spotify premium",       "Entertainment",    (99,  99)),
    ("Gym membership",        "Health",           (700, 1500)),
    ("Doctor consultation",   "Health",           (500, 1000)),
    ("Online course",         "Education",        (999, 4999)),
    ("Hotel booking",         "Travel",           (2000,7000)),
]

INCOME_SEEDS = [
    ("Monthly salary",   "Salary",    (45000, 75000)),
    ("Freelance project","Freelance", (5000,  25000)),
    ("Dividend income",  "Investment",(1000,  5000)),
]


class Command(BaseCommand):
    help = "Seed the demo user with realistic sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete all existing demo data before seeding"
        )

    def handle(self, *args, **options):
        self.stdout.write("==> Seeding demo user ...")
        user = self._get_or_create_demo_user(options["reset"])
        categories = self._seed_categories(user)
        methods     = self._seed_payment_methods(user)
        self._seed_expenses(user, categories, methods)
        self._seed_incomes(user, categories)
        self._seed_budgets(user, categories)
        self._seed_goals(user)
        self._seed_notifications(user)
        self.stdout.write(self.style.SUCCESS(
            f"\nDone!  Login: {DEMO_EMAIL}  /  Password: {DEMO_PASSWORD}"
        ))

    # ── Helpers ──────────────────────────────────

    def _get_or_create_demo_user(self, reset):
        user, created = User.objects.get_or_create(
            email=DEMO_EMAIL,
            defaults={
                "first_name": "Demo",
                "last_name": "User",
                "is_active": True,
                "email_verified": True,
                "onboarding_completed": True,
                "has_dismissed_onboarding": True,
                "currency": "INR",
            }
        )
        user.set_password(DEMO_PASSWORD)
        user.save()

        if reset and not created:
            self.stdout.write("  -> Resetting demo data ...")
            Expense.objects.filter(user=user).delete()
            Income.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            FinancialGoal.objects.filter(user=user).delete()
            Notification.objects.filter(user=user).delete()
            Category.objects.filter(user=user).delete()
            PaymentMethod.objects.filter(user=user).delete()

        action = "Created" if created else "Found"
        self.stdout.write(f"  [user] {action} demo user: {DEMO_EMAIL}")
        return user

    def _seed_categories(self, user):
        cats = {}
        for name, color, icon in EXPENSE_CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, type="expense", user=user,
                defaults={"color": color, "icon": icon}
            )
            cats[name] = cat
        for name, color, icon in INCOME_CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, type="income", user=user,
                defaults={"color": color, "icon": icon}
            )
            cats[name] = cat
        self.stdout.write(f"  [cat]  {len(cats)} categories seeded")
        return cats

    def _seed_payment_methods(self, user):
        methods = []
        for i, (name, icon) in enumerate(PAYMENT_METHODS):
            method, _ = PaymentMethod.objects.get_or_create(
                name=name, user=user,
                defaults={"icon": icon, "is_default": (i == 0)}
            )
            methods.append(method)
        self.stdout.write(f"  [pay]  {len(methods)} payment methods seeded")
        return methods

    def _seed_expenses(self, user, categories, methods):
        today = timezone.now().date()
        count = 0
        random.seed(42)  # reproducible data

        for days_back in range(180):  # last 6 months
            d = today - timedelta(days=days_back)
            # 0–3 expenses per day
            n = random.choices([0, 1, 2, 3], weights=[40, 35, 15, 10])[0]
            for _ in range(n):
                desc, cat_name, (lo, hi) = random.choice(EXPENSE_SEEDS)
                cat = categories.get(cat_name)
                if not cat:
                    continue
                amount = Decimal(str(random.randint(lo, hi)))
                method = random.choice(methods)
                Expense.objects.create(
                    user=user, category=cat, payment_method=method,
                    amount=amount, date=d, description=desc
                )
                count += 1

        self.stdout.write(f"  [exp]  {count} expenses seeded")

    def _seed_incomes(self, user, categories):
        today = timezone.now().date()
        count = 0
        random.seed(99)

        for months_back in range(6):
            salary_day = today.replace(day=1) - timedelta(days=months_back * 30)
            for desc, cat_name, (lo, hi) in INCOME_SEEDS:
                cat = categories.get(cat_name)
                if not cat:
                    continue
                # salary every month; freelance / investment randomly
                if cat_name == "Salary" or random.random() > 0.4:
                    amount = Decimal(str(random.randint(lo, hi)))
                    Income.objects.create(
                        user=user, category=cat, amount=amount,
                        date=salary_day, source=desc, description=desc,
                    )
                    count += 1

        self.stdout.write(f"  [inc]  {count} income records seeded")

    def _seed_budgets(self, user, categories):
        budget_defs = [
            ("Food & Dining",     Decimal("8000"),  "monthly", 80),
            ("Transport",         Decimal("3000"),  "monthly", 75),
            ("Shopping",          Decimal("5000"),  "monthly", 80),
            ("Bills & Utilities", Decimal("4000"),  "monthly", 90),
            ("Entertainment",     Decimal("2000"),  "monthly", 70),
            ("Health",            Decimal("3000"),  "monthly", 80),
        ]
        count = 0
        for cat_name, amount, period, threshold in budget_defs:
            cat = categories.get(cat_name)
            if not cat:
                continue
            Budget.objects.get_or_create(
                user=user, category=cat, period=period,
                defaults={
                    "amount": amount,
                    "alert_threshold": threshold,
                    "start_date": date.today().replace(day=1),
                }
            )
            count += 1
        self.stdout.write(f"  [bud]  {count} budgets seeded")

    def _seed_goals(self, user):
        count = 0
        for name, gtype, target, current, priority, status in GOALS:
            FinancialGoal.objects.get_or_create(
                user=user, name=name,
                defaults={
                    "goal_type": gtype,
                    "target_amount": Decimal(str(target)),
                    "current_amount": Decimal(str(current)),
                    "priority": priority,
                    "status": status,
                    "deadline": date.today() + timedelta(days=180),
                }
            )
            count += 1
        self.stdout.write(f"  [goal] {count} goals seeded")

    def _seed_notifications(self, user):
        notifs = [
            ("Budget Alert: Food & Dining",
             "You've used 87% of your monthly food budget.",
             "budget_warning"),
            ("Goal Milestone: Emergency Fund",
             "You're 64% of the way to your Emergency Fund goal!",
             "goal_milestone"),
            ("Welcome to the Demo!",
             "This is a pre-filled demo account. Explore the dashboard, reports, budgets and goals.",
             "info"),
        ]
        Notification.objects.filter(user=user).delete()
        for title, msg, ntype in notifs:
            Notification.objects.create(
                user=user, title=title, message=msg, type=ntype
            )
        self.stdout.write(f"  [notf] {len(notifs)} notifications seeded")
