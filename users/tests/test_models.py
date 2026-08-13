import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        """Проверка создания пользователя по email."""
        user = User.objects.create_user(email="user@example.com", password="testpass123")

        assert user.email == "user@example.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("testpass123") is True

    def test_create_superuser(self):
        """Проверка создания суперпользователя."""
        admin = User.objects.create_superuser(email="admin@example.com", password="adminpass123")

        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_email_uniqueness(self):
        """Проверка уникальности email."""
        User.objects.create_user(email="user@example.com", password="pass123")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="user@example.com", password="pass456")

    def test_user_string_representation(self):
        """Проверка строкового представления пользователя."""
        user = User.objects.create_user(email="user@example.com", password="pass123")
        assert str(user) == "user@example.com"
