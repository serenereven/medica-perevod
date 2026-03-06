import re
from django.core.exceptions import ValidationError
from django.db import models


PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def validate_phone(value: str):
    v = (value or "").strip().replace(" ", "")
    if not PHONE_RE.fullmatch(v):
        raise ValidationError("Введите телефон в формате +79991234567 (10–15 цифр).")


class NormalizedEmailField(models.EmailField):
    """
    EmailField с нормализацией (strip + lower).
    Валидация используется стандартная от Django EmailField.
    """

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            value = value.strip().lower()
        return value


class PhoneField(models.CharField):
    """
    Телефон как строка + валидация.
    Хранит телефон в виде +79991234567 или 79991234567.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 16)

        validators = list(kwargs.get("validators", []))
        validators.append(validate_phone)
        kwargs["validators"] = validators

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            value = value.strip().replace(" ", "")
        return value
