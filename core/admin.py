from django.contrib import admin
from .models import (
    Category, PaymentMethod, Expense, Income,
    Budget, FinancialGoal, Notification
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'color', 'icon', 'user', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'user', 'is_default', 'is_active')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name',)





@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date', 'category', 'payment_method', 'is_tax_deductible')
    list_filter = ('date', 'category', 'payment_method', 'is_tax_deductible')
    search_fields = ('description', 'location')
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date', 'source', 'category')
    list_filter = ('date', 'category')
    search_fields = ('source', 'description')
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'period', 'is_active')
    list_filter = ('period', 'is_active')


@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'goal_type', 'target_amount', 'current_amount', 'status')
    list_filter = ('goal_type', 'status', 'priority')
    search_fields = ('name',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('title', 'message')
