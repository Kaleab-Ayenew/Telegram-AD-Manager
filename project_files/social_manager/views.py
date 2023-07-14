from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import authenticate

from . import utils
from . import config
from .permissions import IsSocialManagerUser
from .models import FacebookData, TelegramData, SocialManagerUser
from .serializers import LoginSerializer
from modules.global_utils import utils as gb_utils


@api_view(['POST'])
@permission_classes((IsSocialManagerUser,))
def post_action(request):

    user = request.user
    social_manager_user = SocialManagerUser.objects.get(main_user=user)

    rsp_data = {}
    print(request.data)
    post_text = request.data.get('post_text')
    post_image = request.FILES.get('post_image').read()

    image_url, image_path = utils.save_image(request.FILES.get('post_image'))

    if request.data.get('post_to_facebook') == "on":
        if not FacebookData.objects.filter(owner=social_manager_user).exists():
            return Response(data={"error": "Please connect your Facebook account."}, status=status.HTTP_400_BAD_REQUEST)

        fb_data = FacebookData.objects.get(owner=social_manager_user)
        fb_page_id = request.data.getlist('fb_page_id')

        print("[&&] This is the page id", fb_page_id)

        for p_id in fb_page_id:
            page_access_token = utils.get_single_page_token(
                p_id, fb_data.user_access_token)
            rsp = utils.post_to_facebook(page_token=page_access_token,
                                         page_id=p_id, post_content=[post_text, image_url])
            rsp_data.update({"facebook": rsp})

    if request.data.get('post_to_telegram') == "on":
        tg_channels = request.data.getlist('tg_channel')
        if not TelegramData.objects.filter(owner=social_manager_user).exists():
            return Response(data={"error": "Please connect yout Telegram Channel."}, status=status.HTTP_400_BAD_REQUEST)

        for channel in tg_channels:
            rsp = utils.post_to_telegram(
                config.TELEGRAM_MANAGER_BOT_TOKEN, channel, [post_text, image_url])

        # rsp = utils.post_to_telegram(tg_data.manager_bot_token,
        #                              tg_data.channel_username, [post_text, image_url])
        rsp_data.update({"telegram": rsp})

    if request.data.get('post_to_instagram') == 'on':
        if not FacebookData.objects.filter(owner=social_manager_user).exists():
            return Response(data={"error": "Please connect your Facebook account."}, status=status.HTTP_400_BAD_REQUEST)

        fb_data = FacebookData.objects.get(owner=social_manager_user)
        ig_page_id = request.data.getlist('ig_page_id')

        for p_id in ig_page_id:

            rsp = utils.post_to_instagram(
                fb_data.user_access_token, p_id, [post_text, image_url, image_url])
            rsp_data.update({"instagram": rsp})

    # Delete the post image from the file system
    gb_utils._delete_file(image_path)

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
                        "uid": uname}
            return Response(data=rsp_data)
        else:
            return Response(data={"error": "Please provide valid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def sign_up_view(request):
    data = request.data
    print(data)

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        uname = serializer.validated_data.get("username")
        passwd = serializer.validated_data.get("password")
        email = serializer.validated_data.get("email")
        new_user = utils.create_user(
            username=uname, password=passwd, email=email)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=new_user)
    rsp_data = {"username": new_user.username, "token": token.key,
                "uid": new_user.username, "role": "admin"}

    return Response(data=rsp_data)


@api_view(['POST'])
@permission_classes((IsSocialManagerUser,))
def create_fb_data(request):
    data = request.data
    user_access_token = data.get('accessToken')
    fb_user_id = data.get('userID')
    social_user = utils.get_social_user(request.user)

    if utils.get_facebook_data(social_user):
        return Response(data={'error': 'You have already connected your Facebook data.'}, status=status.HTTP_400_BAD_REQUEST)
    fb_data = utils.create_facebook_data(
        social_user, fb_user_id, user_access_token)

    rsp_data = {
        'uat': fb_data.user_access_token,
        'user_id': fb_data.fb_user_id,
        'uat_exp_date': fb_data.uat_exp_date
    }
    return Response(data=rsp_data)


@api_view(['POST'])
@permission_classes((IsSocialManagerUser,))
def update_fb_data(request):
    data = request.data
    user_access_token = data.get('accessToken')
    fb_user_id = data.get('userID')
    social_user = utils.get_social_user(request.user)

    current_fb_data = utils.get_facebook_data(social_user)
    if current_fb_data:
        current_fb_data.fb_user_id = fb_user_id
        current_fb_data.user_access_token = user_access_token
        current_fb_data.save()

        rsp_data = {
            'uat': current_fb_data.user_access_token,
            'user_id': current_fb_data.fb_user_id,
            'uat_exp_date': current_fb_data.uat_exp_date
        }

        return Response(data=rsp_data)

    else:
        return Response(data={'error': 'The requested data was not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((IsSocialManagerUser,))
def get_fb_pages(request):
    social_user = utils.get_social_user(request.user)
    pages = utils.get_fb_pages(social_user.facebook_data.user_access_token)[2]
    rsp_data = pages

    return Response(data=rsp_data)


@api_view(['GET'])
@permission_classes((IsSocialManagerUser,))
def get_ig_pages(request):
    social_user = utils.get_social_user(request.user)
    fb_uat = social_user.facebook_data.user_access_token
    pages = utils.get_fb_pages(fb_uat)[2]

    ig_pages = utils.get_ig_page_list(
        list(pages.keys()), fb_uat)
    rsp_data = {}
    for fb_pg_id, ig_pg_id in ig_pages:
        ig_pg_info = utils.get_ig_page_info(ig_pg_id, fb_uat)
        if ig_pg_info.get('error'):
            continue
        rsp_data.update({fb_pg_id: ig_pg_info})

    return Response(data=rsp_data)


@api_view(['GET'])
@permission_classes((IsSocialManagerUser,))
def get_tg_pages(request):
    social_user = utils.get_social_user(request.user)
    channel_list = utils.get_tg_channel_list(social_user)
    return Response(data=channel_list)
