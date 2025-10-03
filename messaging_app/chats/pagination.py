from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow client to set page size
    max_page_size = 100  # Maximum page size allowed