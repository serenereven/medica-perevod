from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        page_size = self.get_page_size(self.request)
        page_number = self.page.number
        from_item = (page_number - 1) * page_size + 1
        to_item = min(page_number * page_size, self.page.paginator.count)
        return Response(
            {
                "count": self.page.paginator.count,
                "from": from_item,
                "to": to_item,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "required": ["count", "from", "to", "results"],
            "properties": {
                "count": {"type": "integer"},
                "from": {"type": "integer"},
                "to": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": schema,
            },
        }
