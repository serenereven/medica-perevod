from django.core.paginator import Paginator
from django.views.generic import View, TemplateView, ListView, DetailView
from .models import Document
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
    queryset = Document.objects.filter(is_published=True)  # если PublishableModel
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]

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
