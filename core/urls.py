from django.urls import path
from django.views.generic import RedirectView
from .views import DocumentListView, DocumentDownloadView, DocumentMetaView

app_name = "core"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="core:documents_page", permanent=False)),
    path("documents/", DocumentListView.as_view(), name="documents_page"),
    path("documents/<int:pk>/download/", DocumentDownloadView.as_view(), name="document_download"),
    path("api/documents/meta/", DocumentMetaView.as_view(), name="document_meta"),
]