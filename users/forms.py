# from django import forms
# from django.contrib.auth import authenticate
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class LoginForm(forms.Form):
#     email = forms.EmailField(label="Email")
#     password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

#     def clean(self):
#         cleaned = super().clean()
#         email = cleaned.get("email")
#         password = cleaned.get("password")
#         if not email or not password:
#             return cleaned

#         user = authenticate(email=email, password=password)
#         if not user:
#             raise forms.ValidationError("Неверный email или пароль.")
#         if not user.is_active:
#             raise forms.ValidationError("Аккаунт отключён.")
#         cleaned["user"] = user
#         return cleaned


# class RegisterForm(forms.ModelForm):
#     password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
#     password2 = forms.CharField(label="Пароль ещё раз", widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ("email",)

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Пользователь с таким email уже существует.")
#         return email

#     def clean(self):
#         cleaned = super().clean()
#         p1 = cleaned.get("password1")
#         p2 = cleaned.get("password2")
#         if p1 and p2 and p1 != p2:
#             raise forms.ValidationError("Пароли не совпадают.")
#         return cleaned

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = user.email.lower()
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user

from django.utils.html import strip_tags
from allauth.account.forms import SignupForm


class CleanSignupForm(SignupForm):
    """
    Исправляет баг allauth: поле password1 содержит help_text в виде HTML-строки
    с тегом </p><ul>..., что ломает разметку формы — ul выпадает за пределы <p>.

    Решение: конвертируем HTML-список правил пароля в plain-text,
    который Django вставляет корректно внутри <span class="helptext">.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        password1 = self.fields.get("password1")
        if password1 and password1.help_text:
            # Исходный help_text: '</p><ul><li>Правило 1</li><li>Правило 2</li></ul>'
            # strip_tags убирает все теги, остаётся текст через пробелы
            raw = str(password1.help_text)
            # Заменяем </li><li> на разделитель перед strip_tags
            raw = raw.replace("</li><li>", " • ")
            raw = raw.replace("<li>", "")
            plain = strip_tags(raw).strip(" •")
            password1.help_text = plain