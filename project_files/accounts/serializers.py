from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserData


class UserSerializer(serializers.ModelSerializer):
    tg_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        id = validated_data.get("tg_id")
        print("This is the id", id, sep=":")
        new_user = User.objects.create_user(str(id), None, str(id))
        new_user.first_name = validated_data.get("first_name")
        new_user.save()
        return new_user

    class Meta:
        model = User
        fields = ["tg_id", "first_name"]


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = "__all__"
