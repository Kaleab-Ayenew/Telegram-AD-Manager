from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import authenticate

from .utils import post_to_facebook, post_to_telegram
from .permissions import IsSocialManagerUser
from .models import FacebookData, TelegramData, SocialManagerUser
from .serializers import LoginSerializer


@api_view(['POST'])
@permission_classes((IsSocialManagerUser,))
def post_action(request):

    user = request.user
    social_manager_user = SocialManagerUser.objects.get(main_user=user)

    rsp_data = {}

    post_text = request.data.get('post_text')
    post_image = request.FILES.get('post_image').read()

    if request.data.get('post_to_facebook') == "on":
        if not FacebookData.objects.filter(owner=social_manager_user).exists():
            return Response(data={"error": "Please provide complete Facebook data."})

        fb_data = FacebookData.objects.get(owner=social_manager_user)

        rsp = post_to_facebook(fb_data.page_access_token,
                               fb_data.page_id, [post_text, post_image])
        rsp_data.update({"facebook": rsp})

    if request.data.get('post_to_telegram') == "on":

        if not TelegramData.objects.filter(owner=social_manager_user).exists():
            return Response(data={"error": "Please provide complete Telegram data."})
        tg_data = TelegramData.objects.get(owner=social_manager_user)

        rsp = post_to_telegram(tg_data.manager_bot_token,
                               tg_data.channel_username, [post_text, post_image])
        rsp_data.update({"telegram": rsp})

    return Response(data=rsp_data)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        uname = serializer.validated_data.get("username")
        passwd = serializer.validated_data.get("password")
        user = authenticate(username=uname, password=passwd)
        if user is not None:

            token, _ = Token.objects.get_or_create(user=user)
            rsp_data = {"username": uname, "token": token.key,
                        "uid": uname, "role": "admin"}
            return Response(data=rsp_data)
        else:
            return Response(data={"error": "Please provide valid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
