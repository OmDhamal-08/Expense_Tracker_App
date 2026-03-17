from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views.auth import RegisterView, LoginView, LogoutView, ProfileView
from api.views.transactions import (
    ExpenseListCreateView, ExpenseDetailView,
    IncomeListCreateView, IncomeDetailView,
)
from api.views.categories import (
    CategoryListCreateView, CategoryDetailView,
    PaymentMethodListCreateView, PaymentMethodDetailView,
)
from api.views.planning import (
    BudgetListCreateView, BudgetDetailView,
    GoalListCreateView, GoalDetailView,
)
from api.views.dashboard import DashboardView
from api.views.exports import ExportCSVView, ExportPDFView, ExportJSONView
from api.views.stats import MonthlyStatsView, NotificationListView, NotificationMarkReadView

app_name = 'api'

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Expenses
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),

    # Income
    path('income/', IncomeListCreateView.as_view(), name='income-list'),
    path('income/<int:pk>/', IncomeDetailView.as_view(), name='income-detail'),

    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # Payment Methods
    path('payment-methods/', PaymentMethodListCreateView.as_view(), name='payment-method-list'),
    path('payment-methods/<int:pk>/', PaymentMethodDetailView.as_view(), name='payment-method-detail'),

    # Budgets
    path('budgets/', BudgetListCreateView.as_view(), name='budget-list'),
    path('budgets/<int:pk>/', BudgetDetailView.as_view(), name='budget-detail'),

    # Financial Goals
    path('goals/', GoalListCreateView.as_view(), name='goal-list'),
    path('goals/<int:pk>/', GoalDetailView.as_view(), name='goal-detail'),

    # Exports (CSV / PDF / JSON)
    path('export/csv/', ExportCSVView.as_view(), name='export-csv'),
    path('export/pdf/', ExportPDFView.as_view(), name='export-pdf'),
    path('export/json/', ExportJSONView.as_view(), name='export-json'),

    # Stats & Notifications (New)
    path('stats/monthly/', MonthlyStatsView.as_view(), name='stats-monthly'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),

    # Swagger Docs (New)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
]
