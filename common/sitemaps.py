from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return ["core:documents_page",]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
}