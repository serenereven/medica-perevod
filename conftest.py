import pytest
from django.contrib.auth import get_user_model
from core.models import Document, DocumentCategory, DocumentType

User = get_user_model()


@pytest.fixture
def user(db):
    """Создание стандартного пользователя."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        is_active=True
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Клиент с авторизацией."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def document_category(db):
    """Категория документов."""
    return DocumentCategory.objects.create(
        name='Медицинские заключения',
        slug='medical-conclusions'
    )


@pytest.fixture
def document_type(db):
    """Тип документа."""
    return DocumentType.objects.create(
        name='Справка',
        slug='spravka'
    )


@pytest.fixture
def sample_document(db, document_category, document_type):
    """Пример документа для тестов."""
    return Document.objects.create(
        title='Документ 1',
        description='Тестовое описание',
        document_category=document_category,
        document_type=document_type,
        is_published=True,
        file_size=1024
    )