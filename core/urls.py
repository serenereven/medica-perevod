from django.urls import path
from .views import documents_page, DocumentListView
from django.views.generic import RedirectView
app_name = "core"

urlpatterns = [
    # path("", DocumentListView.as_view(), name="documents_page"),
    path("", RedirectView.as_view(pattern_name="core:documents_page", permanent=False)),
    path("documents/", documents_page, name="documents_page"),
]
