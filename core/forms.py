from django import forms
from django.db.models import Q
from .models import (
    Category, PaymentMethod, Expense, Income,
    Budget, FinancialGoal
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'color', 'icon', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    ICON_CHOICES = [
        ('fa-utensils', 'Food & Dining'),
        ('fa-bus', 'Transport'),
        ('fa-shopping-bag', 'Shopping'),
        ('fa-file-invoice-dollar', 'Bills'),
        ('fa-film', 'Entertainment'),
        ('fa-heartbeat', 'Health'),
        ('fa-graduation-cap', 'Education'),
        ('fa-home', 'Housing'),
        ('fa-briefcase', 'Salary'),
        ('fa-laptop-code', 'Freelance'),
        ('fa-chart-line', 'Investment'),
        ('fa-gift', 'Gift'),
        ('fa-piggy-bank', 'Savings'),
        ('fa-tag', 'Other'),
        ('fa-gamepad', 'Gaming'),
        ('fa-plane', 'Travel'),
        ('fa-tshirt', 'Clothing'),
        ('fa-car', 'Vehicle'),
        ('fa-bolt', 'Utilities'),
        ('fa-baby', 'Kids'),
        ('fa-paw', 'Pets'),
        ('fa-dumbbell', 'Fitness'),
        ('fa-wallet', 'Miscellaneous'),
    ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'] = forms.ChoiceField(
            choices=self.ICON_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        if user:
            self.fields['parent'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True),
                parent__isnull=True, is_active=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = 'No parent (top-level)'


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name', 'icon', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment method name'}),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    ICON_CHOICES = [
        ('fa-money-bill', 'Cash'),
        ('fa-credit-card', 'Credit Card'),
        ('fa-university', 'Bank Transfer'),
        ('fa-mobile-alt', 'UPI / Mobile'),
        ('fa-wallet', 'Wallet'),
        ('fa-coins', 'Coins'),
        ('fa-exchange-alt', 'Transfer'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'] = forms.ChoiceField(
            choices=self.ICON_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select'})
        )





class ExpenseForm(forms.ModelForm):
    # #4 Tags — comma-separated
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. vacation, food, work (comma-separated)',
        }),
        help_text='Separate tags with commas.'
    )

    class Meta:
        model = Expense
        fields = [
            'amount', 'date', 'time', 'category', 'payment_method',
            'description', 'receipt', 'location',
            'is_tax_deductible', 'recurrence', 'recurrence_end_date', 'tags'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'is_tax_deductible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence': forms.Select(attrs={'class': 'form-select'}),
            'recurrence_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True),
                type='expense', is_active=True
            )
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
                Q(user=user) | Q(user__isnull=True),
                is_active=True
            )

            default_pm = PaymentMethod.objects.filter(user=user, is_default=True).first()
            if default_pm and not self.instance.pk:
                self.fields['payment_method'].initial = default_pm.pk


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'amount', 'date', 'source', 'category',
            'description', 'recurrence', 'recurrence_end_date'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Company Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'recurrence': forms.Select(attrs={'class': 'form-select'}),
            'recurrence_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True),
                type='income', is_active=True
            )


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'alert_threshold', 'rollover']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'rollover': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True),
                type='expense', is_active=True
            )


class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = [
            'name', 'goal_type', 'target_amount', 'current_amount',
            'deadline', 'priority', 'status', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Goal name'}),
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }
