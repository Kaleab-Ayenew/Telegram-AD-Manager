from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .models import TelegramUser
from .utils import get_user, new_user_rsp, user_stat_rsp, empty_rsp, proxy_rsp
# Create your views here.

import requests


@api_view(['POST'])
@permission_classes((AllowAny,))
def invite_bot_requests(request):
    data = request.data
    user_id = str(data['message']['from']['id'])
    first_name = data['message']['from']['first_name']
    msg = data['message'].get('text')

    if msg is not None:
        msg_split = msg.split(" ")

        if msg_split[0] == "/start":
            inviter = msg_split[1] if len(msg_split) == 2 else None

            if get_user(user_id) is not None:
                print("User is already registered")
                return Response(data="Done")

            new_user = TelegramUser(
                tg_user_id=user_id, first_name=first_name, invited_by=inviter)
            new_user.save()

            if inviter:
                inviter_user = get_user(inviter)
                if inviter_user and inviter != user_id:
                    inviter_user.invited_number = inviter_user.invited_number + 1
                    inviter_user.save()

            rsp_code = new_user_rsp(new_user)

            print(f"Recieved data `{rsp_code}]` from telegram.\n")

            return Response(data=str(rsp_code))
        else:
            if msg.strip() == "መረጃዎትን ለመመልከት":
                user = get_user(user_id)
                if not user:
                    return Response(data="Done")
                stat_rsp = user_stat_rsp(user)
                return Response(data="Done")
            else:
                empty_rsp(user_id)
                return Response(data="Done")

    return Response(data="Done")


@api_view(['POST'])
@permission_classes((AllowAny,))
def proxy_bot_request(request):
    data = request.data
    user_id = str(data['message']['from']['id'])
    first_name = data['message']['from']['first_name']
    msg = data['message'].get('text')
    if msg is not None:

        if msg == "/start":
            rsp = proxy_rsp(user_id)
            print(rsp)
            return Response(data="Done")
        else:
            return Response(data="Done")


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_pay_bot(request):
    return Response(data="Hello World")


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_api_hook(request):
    return Response(data="Hello World")