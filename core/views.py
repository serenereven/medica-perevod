from django.db.models import F
from django.http import FileResponse, Http404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Document, DocumentCategory
from .api.serializers import DocumentListSerializer


class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Document.objects.published().for_list_view()

        category = self.request.query_params.get("category")
        doc_type = self.request.query_params.get("type")
        q = self.request.query_params.get("q")

        if category:
            qs = qs.filter(document_category_id=category)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class DocumentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        try:
            doc = Document.objects.published().get(pk=pk)
        except Document.DoesNotExist as err:
            raise Http404("Document not found") from err

        if not doc.file:
            raise Http404

        Document.objects.filter(pk=doc.pk).update(download_count=F("download_count") + 1)

        return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.file.name.split("/")[-1])


class DocumentMetaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Используем аннотацию для подсчета документов
        categories = DocumentCategory.objects.with_document_count()

        return Response(
            {
                "authenticated": request.user.is_authenticated,
                "document_categories": [
                    {"value": str(c.pk), "label": c.name, "count": c.documents_count} for c in categories
                ],
                "document_types": [{"value": value, "label": label} for value, label in Document.DocumentType.choices],
            }
        )
