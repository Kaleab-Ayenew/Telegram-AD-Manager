from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from . import utils


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_proposal(request):
    user = request.data.get('message').get('from').get('id')
    rsp = utils.send_message(user, "Done")
    return Response(data="Done")
    print(request.data)
    user = request.data.get('message').get('from').get('id')
    text = request.data.get('message').get('text')

    print(text)
    print(user)
    buffer = ""
    rsp = utils.send_message(user, text[0])
    msg_id = rsp.json().get("result").get("message_id")
    for t in text.split(' '):
        buffer = buffer + " " + t
        rsp = utils.edit_message(user, msg_id, buffer)

    return Response(data="Done")
