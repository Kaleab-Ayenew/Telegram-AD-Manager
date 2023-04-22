from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import requests

from .utils import request_payment, check_webhook_origin, send_payment_invoice, answer_callback_query, shop_bot_request, shop_bot_channel_post, send_bot_msg


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_pay(request):
    rsp = request_payment(request.data)
    return Response(data=rsp)


@api_view(['POST', 'GET'])
@permission_classes((AllowAny,))
def chapa_callback(request):
    print(request.query_params)
    print(request.data)
    return Response(data={})


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_payment_webhook(request):
    print(request.data)
    hash = request.headers.get('Chapa-Signature')
    if check_webhook_origin(hash):
        print("This is a Legitmate request")
    else:
        print("This is a HACKER")
    return Response(data='Done')


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_bot_webhook(request):
    print(request.data)
    if request.data.get('pre_checkout_query'):
        query = request.data.get('pre_checkout_query')
        print(query)
        print(request.data.get('invoice_payload'))
        answer_callback_query(query['id'])
        return Response(data='Done')
    if request.data.get('message') and request.data.get('message').get('text'):
        text = request.data.get('message').get('text')
        if '/start' in text:
            id = request.data.get('message').get('from').get('id')
            if len(text.split(' ')) == 2:
                product_id = text.split(' ')[1]
            else:
                return Response(data='Done')
            rsp = send_payment_invoice(product_id, id)
            print(rsp)
    elif request.data.get('message') and request.data.get('message').get('successful_payment'):
        payment_info = request.data.get('message').get('successful_payment')
        price = payment_info.get('total_amount') / 100
        currency = payment_info.get('currency')
        chat_id = request.data.get('message').get('from').get('id')
        name = request.data.get('message').get('from').get('first_name')
        msg = f'Dear {name},\nYou have succesfully paid {price} {currency} to ሱቅ🛒'
        data = {
            'text': msg,
            'chat_id': chat_id
        }
        from .utils import CHAPA_BOT_TOKEN
        rsp = send_bot_msg(data, CHAPA_BOT_TOKEN)
        print(rsp)

    return Response(data='Done')


product_form_index = 0
product_info = {}


@api_view(['POST'])
@permission_classes((AllowAny,))
def shop_manager_webhook(request):
    global product_form_index, product_info

    if request.data.get('my_chat_member'):
        channel_name = request.data.get(
            'my_chat_member').get('chat').get('title')
        adder_name = request.data.get(
            'my_chat_member').get('from').get('first_name')
        adder_id = request.data.get(
            'my_chat_member').get('from').get('id')

        text = f"The bot was added to channel {channel_name} by {adder_name}"

        data = {
            'chat_id': adder_id,
            'text': text,
            'buttons': ['Add a new product', 'List all products']
        }

        rsp = shop_bot_request(data)
        print(rsp)

        return Response(data='Done')

    if request.data.get('message'):
        print(request.data)
        chat_id = request.data.get('message').get('from').get('id')
        text = request.data.get('message').get('text')
        questions = ['What is the product name?', 'What is the product description?',
                     'What is the product price?', 'Send product image?']

        data = {'chat_id': chat_id}

        if text == '/start':
            data.update({'text': 'Add this bot as an Admin to your channel'})
            rsp = shop_bot_request(data)
            print(rsp)
        if text == 'hi':
            data = {
                'chat_id': chat_id,
                'text': "Welcome to Black Storm Shop Manager",
                'buttons': ['Add a new product', 'List all products']
            }

            rsp = shop_bot_request(data)
            print(rsp)
        elif text == 'Add a new product' and product_form_index == 0:
            data.update({'text': questions[product_form_index]})
            product_form_index += 1
            rsp = shop_bot_request(data)
            print(rsp)

        elif product_form_index > 0 and product_form_index < len(questions):
            product_info.update({questions[product_form_index-1]: text})
            data.update({'text': questions[product_form_index]})
            product_form_index += 1
            rsp = shop_bot_request(data)
            print(rsp)

        elif product_form_index == len(questions):
            image_id = request.data.get('message').get('photo')[
                2].get('file_id')
            image_width = request.data.get('message').get('photo')[
                2].get('width')
            image_height = request.data.get('message').get('photo')[
                2].get('height')
            image = {'file_id': image_id,
                     'width': image_width, 'height': image_height}
            product_info.update({questions[product_form_index-1]: image})
            product_form_index = 0
            print(product_info)
            data.update({'text': 'Product has been added succesfully',
                        'buttons': ['Post to Channel']})
            rsp = shop_bot_request(data)
            print(rsp)

        elif product_form_index == 0 and text == 'Post to Channel':
            post_data = {**product_info}
            post_data.update({'chat_id': chat_id})
            shop_bot_channel_post(post_data)
            product_info = {}

            data = {
                'chat_id': chat_id,
                'text': "Product has been posted to your channel.",
                'buttons': ['Add a new product', 'List all products']
            }

            rsp = shop_bot_request(data)
            print(rsp)

    return Response(data='Done')
