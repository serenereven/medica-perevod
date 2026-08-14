from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import FileResponse
from django.db.models import F, IntegerField, Value
from django.db.models.functions import Cast, Coalesce
from django.db import connection
from core.models import Document
from .serializers import DocumentListSerializer
from .functions import ExtractLeadingText, ExtractFirstNumber


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentListSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Document.objects.filter(is_published=True)
        queryset = queryset.select_related("document_category")
        queryset = queryset.only(
            "id",
            "title",
            "description",
            "document_type",
            "document_category",
            "file_size",
            "download_count",
            "preview",
            "created_at",
        )

        if connection.vendor == "postgresql":
            queryset = queryset.annotate(
                sort_text=ExtractLeadingText("title"),
                sort_num=Coalesce(
                    Cast(ExtractFirstNumber("title"), IntegerField()),
                    Value(0),
                ),
            ).order_by("sort_text", "sort_num")
        else:
            queryset = queryset.order_by("title")

        return queryset

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download(self, request, pk=None):
        try:
            doc = self.get_queryset().get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {"detail": "Документ не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doc.file:
            return Response(
                {"detail": "Файл отсутствует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        Document.objects.filter(pk=doc.pk).update(download_count=F("download_count") + 1)

        return FileResponse(
            doc.file.open("rb"),
            as_attachment=True,
            filename=doc.file.name.split("/")[-1],
        )
