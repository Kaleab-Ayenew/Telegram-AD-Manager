# DRF Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

# DJANGO IMPORTS
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Application imports
from accounts.serializers import UserSerializer, UserDataSerializer
from .models import UserData

# module imports
from modules.accounts import utils as auth_utils


@api_view(['POST'])
@permission_classes((AllowAny,))
def auth_view(request):

    if request.user.is_authenticated:
        print("The User is Already Authenticated")
        return Response({"error": "You are already logged in"})

    user_data = request.data.copy()
    user_data.update({"tg_id": user_data.get("id")})
    user_data.pop("id")

    serializer = UserSerializer(data=user_data)

    if serializer.is_valid():
        if not auth_utils.verify_hash(request.data, request.data.get("hash")):
            return Response({"error": "Invalid Login Details"}, status=status.HTTP_401_UNAUTHORIZED)
        print(serializer.validated_data)
        user_name = str(serializer.validated_data.get("tg_id"))
        password = str(serializer.validated_data.get("tg_id"))

        user_instance = authenticate(
            request, username=user_name, password=password)

        if user_instance is None:
            user_instance = serializer.save()
            user_details = user_data.copy()
            user_details.update({"main_user": user_instance.id})
            user_details_serializer = UserDataSerializer(data=user_details)
            if user_details_serializer.is_valid():
                user_details_serializer.save()
            else:
                return Response(user_details_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_details = UserData.objects.get(main_user=user_instance.id)
            user_details_serializer = UserDataSerializer(user_details)

        # Create the authentication token

        token, _ = Token.objects.get_or_create(user=user_instance)
        login_data = {}
        login_data['id'] = user_instance.id
        login_data['status'] = "ok"
        login_data['token'] = token.key
        login_data['user_details'] = user_details_serializer.data
        return Response(login_data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
