from rest_framework import serializers
from core.models import Document


class DocumentListSerializer(serializers.ModelSerializer):
    file_size_display = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "document_type",
            "document_category",
            "file_size",
            "file_size_display",
            "extension",
            "preview_url",
            "download_count",
            "can_download",
            "download_url",
        ]

    def get_file_size_display(self, obj):
        return obj.get_file_size_display()

    def get_extension(self, obj):
        return obj.get_file_extension()

    def get_preview_url(self, obj):
        if not obj.preview:
            return None
        request = self.context.get("request")
        url = obj.preview.url
        return request.build_absolute_uri(url) if request else url

    def get_can_download(self, obj):
        request = self.context.get("request")
        return bool(request and request.user and request.user.is_authenticated)

    def get_download_url(self, obj):
        request = self.context.get("request")
        if not (request and request.user and request.user.is_authenticated):
            return None
        url = f"/api/documents/{obj.pk}/download/"
        return request.build_absolute_uri(url) if request else url
