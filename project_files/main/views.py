from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from .models import ScheduledPost
from .serializers import PostSerializer
from .permissions import IsAuthAndOwnsObject

from channels.models import TelegramChannel


class CreateListPost(generics.ListCreateAPIView):
    serializer_class = PostSerializer

    def user_owns_channel(self, ch_username):
        print("Channel username: ", ch_username)
        try:
            channel = TelegramChannel.objects.get(ch_username=ch_username)
        except TelegramChannel.DoesNotExist:
            print("This channel doesn't exist.")
            return None
        if channel.owner == self.request.user:
            return channel
        else:
            print("The user doesn't own this channel: ", channel.ch_username)
            return None

    def get_queryset(self):
        print(self.request.query_params)
        start = int(self.request.query_params.get("s", 0))
        end = int(self.request.query_params.get("e", 10))
        print(start, end)

        if end - start != 10:
            start = 0
            end = 10

        posts = ScheduledPost.objects.filter(
            owner=self.request.user.id)[start:end]
        return posts

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)

            if request.data.get('dest_ch') is None:
                return Response(data={"error": "Please provide a target channel."}, status=status.HTTP_400_BAD_REQUEST)
            dest_ch = request.data.get('dest_ch')

            if self.user_owns_channel(dest_ch) is None:
                return Response(data={"error": "Please select another channel."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save(owner=request.user,
                            destination_channel=self.user_owns_channel(dest_ch))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthAndOwnsObject]
    lookup_field = "unique_id"

    def get_queryset(self):
        posts = ScheduledPost.objects.filter(owner=self.request.user.id)
        return posts

    def user_owns_channel(self, ch_username):
        print("Channel username: ", ch_username)
        try:
            channel = TelegramChannel.objects.get(ch_username=ch_username)
        except TelegramChannel.DoesNotExist:
            print("This channel doesn't exist.")
            return None
        if channel.owner == self.request.user:
            return channel
        else:
            print("The user doesn't own this channel: ", channel.ch_username)
            return None

    def update(self, request, *args, **kwargs):
        serializer = PostSerializer(self.get_object(), data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)

            # Add type checking here [Check if the value is of the appropriate type]
            if request.data.get('dest_ch') is None:
                return Response(data={"error": "Please provide a target channel."}, status=status.HTTP_400_BAD_REQUEST)
            dest_ch = request.data.get('dest_ch')

            if self.user_owns_channel(dest_ch) is None:
                return Response(data={"error": "Please select another channel."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save(owner=request.user,
                            destination_channel=self.user_owns_channel(dest_ch))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
