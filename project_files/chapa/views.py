from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.db import IntegrityError

from .models import TempData, Product
import requests

from .utils import request_payment, check_webhook_origin, send_payment_invoice, answer_callback_query, shop_bot_request, shop_bot_channel_post, send_bot_msg, save_product_info


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
            try:
                rsp = send_payment_invoice(product_id, id)
            except Product.DoesNotExist:
                return Response(data='None')
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
        try:
            if text == '/start':
                data.update(
                    {'text': 'Add this bot as an Admin to your channel : BOT_VERSION[2.0]'})
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

            elif text == 'Add a new product':
                try:
                    temp = TempData.objects.create(current_user=chat_id)
                    data.update({'text': questions[temp.question_index]})
                    temp.question_index = temp.question_index + 1
                    temp.save()
                except IntegrityError:
                    temp = TempData.objects.get(current_user=chat_id)
                    data.update({'text': questions[temp.question_index]})
                    temp.question_index = temp.question_index + 1
                    temp.save()
                    # data.update({'text': 'Wrong Response'})

                rsp = shop_bot_request(data)
                print(rsp)

            elif TempData.objects.filter(current_user=chat_id).exists() and TempData.objects.filter(current_user=chat_id)[0].question_index > 0 and TempData.objects.filter(current_user=chat_id)[0].question_index < len(questions):
                temp = TempData.objects.filter(current_user=chat_id)[0]
                try:
                    if temp.question_index == 1:
                        product_id = save_product_info(
                            {questions[temp.question_index-1]: text})
                        temp.current_product_id = product_id
                    else:
                        product_id = temp.current_product_id
                        save_product_info(
                            {questions[temp.question_index-1]: text}, product_id)
                except ValueError:
                    data.update({"text": "Please enter a valid price"})
                    rsp = shop_bot_request(data)
                    return Response(data='Done')

                data.update({'text': questions[temp.question_index]})
                temp.question_index += 1
                temp.save()
                rsp = shop_bot_request(data)
                print(rsp)

            elif TempData.objects.filter(current_user=chat_id).exists() and TempData.objects.filter(current_user=chat_id)[0].question_index == len(questions):
                try:
                    image_id = request.data.get('message').get('photo')[
                        2].get('file_id')
                    image_width = request.data.get('message').get('photo')[
                        2].get('width')
                    image_height = request.data.get('message').get('photo')[
                        2].get('height')
                except TypeError:
                    temp = TempData.objects.filter(
                        current_user=chat_id)[0]
                    temp.delete()
                    return Response(data='Done')

                image = {'file_id': image_id,
                         'width': image_width, 'height': image_height}
                temp = TempData.objects.filter(
                    current_user=chat_id)[0]

                product_id = temp.current_product_id

                save_product_info(
                    {questions[temp.question_index-1]: image}, product_id)

                temp.question_index = 0
                temp.save()
                data.update({'text': 'Product has been added succesfully',
                            'buttons': ['Post to Channel']})
                rsp = shop_bot_request(data)
                print(rsp)

            elif TempData.objects.filter(current_user=chat_id).exists() and TempData.objects.get(current_user=chat_id).question_index == 0 and text == 'Post to Channel':
                post_data = {}
                temp = TempData.objects.filter(
                    current_user=chat_id)[0]
                product_id = temp.current_product_id
                post_data.update(
                    {'chat_id': chat_id, 'product_id': product_id})

                data = {
                    'chat_id': chat_id,
                    'text': "Product has been posted to your channel.",
                    'buttons': ['Add a new product', 'List all products']
                }

                try:
                    rsp = shop_bot_channel_post(post_data)
                    if rsp.status_code != 200:
                        print(rsp.json())
                        data = {
                            'chat_id': chat_id,
                            'text': "🛑 Failed to post the product to your channel. Please try again. 🛑",
                            'buttons': ['Add a new product', 'List all products']
                        }
                except Product.DoesNotExist:
                    print("The Product Doesn't exist")
                    data = {
                        'chat_id': chat_id,
                        'text': "🛑 Failed to post the product to your channel. Please try again. 🛑",
                        'buttons': ['Add a new product', 'List all products']
                    }

                product_info = {}

                rsp = shop_bot_request(data)
                temp.delete()
                print(rsp)
        except TempData.DoesNotExist:
            data = {
                'chat_id': chat_id,
                'text': "An error has occured",
                'buttons': ['Add a new product', 'List all products']
            }

            rsp = shop_bot_request(data)

    return Response(data='Done')
