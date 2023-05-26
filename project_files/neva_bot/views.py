
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from .utils import edit_message, send_message, post_to_telegraph, translate
from .data import ACCOUNTS_TEXT


@api_view(['POST'])
@permission_classes((AllowAny,))
def channel_admin_bot(request):
    print(request.data)
    if request.data.get('channel_post') and request.data.get('channel_post').get('sender_chat').get('username') == 'neva_test_channel':
        chat_id = request.data.get('channel_post').get('sender_chat').get('id')
        msg_id = request.data.get('channel_post').get('message_id')
        msg_text = request.data.get('channel_post').get('text')
        caption = request.data.get('channel_post').get('caption')

        new_msg = msg_text if msg_text else caption
        if not new_msg:
            return Response(data="Done")

        # am_text = translate(new_msg)
        tg_url = post_to_telegraph(new_msg)

        btns = [[{
            'text': "Map", "url": "https://goo.gl/maps/M8cxKRRHALFurfURA"}]]

        new_msg = new_msg + \
            f"\n\n<a href=\"{tg_url}\">ለአማርኛ ይሄን ይጫኑ</a>\n\n[Neva Computers]"
        edit_message(chat_id=chat_id, msg_id=msg_id,
                     text=new_msg, buttons=btns) if msg_text else edit_message(chat_id=chat_id, msg_id=msg_id,
                                                                               caption=new_msg, buttons=btns)

    return Response(data="Done")


@api_view(['POST'])
@permission_classes((AllowAny,))
def info_bot(request):
    print(request.data)
    INFO_BOT_TOKEN = "6198880276:AAG_eixN41p_9028rQuC6gkcFeTme2W4Z6k"
    if request.data.get('message'):
        user_id = request.data.get('message').get('from').get('id')
        first_name = request.data.get('message').get('from').get('first_name')
        message = request.data.get('message').get('text')

        if message == '/start':
            btns = [[{"text": "Bank Accounts"}]]
            send_message(user_id=user_id, text="Welcome to Neva Info Bot\nWhat do you want to do?",
                         token=INFO_BOT_TOKEN, buttons=btns)
            return Response(data="Done")
        elif message == "Bank Accounts":
            btns = [[{"text": "Bank Accounts"}]]
            send_message(user_id=user_id, text=ACCOUNTS_TEXT,
                         token=INFO_BOT_TOKEN, buttons=btns)
            return Response(data="Done")
    return Response(data="Done")
