from django.contrib import admin
from common.admin import TimeStampedAdminMixin, PublishableAdminMixin, SoftDeleteAdminMixin
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(TimeStampedAdminMixin, admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(TimeStampedAdminMixin, PublishableAdminMixin, SoftDeleteAdminMixin, admin.ModelAdmin):
    actions = (
        "publish_selected",
        "unpublish_selected",
        "restore_selected",
        "hard_delete_selected",
    )
    list_display = (
        "id",
        "title",
        "document_category",
        "document_type",
        "is_published",
        "file_size",
        "download_count",
        "created_at",
    )
    list_filter = (
        "document_category",
        "document_type",
        "is_published",
        "created_at",
    )
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    readonly_fields = ("file_size", "download_count", "created_at", "updated_at")

    fieldsets = (
        ("Основное", {
            "fields": ("title", "description", "file", "preview"),
        }),
        ("Классификация", {
            "fields": ("document_category", "document_type"),
        }),
        ("Публикация", {
            "fields": ("is_published",),
        }),
        ("Статистика", {
            "fields": ("file_size", "download_count"),
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at",),
            "classes": ("collapse",),
        }),
    )
