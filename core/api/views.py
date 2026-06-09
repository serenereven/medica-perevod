from django.db.models import Q, F
from django.http import FileResponse
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from natsort import natsorted, ns

from core.models import Document
from .serializers import DocumentListSerializer


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Document.objects.filter(is_published=True)

        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        # Натуральная сортировка
        sorted_qs = natsorted(qs, key=lambda d: d.title, alg=ns.LOCALE)

        page = self.paginate_queryset(sorted_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sorted_qs, many=True)
        return Response(serializer.data)

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