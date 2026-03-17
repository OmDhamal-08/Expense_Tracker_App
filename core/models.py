from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from taggit.managers import TaggableManager


class Category(models.Model):
    TYPE_CHOICES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    color = models.CharField(max_length=7, default='#4361ee')
    icon = models.CharField(max_length=50, default='fa-tag')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = ['name', 'type', 'user']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    @property
    def is_predefined(self):
        return self.user is None


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-money-bill')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payment_methods'
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default and self.user:
            PaymentMethod.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)





class Expense(models.Model):
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date = models.DateField(default=timezone.now)
    time = models.TimeField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    description = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='receipts/%Y/%m/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_tax_deductible = models.BooleanField(default=False)
    recurrence = models.CharField(
        max_length=10, choices=RECURRENCE_CHOICES, default='none'
    )
    recurrence_end_date = models.DateField(null=True, blank=True)
    tags = TaggableManager(blank=True)  # #4 Tags
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description or self.category} - {self.amount}"


class Income(models.Model):
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incomes'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes'
    )
    description = models.TextField(blank=True)
    recurrence = models.CharField(
        max_length=10, choices=RECURRENCE_CHOICES, default='none'
    )
    recurrence_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.source or self.category} - {self.amount}"


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField(default=timezone.now)
    alert_threshold = models.IntegerField(
        default=80,
        validators=[MinValueValidator(1)]
    )
    rollover = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'category', 'period']

    def __str__(self):
        return f"{self.category.name} - {self.amount}/{self.get_period_display()}"

    @property
    def spent_amount(self):
        from datetime import timedelta
        today = timezone.now().date()

        if self.period == 'weekly':
            start = today - timedelta(days=today.weekday())
        elif self.period == 'monthly':
            start = today.replace(day=1)
        else:
            start = today.replace(month=1, day=1)

        return self.category.expenses.filter(
            user=self.user,
            date__gte=start,
            date__lte=today
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def spent_percentage(self):
        if self.amount == 0:
            return 0
        return min(round((self.spent_amount / self.amount) * 100, 1), 100)

    @property
    def is_over_budget(self):
        return self.spent_amount > self.amount

    @property
    def is_near_limit(self):
        return self.spent_percentage >= self.alert_threshold and not self.is_over_budget


class FinancialGoal(models.Model):
    TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('debt', 'Debt Repayment'),
        ('purchase', 'Major Purchase'),
        ('emergency', 'Emergency Fund'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    name = models.CharField(max_length=200)
    goal_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='savings')
    target_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(round((self.current_amount / self.target_amount) * 100, 1), 100)

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, 0)


class Notification(models.Model):
    TYPE_CHOICES = [
        ('budget_warning', 'Budget Warning'),
        ('budget_exceeded', 'Budget Exceeded'),
        ('goal_milestone', 'Goal Milestone'),
        ('goal_completed', 'Goal Completed'),
        ('reminder', 'Reminder'),
        ('info', 'Information'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
