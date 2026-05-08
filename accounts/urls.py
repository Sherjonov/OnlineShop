from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # JSON API endpoints
    path("api/login/", views.api_login, name="api_login"),
    path("api/register/", views.api_register, name="api_register"),
    path("api/verify-otp/", views.api_verify_otp, name="api_verify_otp"),
    path("api/logout/", views.api_logout, name="api_logout"),
    path("api/login-activity/", views.api_login_activity, name="api_login_activity"),
    
    # Traditional form views
    path("register/", views.register_view, name="register"),
    path("register/verify/", views.verify_register_view, name="verify_register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/password/", views.change_password_view, name="change_password"),
    path("settings/password/verify/", views.verify_password_view, name="verify_password"),
    path("settings/email/", views.change_email_view, name="change_email"),
    path("settings/email/verify/", views.verify_email_view, name="verify_email"),
    path("settings/username/", views.change_username_view, name="change_username"),
    path("settings/username/verify/", views.verify_username_view, name="verify_username"),
]
