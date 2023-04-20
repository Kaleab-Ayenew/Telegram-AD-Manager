from rest_framework import serializers
from .models import ScheduledPost
from .utils import b64tofile
import base64
import io
from django.core.files import File


class PostSerializer(serializers.ModelSerializer):
    channel = serializers.ReadOnlyField(
        source="destination_channel.ch_username")
    # uuid = serializers.ReadOnlyField(source="unique_id")
    post_image = serializers.ReadOnlyField()

    # def create(self, validated_data):
    #     photo = validated_data.
    #     instance = ScheduledPost.objects.create()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({"post_image": str(instance.post_image)})
        return data

    def create(self, validated_data):
        img = validated_data.get('image')
        validated_data.pop('image')
        instance = ScheduledPost.objects.create(**validated_data)
        instance.post_image.save(*b64tofile(img))
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # file_data = validated_data.get('image').split(
        #     ',') if validated_data.get('image') else None
        # if file_data:
        #     ext = file_data[0].split(';')[0].split('/')[1]
        #     file = io.BytesIO(base64.b64decode(
        #         file_data[1]))
        #     dj_file = File(file)
        #     instance.post_image.save('image.'+ext, dj_file)

        img = validated_data.get('image')
        if img:
            instance.post_image.save(*b64tofile(img))

        instance.post_content = validated_data.get(
            'post_content', instance.post_content)
        instance.post_buttons = validated_data.get(
            'post_buttons', instance.post_buttons)
        instance.start_date = validated_data.get(
            'start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.post_time = validated_data.get(
            'post_time', instance.post_time)
        instance.sent = validated_data.get('sent', instance.sent)
        instance.save()
        print(instance.post_image, "Here is the post image")
        return instance

    class Meta:
        model = ScheduledPost
        extra_kwargs = {'owner': {'write_only': True},
                        'destination_channel': {'write_only': True}, 'image': {}}
        exclude = ['owner', 'destination_channel',]
