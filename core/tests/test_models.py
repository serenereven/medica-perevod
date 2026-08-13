import pytest
from django.utils import timezone
from core.models import Document, DocumentCategory


@pytest.mark.django_db
class TestDocumentModel:
    
    def test_create_document(self, sample_document):
        """Проверка создания документа."""
        assert sample_document.pk is not None
        assert sample_document.title == 'Документ 1'
        assert sample_document.is_published is True
    
    def test_soft_delete(self, sample_document):
        """Проверка работы Soft Delete."""
        sample_document.delete()
        
        assert not Document.objects.filter(pk=sample_document.pk).exists()
        
        assert Document.alive.filter(pk=sample_document.pk).exists()
        
        assert Document.deleted.filter(pk=sample_document.pk).exists()
    
    def test_publishable_model(self, sample_document):
        """Проверка логики публикации."""
        # Документ опубликован
        assert sample_document.is_published is True
        
        # Снимаем с публикации
        sample_document.is_published = False
        sample_document.save()
        
        # Проверяем, что документ не отображается в публичном доступе
        assert not Document.objects.filter(is_published=True).exists()
    
    def test_natural_sorting(self, db, document_category, document_type):
        """Проверка натуральной сортировки документов."""
        titles = ['Документ 10', 'Документ 2', 'Документ 1']
        
        for title in titles:
            Document.objects.create(
                title=title,
                document_category=document_category,
                document_type=document_type,
                is_published=True
            )
        
        documents = list(Document.alive.all().order_by('title'))
        
        # При обычной сортировке будет: Документ 1, Документ 10, Документ 2
        # При натуральной должно быть: Документ 1, Документ 2, Документ 10
        assert documents[0].title == 'Документ 1'
        assert documents[1].title == 'Документ 2'
        assert documents[2].title == 'Документ 10'
    
    def test_timestamped_model(self, sample_document):
        """Проверка автоматического обновления временных меток."""
        assert sample_document.created_at is not None
        assert sample_document.updated_at is not None
        
        # Обновляем объект
        sample_document.title = 'Обновленный документ'
        sample_document.save()
        
        # Проверяем, что updated_at изменился
        sample_document.refresh_from_db()
        assert sample_document.updated_at > sample_document.created_at