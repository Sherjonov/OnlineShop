from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=40, label="Ism")
    last_name = forms.CharField(max_length=40, label="Familiya")
    username = forms.CharField(max_length=40, label="Foydalanuvchi nomi")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol", min_length=4)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni tasdiqlang")

    def clean_username(self):
        u = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=u).exists():
            raise ValidationError("Bu username band.")
        return u

    def clean_email(self):
        e = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=e).exists():
            raise ValidationError("Bu email allaqachon ro'yxatda.")
        return e

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Parollar mos emas.")
        return cleaned


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username yoki email")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, label="Kod")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Joriy parol")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Yangi parol", min_length=4)
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Tasdiqlang")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") and cleaned.get("new_password") != cleaned.get("new_password2"):
            self.add_error("new_password2", "Parollar mos emas.")
        return cleaned


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label="Yangi email")
    password = forms.CharField(widget=forms.PasswordInput, label="Joriy parol")

    def clean_new_email(self):
        e = self.cleaned_data["new_email"].strip().lower()
        if User.objects.filter(email__iexact=e).exists():
            raise ValidationError("Bu email band.")
        return e


class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(max_length=40, label="Yangi username")
    password = forms.CharField(widget=forms.PasswordInput, label="Joriy parol")

    def clean_new_username(self):
        u = self.cleaned_data["new_username"].strip()
        if User.objects.filter(username__iexact=u).exists():
            raise ValidationError("Bu username band.")
        return u
