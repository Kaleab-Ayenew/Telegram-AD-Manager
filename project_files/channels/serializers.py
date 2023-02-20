from rest_framework import serializers
from .models import TelegramChannel


class ChannelSerializer(serializers.ModelSerializer):
    # def update(self, instance, validated_data):
    #     instance.ch_username = validated_data.get(
    #         'ch_username', instance.ch_username)
    #     instance.ch_id = validated_data.get('ch_id', instance.)
    #     instance.ch_photo_id = validated_data.get('ch_photo_id')
    #     instance.ch_member_count = validated_data.get('ch_member_count')
    #     instance.save()
    #     return instance
    id = serializers.IntegerField(read_only=True)

    class Meta:
        # fields = "__all__" Can't be set if the exclude is used
        model = TelegramChannel
        extra_kwargs = {'owner': {'write_only': True}}
        exclude = ['owner']
