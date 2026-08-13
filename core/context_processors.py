from django.core.cache import cache
from core.models import Contact, BasicPage, ContactType

CACHE_KEY = "core_base_data:v1"
CACHE_TTL = 60 * 10  # 10 минут


def base_data(request):
    data = cache.get(CACHE_KEY)
    if data:
        return data

    qs = Contact.published.order_by("sort_order")
    social_types = [ContactType.TELEGRAM, ContactType.VK, ContactType.WHATSAPP]

    socials = list(qs.filter(contact_type__in=social_types))
    contacts = list(qs.exclude(contact_type__in=social_types))

    data = {
        "socials": socials,
        "contacts": contacts,
        "pages_menu": list(BasicPage.published.alive().filter(is_navbar=True)),
    }
    cache.set(CACHE_KEY, data, CACHE_TTL)
    return data
