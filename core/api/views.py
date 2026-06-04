from django.db.models import Q, F
from django.http import FileResponse
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Document
from .serializers import DocumentListSerializer


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title"]
    ordering = ["title"]

    def get_queryset(self):
        qs = Document.objects.filter(is_published=True)
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return qs

    @action(detail=False, methods=["get"], url_path="meta", permission_classes=[permissions.AllowAny])
    def meta(self, request):
        return Response({
            "authenticated": request.user.is_authenticated,
        })

    @action(detail=True, methods=["get"], url_path="download", permission_classes=[permissions.IsAuthenticated])
    def download(self, request, pk=None):
        doc = self.get_object()

        if not doc.file:
            return Response({"detail": "Not found"}, status=404)

        Document.objects.filter(pk=doc.pk).update(download_count=F("download_count") + 1)

        return FileResponse(
            doc.file.open("rb"),
            as_attachment=True,
            filename=doc.file.name.split("/")[-1],
        )