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
