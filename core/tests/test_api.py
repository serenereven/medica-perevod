import pytest
from django.urls import reverse
from rest_framework import status
from core.models import Document


@pytest.mark.django_db
class TestDocumentViewSet:
    def test_list_documents_unauthenticated(self, api_client, sample_document):
        """Проверка списка документов без авторизации."""
        url = reverse("documents-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        # Проверяем структуру ответа
        doc = response.data["results"][0]
        assert "id" in doc
        assert "title" in doc
        assert "can_download" in doc
        assert doc["can_download"] is False  # Без авторизации нельзя скачивать

    def test_list_documents_authenticated(self, authenticated_client, sample_document):
        """Проверка списка документов с авторизацией."""
        url = reverse("documents-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        doc = response.data["results"][0]
        assert doc["can_download"] is True  # С авторизацией можно скачивать

    def test_list_documents_only_published(self, api_client, sample_document):
        """Проверка, что отображаются только опубликованные документы."""
        # Создаем неопубликованный документ
        Document.objects.create(
            title="Черновик",
            document_category=sample_document.document_category,
            document_type=sample_document.document_type,
            is_published=False,
        )

        url = reverse("documents-list")
        response = api_client.get(url)

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Документ 1"

    def test_download_document_authenticated(self, authenticated_client, sample_document):
        """Проверка скачивания документа авторизованным пользователем."""
        url = reverse("documents-download", kwargs={"pk": sample_document.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что счетчик скачиваний увеличился
        sample_document.refresh_from_db()
        assert sample_document.download_count == 1

    def test_download_document_unauthenticated(self, api_client, sample_document):
        """Проверка запрета скачивания без авторизации."""
        url = reverse("documents-download", kwargs={"pk": sample_document.pk})
        response = api_client.get(url)

        # Должен быть редирект на логин или 401/403
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_download_unpublished_document(self, authenticated_client, sample_document):
        """Проверка запрета скачивания неопубликованного документа."""
        sample_document.is_published = False
        sample_document.save()

        url = reverse("documents-download", kwargs={"pk": sample_document.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_n_plus_1_queries_optimization(self, authenticated_client, sample_document):
        """Проверка отсутствия проблемы N+1 в списке документов."""
        # Создаем несколько документов
        for i in range(5):
            Document.objects.create(
                title=f"Документ {i}",
                document_category=sample_document.document_category,
                document_type=sample_document.document_type,
                is_published=True,
            )

        url = reverse("documents-list")

        with self.assertNumQueries(2):  # 1 для COUNT, 1 для SELECT
            response = authenticated_client.get(url)

        assert len(response.data["results"]) == 6

    def test_natural_sorting_api(self, authenticated_client, db):
        """Проверка натуральной сортировки в API."""
        from core.models import DocumentCategory, DocumentType

        category = DocumentCategory.objects.create(name="Тест", slug="test")
        doc_type = DocumentType.objects.create(name="Тип", slug="type")

        titles = ["Документ 10", "Документ 2", "Документ 1"]
        for title in titles:
            Document.objects.create(title=title, document_category=category, document_type=doc_type, is_published=True)

        url = reverse("documents-list")
        response = authenticated_client.get(url)

        results = response.data["results"]
        assert results[0]["title"] == "Документ 1"
        assert results[1]["title"] == "Документ 2"
        assert results[2]["title"] == "Документ 10"
