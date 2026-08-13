from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from common.views import robots_txt
from django.contrib.sitemaps.views import sitemap
from common.sitemaps import sitemaps


urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("", include(("core.urls", "core"), namespace="core")),
    path("api/", include("core.api.urls")),
    # SEO files
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django_sitemap"),
    path("accounts/", include("allauth.urls")),
]


handler400 = "common.views.error_page"
handler403 = "common.views.error_page"
handler404 = "common.views.error_page"
handler500 = "common.views.error_page"

if settings.DEBUG:
    # Медиа файлы
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Статические файлы
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
