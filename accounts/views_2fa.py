"""
#20 Two-Factor Authentication views using django-otp TOTP.
"""
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django_otp.plugins.otp_totp.models import TOTPDevice


@login_required
def setup_2fa(request):
    """Show QR code for the user to scan with their authenticator app."""
    # Get or create a device
    device, created = TOTPDevice.objects.get_or_create(
        user=request.user,
        defaults={'name': 'default', 'confirmed': False}
    )

    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            messages.success(request, '2FA enabled successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    # Generate QR code as base64 image
    otp_url = device.config_url
    qr = qrcode.make(otp_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'accounts/2fa_setup.html', {
        'device': device,
        'qr_b64': qr_b64,
        'is_confirmed': device.confirmed,
    })


@login_required
def disable_2fa(request):
    """Disable 2FA for the current user."""
    if request.method == 'POST':
        TOTPDevice.objects.filter(user=request.user).delete()
        messages.success(request, '2FA has been disabled.')
        return redirect('profile')
    return render(request, 'accounts/2fa_disable.html')
