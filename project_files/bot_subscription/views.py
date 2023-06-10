from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny


from django.db import IntegrityError

from . import utils, data
from modules.global_utils.utils import send_message

import json


@api_view(['POST'])
@permission_classes((AllowAny,))
def main_bot_handler(request):

    if request.data.get('pre_checkout_query'):
        query = request.data.get('pre_checkout_query')
        print(query)
        print(request.data.get('invoice_payload'))
        utils.answer_callback_query(query['id'])
        return Response(data='Done')

    if request.data.get('message') and request.data.get('message').get('text'):
        text = request.data.get('message').get('text')
        chat_id = request.data.get('message').get('from').get('id')

        if len(text.split(' ')) == 2:
            invoice_code = text.split(' ')[1]
            utils.send_payment_invoice(
                invoice_code=invoice_code, chat_id=chat_id)
            return Response(data='Done')
        else:
            send_message(user_id=chat_id, text='Invalid Request',
                         bot_token=data.SUB_BOT_TOKEN)
            return Response(data='Done')

    elif request.data.get('message') and request.data.get('message').get('successful_payment'):
        payment_info = request.data.get('message').get('successful_payment')

        price = payment_info.get('total_amount') / 100
        currency = payment_info.get('currency')
        payload = payment_info.get('invoice_payload')
        chat_id = request.data.get('message').get('from').get('id')
        name = request.data.get('message').get('from').get('first_name')

        print("This is payload", type(payload))
        payload = json.loads(payload)
        bt_name = payload.get('bot_name')
        sub_fun = utils.SUB_FUNS.get(bt_name)
        subscription = sub_fun(chat_id=chat_id, data=payload)
        
        
        if subscription:
            text_response = f"❇️ ክፍያው ተሳክቷል።\n\n😊 ወደ ቦቱ በመመለስ አዲስ የገዙትን {payload.get('sub_level')} plan መጠቀም ይችላሉ።"
            send_message(user_id=chat_id, text=text_response,
                         bot_token=data.SUB_BOT_TOKEN)
            return Response(data='Done')
        else:
            text_response = '⛔️ ክፍያው አልተሳካም። እባክዎን እንደገና ይሞክሩ ⛔️'
            send_message(user_id=chat_id, text=text_response,
                         bot_token=data.SUB_BOT_TOKEN)
            return Response(data='Done')

    return Response(data='Done')
