from rest_framework import serializers
from .models import ScheduledPost


class PostSerializer(serializers.ModelSerializer):
    channel = serializers.ReadOnlyField(
        source="destination_channel.ch_username")
    # uuid = serializers.ReadOnlyField(source="unique_id")

    class Meta:
        model = ScheduledPost
        extra_kwargs = {'owner': {'write_only': True},
                        'destination_channel': {'write_only': True}}
        exclude = ['owner', 'destination_channel']
