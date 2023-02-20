from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

# Serializer Imports
from .serializers import ChannelSerializer
from .models import TelegramChannel

# Permission Imports
from .permissions import IsAuthAndOwnsObject


class ChannelListCreate(generics.ListCreateAPIView):
    serializer_class = ChannelSerializer

    def create(self, request, *args, **kwargs):
        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return TelegramChannel.objects.filter(owner=self.request.user.id)


class ChannelRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = TelegramChannel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthAndOwnsObject]

    def update(self, request, *args, **kwargs):
        channel = self.get_object()
        serializer = ChannelSerializer(channel, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
