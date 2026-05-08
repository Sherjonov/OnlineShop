"""Accounts views with JSON API endpoints."""
import json
import random
import re

from django.contrib import messages
from django.contrib.auth import (
    authenticate, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    ChangeEmailForm, ChangePasswordForm, ChangeUsernameForm,
    LoginForm, OTPForm, ProfileForm, RegisterForm,
)
from .models import LoginActivity
from .services import consume_otp, issue_otp, peek_otp

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def log_activity(request, user, action):
    """Log user activity."""
    LoginActivity.objects.create(
        user=user,
        username_snapshot=user.username if user else '',
        full_name_snapshot=user.full_name if user else '',
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
    )


# ============ JSON API Endpoints ============

@require_POST
def api_login(request):
    """JSON API for login."""
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return JsonResponse({'ok': False, 'error': 'Username va parol kerak'}, status=400)
    
    user = authenticate(request, username=username, password=password)
    if user is None:
        # Log failed attempt
        LoginActivity.objects.create(
            user=None,
            username_snapshot=username,
            full_name_snapshot='',
            action=LoginActivity.FAILED,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
        return JsonResponse({'ok': False, 'error': 'Login yoki parol xato'}, status=401)
    
    auth_login(request, user, backend='accounts.backends.UsernameOrEmailBackend')
    log_activity(request, user, LoginActivity.LOGIN)
    
    return JsonResponse({
        'ok': True,
        'user': {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
        },
        'is_admin': user.is_admin,
    })


@require_POST
def api_register(request):
    """JSON API for registration - sends OTP."""
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    
    if not first_name or not username or not email or not password:
        return JsonResponse({'ok': False, 'error': 'Barcha maydonlar kerak'}, status=400)
    if phone and not re.fullmatch(r"\d{7,15}", phone):
        return JsonResponse({'ok': False, 'error': 'Telefon faqat raqamlardan iborat bo\'lsin'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'ok': False, 'error': 'Bu username band'}, status=400)
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({'ok': False, 'error': 'Bu email band'}, status=400)
    
    # Generate OTP and store in session
    code = str(random.randint(100000, 999999))
    request.session['otp_register'] = {
        'code': code,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'phone': phone,
        'password': password,
        'created_at': timezone.now().isoformat(),
    }
    request.session.modified = True
    
    # In production, send email here
    # For demo, we return the code (simulating email)
    print(f"[OTP] Sherjonov Abduaziz - Kod: {code} -> {email}")
    
    return JsonResponse({
        'ok': True,
        'message': 'Kod emailga yuborildi',
        'code': code,  # Auto-fill uchun (demo rejimda)
    })


@require_POST
def api_verify_otp(request):
    """JSON API for OTP verification."""
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    
    code = data.get('code', '').strip()
    action = data.get('action', 'register')
    
    session_key = f'otp_{action}'
    otp_data = request.session.get(session_key)
    
    if not otp_data:
        return JsonResponse({'ok': False, 'error': 'OTP topilmadi. Qayta urinib ko\'ring.'}, status=400)
    
    if otp_data.get('code') != code:
        return JsonResponse({'ok': False, 'error': 'Kod noto\'g\'ri'}, status=400)
    
    if action == 'register':
        # Create user
        user = User.objects.create_user(
            username=otp_data['username'],
            email=otp_data['email'],
            password=otp_data['password'],
            first_name=otp_data['first_name'],
            last_name=otp_data.get('last_name', ''),
            phone=otp_data.get('phone', ''),
            is_email_verified=True,
        )
        auth_login(request, user, backend='accounts.backends.UsernameOrEmailBackend')
        log_activity(request, user, LoginActivity.REGISTER)
        del request.session[session_key]
        
        return JsonResponse({
            'ok': True,
            'message': 'Akkount yaratildi',
            'user': {
                'id': user.pk,
                'username': user.username,
                'full_name': user.full_name,
            }
        })
    
    elif action == 'change_password':
        user = request.user
        user.set_password(otp_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save()
        update_session_auth_hash(request, user)
        del request.session[session_key]
        return JsonResponse({'ok': True, 'message': 'Parol yangilandi'})
    
    elif action == 'change_email':
        user = request.user
        user.previous_email = user.email
        user.email = otp_data['new_email']
        user.save()
        del request.session[session_key]
        return JsonResponse({'ok': True, 'message': 'Email yangilandi'})
    
    elif action == 'change_username':
        user = request.user
        user.previous_username = user.username
        user.username = otp_data['new_username']
        user.save()
        del request.session[session_key]
        return JsonResponse({'ok': True, 'message': 'Username yangilandi'})
    
    return JsonResponse({'ok': False, 'error': 'Noma\'lum amal'}, status=400)


@require_POST
def api_logout(request):
    """JSON API for logout."""
    if request.user.is_authenticated:
        log_activity(request, request.user, LoginActivity.LOGOUT)
        auth_logout(request)
    return JsonResponse({'ok': True})


@login_required
def api_login_activity(request):
    """JSON API for login activity (admin only)."""
    if not request.user.is_admin:
        return JsonResponse({'ok': False, 'error': 'Ruxsat yo\'q'}, status=403)
    
    activities = LoginActivity.objects.select_related('user').all()[:100]
    return JsonResponse({
        'ok': True,
        'activities': [
            {
                'id': a.pk,
                'full_name': a.full_name_snapshot,
                'username': a.username_snapshot,
                'action': a.action,
                'action_display': a.get_action_display(),
                'ip': a.ip_address,
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for a in activities
        ]
    })


# ============ Traditional Form-based Views ============

def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            payload = {
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "phone": form.cleaned_data.get("phone", ""),
                "password": form.cleaned_data["password"],
            }
            issue_otp(request.session, "register", payload)
            messages.success(request, "Tasdiqlash kodi emailingizga yuborildi.")
            return redirect("accounts:verify_register")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def verify_register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    auto_code = peek_otp(request.session, "register")
    if not auto_code:
        return redirect("accounts:register")
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            payload = consume_otp(request.session, "register", form.cleaned_data["code"])
            if not payload:
                messages.error(request, "Kod noto'g'ri yoki muddati o'tgan.")
            else:
                user = User.objects.create_user(
                    username=payload["username"],
                    email=payload["email"],
                    password=payload["password"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                    phone=payload.get("phone", ""),
                    is_email_verified=True,
                )
                auth_login(request, user, backend="accounts.backends.UsernameOrEmailBackend")
                log_activity(request, user, LoginActivity.REGISTER)
                messages.success(request, "Hisobingiz yaratildi!")
                return redirect("core:home")
    else:
        form = OTPForm()
    return render(request, "accounts/verify_otp.html", {
        "form": form, "auto_code": auto_code, "title": "Ro'yxatdan o'tishni tasdiqlash"
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["identifier"],
                password=form.cleaned_data["password"],
            )
            if user is None:
                messages.error(request, "Login yoki parol xato.")
            else:
                auth_login(request, user, backend="accounts.backends.UsernameOrEmailBackend")
                log_activity(request, user, LoginActivity.LOGIN)
                messages.success(request, f"Xush kelibsiz, {user.full_name}!")
                return redirect("core:home")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request, request.user, LoginActivity.LOGOUT)
        auth_logout(request)
        messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("core:home")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def settings_view(request):
    return render(request, "accounts/settings.html", {
        "password_form": ChangePasswordForm(),
        "email_form": ChangeEmailForm(),
        "username_form": ChangeUsernameForm(),
    })


# Password/Email/Username change views remain the same as before...
@login_required
def change_password_view(request):
    if request.method != "POST":
        return redirect("accounts:settings")
    form = ChangePasswordForm(request.POST)
    if not form.is_valid():
        for err in form.errors.values():
            messages.error(request, err[0])
        return redirect("accounts:settings")
    if not request.user.check_password(form.cleaned_data["old_password"]):
        messages.error(request, "Joriy parol noto'g'ri.")
        return redirect("accounts:settings")
    issue_otp(request.session, "change_password", {
        "new_password": form.cleaned_data["new_password"],
        "email": request.user.email,
    })
    messages.success(request, "Tasdiqlash kodi emailingizga yuborildi.")
    return redirect("accounts:verify_password")


@login_required
def verify_password_view(request):
    auto_code = peek_otp(request.session, "change_password")
    if not auto_code:
        return redirect("accounts:settings")
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            payload = consume_otp(request.session, "change_password", form.cleaned_data["code"])
            if not payload:
                messages.error(request, "Kod noto'g'ri.")
            else:
                request.user.set_password(payload["new_password"])
                request.user.password_changed_at = timezone.now()
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Parol yangilandi.")
                return redirect("accounts:settings")
    else:
        form = OTPForm()
    return render(request, "accounts/verify_otp.html", {
        "form": form, "auto_code": auto_code, "title": "Parolni tasdiqlash"
    })


@login_required
def change_email_view(request):
    if request.method != "POST":
        return redirect("accounts:settings")
    form = ChangeEmailForm(request.POST)
    if not form.is_valid():
        for err in form.errors.values():
            messages.error(request, err[0])
        return redirect("accounts:settings")
    if not request.user.check_password(form.cleaned_data["password"]):
        messages.error(request, "Parol noto'g'ri.")
        return redirect("accounts:settings")
    issue_otp(request.session, "change_email", {
        "new_email": form.cleaned_data["new_email"],
        "email": form.cleaned_data["new_email"],
    })
    messages.success(request, "Tasdiqlash kodi yangi emailga yuborildi.")
    return redirect("accounts:verify_email")


@login_required
def verify_email_view(request):
    auto_code = peek_otp(request.session, "change_email")
    if not auto_code:
        return redirect("accounts:settings")
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            payload = consume_otp(request.session, "change_email", form.cleaned_data["code"])
            if not payload:
                messages.error(request, "Kod noto'g'ri.")
            else:
                request.user.previous_email = request.user.email
                request.user.email = payload["new_email"]
                request.user.save()
                messages.success(request, "Email yangilandi.")
                return redirect("accounts:settings")
    else:
        form = OTPForm()
    return render(request, "accounts/verify_otp.html", {
        "form": form, "auto_code": auto_code, "title": "Yangi emailni tasdiqlash"
    })


@login_required
def change_username_view(request):
    if request.method != "POST":
        return redirect("accounts:settings")
    form = ChangeUsernameForm(request.POST)
    if not form.is_valid():
        for err in form.errors.values():
            messages.error(request, err[0])
        return redirect("accounts:settings")
    if not request.user.check_password(form.cleaned_data["password"]):
        messages.error(request, "Parol noto'g'ri.")
        return redirect("accounts:settings")
    issue_otp(request.session, "change_username", {
        "new_username": form.cleaned_data["new_username"],
        "email": request.user.email,
    })
    messages.success(request, "Tasdiqlash kodi yuborildi.")
    return redirect("accounts:verify_username")


@login_required
def verify_username_view(request):
    auto_code = peek_otp(request.session, "change_username")
    if not auto_code:
        return redirect("accounts:settings")
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            payload = consume_otp(request.session, "change_username", form.cleaned_data["code"])
            if not payload:
                messages.error(request, "Kod noto'g'ri.")
            else:
                request.user.previous_username = request.user.username
                request.user.username = payload["new_username"]
                request.user.save()
                messages.success(request, "Username yangilandi.")
                return redirect("accounts:settings")
    else:
        form = OTPForm()
    return render(request, "accounts/verify_otp.html", {
        "form": form, "auto_code": auto_code, "title": "Yangi usernameni tasdiqlash"
    })
