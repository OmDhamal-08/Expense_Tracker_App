from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_2fa, views_extras

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('demo-login/', views.demo_login, name='demo_login'),  # One-click demo
    
    # Email verification
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    
    # Password management
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         views.password_reset_confirm, name='password_reset_confirm'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-email/', views.change_email, name='change_email'),
    path('confirm-email-change/<uidb64>/<token>/<new_email_b64>/',
         views.confirm_email_change, name='confirm_email_change'),
    
    # 2FA & Extras
    path('2fa/setup/', views_2fa.setup_2fa, name='setup_2fa'),
    path('2fa/disable/', views_2fa.disable_2fa, name='disable_2fa'),
    path('theme/', views_extras.toggle_theme, name='toggle_theme'),
    
    # Sessions
    path('terminate-session/', views.terminate_session, name='terminate_session'),
    path('terminate-all-sessions/', views.terminate_all_sessions, name='terminate_all_sessions'),
    
    # Account management
    path('delete-account/', views.delete_account, name='delete_account'),
    path('export-data/', views.export_data, name='export_data'),
    path('export-data-pdf/', views.export_data_pdf, name='export_data_pdf'),
]

# Include Django auth URLs for compatibility
urlpatterns += [
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
]