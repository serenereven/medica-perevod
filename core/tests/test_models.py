import pytest
from core.models import Document


@pytest.mark.django_db
class TestDocumentModel:
    
    def test_create_document(self, sample_document):
        assert sample_document.pk is not None
        assert sample_document.title == 'Документ 1'
        assert sample_document.is_published is True
    
    def test_publishable_model(self, sample_document):
        sample_document.is_published = False
        sample_document.save()
        assert not Document.objects.filter(is_published=True).exists()
    
    def test_timestamped_model(self, sample_document):
        assert sample_document.created_at is not None
        sample_document.title = 'Обновленный документ'
        sample_document.save()
        sample_document.refresh_from_db()
        assert sample_document.updated_at > sample_document.created_at