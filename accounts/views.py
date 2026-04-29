from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import logging
from django_ratelimit.decorators import ratelimit

from .models import User, UserSession
from .forms import (CustomUserCreationForm, CustomUserChangeForm, LoginForm,
                   PasswordResetRequestForm, PasswordResetConfirmForm,
                   EmailChangeForm)

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get the client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Get user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

@csrf_protect
@ratelimit(key='ip', rate='5/m', block=True)
def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                if settings.DEBUG:
                    user.is_active = True
                    user.email_verified = True
                else:
                    user.is_active = True  # Changed from False to True so users can login immediately
                    user.email_verified = False
                user.save()
                
                if not settings.DEBUG:
                    send_verification_email(request, user)
                    messages.success(
                        request,
                        'Registration successful! Please check your email to verify your account.'
                    )
                else:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, 'Account created successfully!')
                    return redirect('dashboard')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def send_verification_email(request, user):
    """Send email verification link."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_url = request.build_absolute_uri(
        f'/accounts/verify-email/{uid}/{token}/'
    )
    
    subject = 'Verify Your Email Address'
    message = render_to_string('accounts/email/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
        'request': request,
    })
    
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=False,
    )
    logger.info(f"Verification email sent to {user.email}")

def verify_email(request, uidb64, token):
    """Verify email address."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        
        # Log the user in
        login(request, user)
        
        messages.success(request, 'Email verified successfully!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('home')

@csrf_protect
@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    """Custom login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(
                        request,
                        'Your account is inactive. Please contact support.'
                    )
                    return redirect('login')
                
                # Set session expiration
                if not remember_me:
                    request.session.set_expiry(0)  # Browser session
                
                login(request, user)
                
                # Track user session
                ip_address = get_client_ip(request)
                user_agent = get_user_agent(request)
                
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                
                # Update last login IP
                user.last_login_ip = ip_address
                user.last_login_device = user_agent[:255]
                user.save()
                
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def demo_login(request):
    """
    One-click demo login.
    Finds the pre-seeded demo user and logs them in instantly.
    If the demo account doesn't exist yet, seeds it first.
    """
    from django.core.management import call_command

    DEMO_EMAIL    = "demo@expensetracker.com"
    DEMO_PASSWORD = "Demo@1234"

    try:
        user = User.objects.get(email=DEMO_EMAIL)
    except User.DoesNotExist:
        # Auto-seed if never run before (e.g. fresh Render deploy)
        call_command("seed_demo")
        user = User.objects.get(email=DEMO_EMAIL)

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    messages.info(
        request,
        "👋 Welcome to the demo! You're exploring a pre-filled account with 6 months of sample data."
    )
    return redirect("dashboard")


def logout_view(request):
    """Custom logout view."""
    if request.user.is_authenticated:
        # Mark user session as inactive
        UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key
        ).update(is_active=False)
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    """User profile view."""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    # Get active sessions
    active_sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'active_sessions': active_sessions,
    })

@login_required
def change_password(request):
    """Change password view."""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Your current password was entered incorrectly.')
        elif new_password1 != new_password2:
            messages.error(request, 'The two password fields didn\'t match.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, request.user)  # Fixed this line
            
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    
    return render(request, 'accounts/change_password.html')

@login_required
def change_email(request):
    """Change email view."""
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            
            # Send verification email to new address
            send_email_change_confirmation(request, request.user, new_email)
            
            messages.success(
                request,
                'Please check your new email address for confirmation.'
            )
            return redirect('profile')
    else:
        form = EmailChangeForm(request.user)
    
    return render(request, 'accounts/change_email.html', {'form': form})

def send_email_change_confirmation(request, user, new_email):
    """Send email change confirmation."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    confirmation_url = request.build_absolute_uri(
        f'/accounts/confirm-email-change/{uid}/{token}/{urlsafe_base64_encode(force_bytes(new_email))}/'
    )
    
    subject = 'Confirm Your Email Change'
    message = render_to_string('accounts/email/change_email_confirmation.html', {
        'user': user,
        'new_email': new_email,
        'confirmation_url': confirmation_url,
        'request': request,
    })
    
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [new_email],
        html_message=message,
        fail_silently=False,
    )

@login_required
def confirm_email_change(request, uidb64, token, new_email_b64):
    """Confirm email change."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        new_email = force_str(urlsafe_base64_decode(new_email_b64))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        new_email = None
    
    if (user is not None and new_email is not None and 
        default_token_generator.check_token(user, token)):
        
        if User.objects.filter(email=new_email).exists():
            messages.error(request, 'This email is already in use.')
        else:
            user.email = new_email
            user.email_verified = True
            user.save()
            messages.success(request, 'Email changed successfully!')
        
        return redirect('profile')
    else:
        messages.error(request, 'Invalid confirmation link.')
        return redirect('home')

def password_reset_request(request):
    """Password reset request view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Send password reset email
            send_password_reset_email(request, user)
            
            messages.success(
                request,
                'Password reset link has been sent to your email.'
            )
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})

def send_password_reset_email(request, user):
    """Send password reset email."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    reset_url = request.build_absolute_uri(
        f'/accounts/password-reset-confirm/{uid}/{token}/'
    )
    
    subject = 'Reset Your Password'
    message = render_to_string('accounts/email/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url,
        'request': request,
    })
    
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=False,
    )

def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                
                messages.success(request, 'Password reset successfully!')
                return redirect('login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid password reset link.')
        return redirect('home')

@login_required
@require_POST
def terminate_session(request):
    """Terminate a user session."""
    session_id = request.POST.get('session_id')
    
    if session_id:
        session = get_object_or_404(
            UserSession,
            id=session_id,
            user=request.user
        )
        
        # Don't terminate current session
        if session.session_key != request.session.session_key:
            session.is_active = False
            session.save()
            messages.success(request, 'Session terminated successfully.')
        else:
            messages.error(request, 'Cannot terminate current session.')
    
    return redirect('profile')

@login_required
def terminate_all_sessions(request):
    """Terminate all user sessions except current."""
    UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).exclude(
        session_key=request.session.session_key
    ).update(is_active=False)
    
    messages.success(request, 'All other sessions terminated.')
    return redirect('profile')

@login_required
def delete_account(request):
    """Delete user account."""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if request.user.check_password(password):
            request.user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password.')
    
    return render(request, 'accounts/delete_account.html')

@login_required
def export_data(request):
    """Export ALL user data in JSON format."""
    from django.http import HttpResponse
    import json
    from datetime import datetime
    from core.models import Category, PaymentMethod, Expense, Income, Budget, FinancialGoal

    user = request.user

    expenses = Expense.objects.filter(user=user).select_related('category', 'payment_method')
    incomes = Income.objects.filter(user=user).select_related('category')
    categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True))
    payment_methods = PaymentMethod.objects.filter(Q(user=user) | Q(user__isnull=True))
    budgets = Budget.objects.filter(user=user).select_related('category')
    goals = FinancialGoal.objects.filter(user=user)

    data = {
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'currency': user.currency,
            'timezone': user.timezone,
            'language': user.language,
            'theme': user.theme,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'expenses': [
            {
                'amount': str(e.amount),
                'date': e.date.isoformat(),
                'time': e.time.isoformat() if e.time else None,
                'category': e.category.name if e.category else None,
                'payment_method': e.payment_method.name if e.payment_method else None,
                'description': e.description,
                'location': e.location,
                'is_tax_deductible': e.is_tax_deductible,
                'recurrence': e.recurrence,
            }
            for e in expenses
        ],
        'income': [
            {
                'amount': str(i.amount),
                'date': i.date.isoformat(),
                'source': i.source,
                'category': i.category.name if i.category else None,
                'description': i.description,
                'recurrence': i.recurrence,
            }
            for i in incomes
        ],
        'categories': [
            {
                'name': c.name,
                'type': c.type,
                'color': c.color,
                'icon': c.icon,
                'is_default': c.user is None,
            }
            for c in categories
        ],
        'payment_methods': [
            {
                'name': pm.name,
                'icon': pm.icon,
                'is_default_method': pm.is_default,
                'is_predefined': pm.user is None,
            }
            for pm in payment_methods
        ],
        'budgets': [
            {
                'category': b.category.name,
                'amount': str(b.amount),
                'period': b.period,
                'alert_threshold': b.alert_threshold,
                'is_active': b.is_active,
            }
            for b in budgets
        ],
        'goals': [
            {
                'name': g.name,
                'goal_type': g.goal_type,
                'target_amount': str(g.target_amount),
                'current_amount': str(g.current_amount),
                'deadline': g.deadline.isoformat() if g.deadline else None,
                'priority': g.priority,
                'status': g.status,
                'description': g.description,
            }
            for g in goals
        ],
        'sessions': list(UserSession.objects.filter(user=user).values(
            'ip_address', 'user_agent', 'created_at', 'last_activity', 'is_active'
        )),
        'export_date': datetime.now().isoformat(),
    }

    response = HttpResponse(
        json.dumps(data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="expense_tracker_data_{datetime.now().date()}.json"'
    return response


@login_required
def export_data_pdf(request):
    """Export ALL user data as a PDF report."""
    from io import BytesIO
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    from datetime import datetime
    from decimal import Decimal
    from django.db.models import Sum
    from core.models import Expense, Income, Budget, FinancialGoal

    user = request.user

    expenses = Expense.objects.filter(user=user).select_related('category', 'payment_method').order_by('-date')[:100]
    incomes = Income.objects.filter(user=user).select_related('category').order_by('-date')[:100]
    budgets = Budget.objects.filter(user=user, is_active=True).select_related('category')
    goals = FinancialGoal.objects.filter(user=user)

    total_expenses = Expense.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_income = Income.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or Decimal('0')

    currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
    sym = currency_symbols.get(user.currency, '$')

    html = render_to_string('accounts/pdf/data_export.html', {
        'user': user,
        'expenses': expenses,
        'incomes': incomes,
        'budgets': budgets,
        'goals': goals,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net': total_income - total_expenses,
        'sym': sym,
        'export_date': datetime.now(),
    })

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

    if pdf.err:
        return HttpResponse('PDF generation error', status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expense_tracker_report_{datetime.now().date()}.pdf"'
    return response