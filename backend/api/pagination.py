from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пользовательский класс разбиения на страницы."""
    page_size_query_param = 'limit'
