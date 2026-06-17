import urllib.parse
import random
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from .models import EmailVerification


# ── LOGIN ────────────────────────────────────────────────────────────────────
def login_view(request):
    """Handle standard username/email + password sign-in with verification check."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            # Check verification
            verification = getattr(user, 'verification', None)
            if verification and not verification.is_confirmed:
                logout(request)
                messages.error(request, 'Please verify your email address to log in.')
                return redirect(f"{reverse('verify')}?email={urllib.parse.quote(user.email)}")

            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'accounts/login.html')


# ── SIGNUP ───────────────────────────────────────────────────────────────────
def signup_view(request):
    """Handle user registration and send email confirmation code."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')

        UserModel = get_user_model()
        if UserModel.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'accounts/signup.html')

        if UserModel.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email address is already registered.')
            return render(request, 'accounts/signup.html')

        user = UserModel.objects.create_user(username=username, email=email, password=password)

        # Generate 6-digit confirmation code
        code = f"{random.randint(100000, 999999)}"
        EmailVerification.objects.create(user=user, code=code, is_confirmed=False)

        # Send confirmation email
        subject = 'Verify your DocSign Account'
        message = (
            f"Hi {username},\n\n"
            f"Thank you for registering. Your verification code is: {code}\n\n"
            f"Please enter this code on the verification page to complete your registration.\n\n"
            f"Best regards,\n"
            f"DocSign Team"
        )
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        except Exception:
            pass

        messages.success(request, 'Registration successful! A verification code has been sent to your email.')
        return redirect(f"{reverse('verify')}?email={urllib.parse.quote(email)}")

    return render(request, 'accounts/signup.html')


# ── VERIFY ───────────────────────────────────────────────────────────────────
def verify_view(request):
    """Verify the 6-digit confirmation code entered by the user."""
    if request.user.is_authenticated:
        return redirect('index')

    email = request.GET.get('email', '').strip()
    if not email:
        messages.error(request, 'Invalid verification request.')
        return redirect('login')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=email)
            verification = getattr(user, 'verification', None)
            if verification:
                if verification.is_confirmed:
                    messages.success(request, 'Account already verified. Please log in.')
                    return redirect('login')

                if verification.code == code:
                    verification.is_confirmed = True
                    verification.save()

                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, 'Your email has been verified! Welcome to DocSign.')
                    return redirect('index')
                else:
                    messages.error(request, 'Invalid verification code. Please try again.')
            else:
                messages.error(request, 'Verification record not found.')
        except UserModel.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')

    return render(request, 'accounts/verify.html', {'email': email})


# ── RESEND CODE ──────────────────────────────────────────────────────────────
def resend_code_view(request):
    """Generate, update, and resend the 6-digit confirmation code."""
    if request.user.is_authenticated:
        return redirect('index')

    email = request.GET.get('email', '').strip()
    if not email:
        messages.error(request, 'Invalid request.')
        return redirect('login')

    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(email__iexact=email)
        verification, created = EmailVerification.objects.get_or_create(user=user)

        if verification.is_confirmed:
            messages.success(request, 'Account already verified. Please log in.')
            return redirect('login')

        code = f"{random.randint(100000, 999999)}"
        verification.code = code
        verification.save()

        subject = 'Verify your DocSign Account'
        message = (
            f"Hi {user.username},\n\n"
            f"Your new verification code is: {code}\n\n"
            f"Please enter this code on the verification page to complete your registration.\n\n"
            f"Best regards,\n"
            f"DocSign Team"
        )
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        except Exception:
            pass

        messages.success(request, 'A new verification code has been sent to your email.')
    except UserModel.DoesNotExist:
        messages.error(request, 'User with this email does not exist.')

    return redirect(f"{reverse('verify')}?email={urllib.parse.quote(email)}")


# ── LOGOUT ───────────────────────────────────────────────────────────────────
def logout_view(request):
    """Log the user out."""
    logout(request)
    return redirect('login')


# ── GOOGLE OAUTH ─────────────────────────────────────────────────────────────
def google_login(request):
    """Redirect user to Google's OAuth2 authorization server."""
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        messages.error(request, 'Google Login is not configured. Please define GOOGLE_CLIENT_ID in your environment.')
        return redirect('login')

    redirect_uri = request.build_absolute_uri(reverse('google_callback'))

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    authorization_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(authorization_url)


def google_callback(request):
    """Handle Google authorization code exchange, auto-confirm user, and log in."""
    code = request.GET.get('code')
    if not code:
        error = request.GET.get('error', 'Google authentication failed.')
        messages.error(request, error)
        return redirect('login')

    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))

    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    try:
        token_res = requests.post(token_url, data=token_data, timeout=10)
        token_res.raise_for_status()
        tokens = token_res.json()
        access_token = tokens.get('access_token')

        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_res = requests.get(userinfo_url, headers=headers, timeout=10)
        userinfo_res.raise_for_status()
        userinfo = userinfo_res.json()

    except requests.RequestException as e:
        messages.error(request, f'Failed to retrieve credentials from Google: {e}')
        return redirect('login')

    email = userinfo.get('email')
    name = userinfo.get('name') or userinfo.get('given_name', '')

    if not email:
        messages.error(request, 'Google account email address not provided.')
        return redirect('login')

    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(email__iexact=email)

        # Auto-verify for Google account
        verification, created = EmailVerification.objects.get_or_create(user=user)
        if not verification.is_confirmed:
            verification.is_confirmed = True
            verification.save()

    except UserModel.DoesNotExist:
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while UserModel.objects.filter(username__iexact=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = UserModel.objects.create_user(username=username, email=email)
        user.first_name = name
        user.save()

        # Google users are verified by default
        EmailVerification.objects.create(user=user, code='000000', is_confirmed=True)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('index')
