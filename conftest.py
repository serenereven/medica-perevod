import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from core.models import Document, DocumentCategory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="testpass123", is_active=True)


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def document_category(db):
    return DocumentCategory.objects.create(name="Медицинские заключения")


@pytest.fixture
def sample_file():
    return SimpleUploadedFile(name="test_document.pdf", content=b"file_content", content_type="application/pdf")


@pytest.fixture
def sample_document(db, document_category, sample_file):
    doc_type_value = Document.DocumentType.choices[0][0]

    return Document.objects.create(
        title="Документ 1",
        description="Тестовое описание",
        document_category=document_category,
        document_type=doc_type_value,
        is_published=True,
        file_size=1024,
        file=sample_file,
    )


@pytest.fixture
def create_document(db, document_category):
    def _create_document(title, is_published=True, **kwargs):
        doc_type_value = kwargs.pop("document_type", Document.DocumentType.choices[0][0])

        return Document.objects.create(
            title=title,
            document_category=document_category,
            document_type=doc_type_value,
            is_published=is_published,
            file=SimpleUploadedFile(
                name=f'{title.replace(" ", "_")}.pdf',
                content=f"content_{title}".encode(),
                content_type="application/pdf",
            ),
            **kwargs,
        )

    return _create_document
