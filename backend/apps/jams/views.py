from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Jam
from .serializers import JamSerializer


class JamViewSet(viewsets.ModelViewSet):
    queryset = Jam.objects.all()
    serializer_class = JamSerializer
    permission_classes = [AllowAny]
