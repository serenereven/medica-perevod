from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from core.models import Document
from .serializers import DocumentListSerializer
from .functions import ExtractLeadingText, ExtractFirstNumber


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Document.alive.all()

        # Подгружаем связанные сущности одним SQL-запросом через JOIN
        queryset = queryset.select_related(
            'document_category', 
            'document_type'
        )

        # Загружаем только те поля, которые требуются для сериализатора
        queryset = queryset.only(
            'id', 'title', 'description', 'document_type', 'document_category',
            'file_size', 'download_count', 'preview', 'created_at'
        )

        # Если число отсутствует, Cast вернет NULL, который мы заменяем на 0
        queryset = queryset.annotate(
            sort_text=ExtractLeadingText('title'),
            sort_num=Coalesce(
                Cast(ExtractFirstNumber('title'), IntegerField()), 
                Value(0)
            )
        ).order_by('sort_text', 'sort_num')

        return queryset