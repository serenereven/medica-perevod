from django.core.paginator import Paginator
from django.views.generic import View, TemplateView, ListView, DetailView
from .models import Document, DocumentCategory
from django.shortcuts import render


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)


        return ctx


from django.db.models import F
from django.http import FileResponse, Http404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Document
from .api.serializers import DocumentListSerializer


class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Document.objects.filter(is_published=True)
        category = self.request.query_params.get("category")
        doc_type = self.request.query_params.get("type")
        q = self.request.query_params.get("q")

        if category:
            qs = qs.filter(document_category__pk=category)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class DocumentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        try:
            doc = Document.objects.get(pk=pk, is_published=True)
        except Document.DoesNotExist:
            raise Http404

        if not doc.file:
            raise Http404

        # атомарно увеличиваем скачивания
        Document.objects.filter(pk=doc.pk).update(download_count=F("download_count") + 1)

        # отдача файла (для локального/FS storage)
        # as_attachment=True -> браузер скачивает, а не открывает
        return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.file.name.split("/")[-1])


def documents_page(request):
    return render(request, "core/documents.html")


class DocumentMetaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = DocumentCategory.objects.all()
        return Response({
            "authenticated": request.user.is_authenticated,
            "document_categories": [
                {"value": str(c.pk), "label": c.name} for c in categories
            ],
            "document_types": [
                {"value": v, "label": l}
                for v, l in Document.DocumentType.choices
            ],
        })