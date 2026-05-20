from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Destination
from .serializers import DestinationSerializer, HotelSerializer
from .services.hotel_search import search_hotels
from .pagination import HotelPagination


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]

class HotelSearchView(APIView):
    permission_classes = [AllowAny]
    pagination_class = HotelPagination

    def get(self, request, *args, **kwargs):
        results = search_hotels(request.query_params)
        
        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset(results, request, view=self)
        
        serializer = HotelSerializer(paginated_results, many=True)
        
        return paginator.get_paginated_response(serializer.data)
