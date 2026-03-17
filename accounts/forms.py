from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""
    
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'currency', 'timezone', 
                 'language', 'theme', 'profile_picture', 'phone_number', 
                 'address', 'date_of_birth', 'email_notifications', 
                 'sms_notifications', 'budget_alerts', 'bill_reminders')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        
        # Remove password field from form
        self.fields.pop('password', None)

class LoginForm(forms.Form):
    """Login form."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )
    remember_me = forms.BooleanField(required=False)

class PasswordResetRequestForm(forms.Form):
    """Password reset request form."""
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(_("No active account found with this email address."))
        return email

class PasswordResetConfirmForm(forms.Form):
    """Password reset confirm form."""
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('new_password2', _("The two password fields didn't match."))
        
        return cleaned_data

class EmailChangeForm(forms.Form):
    """Email change form."""
    new_email = forms.EmailField(
        label=_("New email address"),
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    confirm_email = forms.EmailField(
        label=_("Confirm new email address"),
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    current_password = forms.CharField(
        label=_("Current password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
        strip=False,
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email")
        confirm_email = cleaned_data.get("confirm_email")
        current_password = cleaned_data.get("current_password")
        
        if new_email and confirm_email and new_email != confirm_email:
            self.add_error('confirm_email', _("The two email fields didn't match."))
        
        if current_password and not self.user.check_password(current_password):
            self.add_error('current_password', _("Your current password was entered incorrectly."))
        
        if new_email and User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            self.add_error('new_email', _("A user with this email already exists."))
        
        return cleaned_data