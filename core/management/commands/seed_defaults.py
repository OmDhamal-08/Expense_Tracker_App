from django.core.management.base import BaseCommand
from core.models import Category, PaymentMethod


class Command(BaseCommand):
    help = 'Seed default categories and payment methods'

    def handle(self, *args, **options):
        expense_categories = [
            ('Food & Dining', 'fa-utensils', '#e74c3c'),
            ('Transport', 'fa-bus', '#3498db'),
            ('Shopping', 'fa-shopping-bag', '#9b59b6'),
            ('Bills & Utilities', 'fa-bolt', '#f39c12'),
            ('Entertainment', 'fa-film', '#e91e63'),
            ('Health', 'fa-heartbeat', '#2ecc71'),
            ('Education', 'fa-graduation-cap', '#1abc9c'),
            ('Housing', 'fa-home', '#34495e'),
            ('Travel', 'fa-plane', '#00bcd4'),
            ('Clothing', 'fa-tshirt', '#ff9800'),
            ('Vehicle', 'fa-car', '#795548'),
            ('Kids', 'fa-baby', '#ff5722'),
            ('Pets', 'fa-paw', '#8bc34a'),
            ('Fitness', 'fa-dumbbell', '#673ab7'),
            ('Other', 'fa-tag', '#95a5a6'),
        ]

        income_categories = [
            ('Salary', 'fa-briefcase', '#27ae60'),
            ('Freelance', 'fa-laptop-code', '#2980b9'),
            ('Investment', 'fa-chart-line', '#8e44ad'),
            ('Gift', 'fa-gift', '#d35400'),
            ('Rental', 'fa-home', '#16a085'),
            ('Other Income', 'fa-wallet', '#7f8c8d'),
        ]

        payment_methods = [
            ('Cash', 'fa-money-bill'),
            ('Credit Card', 'fa-credit-card'),
            ('Debit Card', 'fa-credit-card'),
            ('UPI', 'fa-mobile-alt'),
            ('Bank Transfer', 'fa-university'),
            ('Wallet', 'fa-wallet'),
        ]

        for name, icon, color in expense_categories:
            Category.objects.get_or_create(
                name=name, type='expense', user=None,
                defaults={'icon': icon, 'color': color}
            )

        for name, icon, color in income_categories:
            Category.objects.get_or_create(
                name=name, type='income', user=None,
                defaults={'icon': icon, 'color': color}
            )

        for name, icon in payment_methods:
            PaymentMethod.objects.get_or_create(
                name=name, user=None,
                defaults={'icon': icon}
            )

        self.stdout.write(self.style.SUCCESS(
            'Default categories and payment methods seeded.'
        ))
