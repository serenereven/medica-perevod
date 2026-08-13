import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestDocumentViewSet:
    def test_list_documents_unauthenticated(self, api_client, sample_document):
        url = reverse("documents-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_list_documents_authenticated(self, authenticated_client, sample_document):
        url = reverse("documents-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_documents_only_published(self, api_client, sample_document, create_document):
        create_document(title="Черновик", is_published=False)

        url = reverse("documents-list")
        response = api_client.get(url)

        assert len(response.data["results"]) == 1

    def test_download_document_authenticated(self, authenticated_client, sample_document):
        url = reverse("documents-download", kwargs={"pk": sample_document.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        sample_document.refresh_from_db()
        assert sample_document.download_count == 1

    def test_download_document_unauthenticated(self, api_client, sample_document):
        url = reverse("documents-download", kwargs={"pk": sample_document.pk})
        response = api_client.get(url)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
