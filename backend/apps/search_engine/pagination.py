from rest_framework.pagination import PageNumberPagination

class HotelPagination(PageNumberPagination):
    page_size = 10
