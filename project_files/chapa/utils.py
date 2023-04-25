import uuid
import requests
import hashlib
import hmac
import uuid
import json
import io
from django.conf import settings
from django.core.files import File
from .models import Product

CHAPA_BOT_TOKEN = "5842793769:AAHp5rNorcAFZngQzYiXNqm3D-5Iic3-wg0"
SHOP_BOT_TOKEN = "6138416100:AAFewlGAuGXrSwQGRWmFBbabCVRVks0S1Pc"
CHAPA_PAYMENT_TOKEN = "6141645565:TEST:PDTwkkww6SQb92RDYIok"
CHAPA_PRIVATE_KEY = "CHASECK_TEST-gXk6cDFDnUpveorEF5UTnkeAXxjvICwu"
CURRENCY = "ETB"

HOST_URL = 'https://ubuntu-vps.kal-dev.com' if settings.PROD else 'https://0a16-196-191-221-176.ngrok-free.app'

CALLBACK_URL = HOST_URL + "/chapa/callback/"
CHAPA_URL = "https://api.chapa.co/v1/transaction/initialize"
WEBHOOK_SECRET = '792F423F4528482B4D6251655468576D'

proxy = None if settings.PROD else {
    'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}


def request_payment(data):

    data = {
        "amount": data['amount'],
        "currency": CURRENCY,
        "callback_url": CALLBACK_URL,
        "email": data['email'],
        "first_name": data['fname'],
        "last_name": data['lname'],
        "tx_ref": str(uuid.uuid4()),
        "customization[title]": "Payment for my favourite merchant",
        "customization[description]": "I love online payments"
    }

    headers = {
        'Authorization': f'Bearer {CHAPA_PRIVATE_KEY}',
        'Content-Type': 'application/json'
    }
    rsp = requests.post(url=CHAPA_URL, json=data, headers=headers)
    return rsp.json()


def check_webhook_origin(hash):

    key = bytes(WEBHOOK_SECRET, encoding='utf-8')
    message = bytes(WEBHOOK_SECRET, encoding='utf-8')

    # Generate the hash.
    signature = hmac.new(
        key,
        message,
        hashlib.sha256
    ).hexdigest()

    return signature == hash


def send_payment_invoice(product_id, chat_id):
    url = f'https://api.telegram.org/bot{CHAPA_BOT_TOKEN}/sendinvoice'
    product_info = get_product_info(product_id)
    image_url = HOST_URL + '/media/' + str(product_info.product_image)
    data = {
        "chat_id": chat_id,
        'title': product_info.product_name,
        'description': product_info.product_description,
        'payload': {'info': 'Some info about the payment'},
        'provider_token': CHAPA_PAYMENT_TOKEN,
        'currency': 'ETB',
        'photo_width': product_info.image_width,
        'photo_height': product_info.image_height,
        'photo_url': image_url,
        # 'need_phone_number': True,
        'protect_content': True,
        'prices': [
            {
                'label': 'Payment Amount',
                'amount': product_info.product_price * 100,
            },
        ]
    }
    rsp = requests.post(url=url, json=data, proxies=proxy)
    return rsp.json()


def answer_callback_query(id):
    url = f'https://api.telegram.org/bot{CHAPA_BOT_TOKEN}/answerPreCheckoutQuery'
    data = {
        'pre_checkout_query_id': id,
        'ok': True
    }
    rsp = requests.post(url=url, json=data, proxies=proxy)
    return rsp.json()


def shop_bot_request(data):
    text = data.get('text')
    chat_id = data.get('chat_id')
    buttons = data.get('buttons')
    url = f'https://api.telegram.org/bot{SHOP_BOT_TOKEN}/sendmessage'
    post_data = {
        'chat_id': chat_id,
        'text': text, }
    if buttons:
        keyboard = {
            "keyboard": [[{'text': b}] for b in buttons]
        }
        post_data.update({'reply_markup': keyboard})

    rsp = requests.post(url=url, json=post_data, proxies=proxy)

    return rsp.json()


def save_product_info(data, product_id=None):

    url = f'https://api.telegram.org/bot{SHOP_BOT_TOKEN}/getfile'

    if data.get('Send product image?'):
        rsp = requests.post(url=url, json={'file_id': data.get(
            'Send product image?').get('file_id')}, proxies=proxy)

        print(rsp.json())
        if rsp.status_code == 200:
            file_path = rsp.json().get('result').get('file_path')
            photo_url = f'https://api.telegram.org/file/bot{SHOP_BOT_TOKEN}/{file_path}'
            photo_data = requests.get(photo_url, proxies=proxy)
            stream = io.BytesIO(photo_data.content)
            ext = file_path.split('.')[-1]
        else:
            stream = None
    else:
        stream = None

    if product_id:
        product = Product.objects.get(unique_id=product_id)
    else:
        product = Product.objects.create()

    name = data.get(
        'What is the product name?')
    desc = data.get('What is the product description?')
    price = data.get('What is the product price?')

    if name:
        product.product_name = name
    if desc:
        product.product_description = desc
    if price:
        product.product_price = price

    if stream:
        product.product_image.save(f'photo.{ext}', File(stream), save=False)
        product.image_height = data.get('Send product image?').get('height')
        product.image_width = data.get('Send product image?').get('width')
    product.save()

    return str(product.unique_id)


def get_product_info(product_id):

    product = Product.objects.get(unique_id=product_id)
    return product


def shop_bot_channel_post(data):
    product = Product.objects.get(unique_id=data.get('product_id'))
    product_id = str(product.unique_id)
    title = product.product_name
    description = product.product_description
    price = product.product_price
    image = HOST_URL + '/media/' + str(product.product_image)
    post_data = {
        'chat_id': '@suqshop',
        'caption': f'''🔸<strong>{title}</strong>🔸\n\n{description}\n\nPrice: {price}''',
        'photo': image,
        'parse_mode': 'html',
        'reply_markup': {
            'inline_keyboard': [[{'text': f'Buy for {price} birr', 'url': f'https://t.me/blackstorm_paybot?start={product_id}'}]]
        }}

    url = f'https://api.telegram.org/bot{SHOP_BOT_TOKEN}/sendphoto'

    rsp = requests.post(url=url, json=post_data, proxies=proxy)

    return rsp


def send_bot_msg(data, token):
    text = data.get('text')
    chat_id = data.get('chat_id')
    buttons = data.get('buttons')
    url = f'https://api.telegram.org/bot{token}/sendmessage'
    post_data = {
        'chat_id': chat_id,
        'text': text, }
    if buttons:
        keyboard = {
            "keyboard": [[{'text': b}] for b in buttons]
        }
        post_data.update({'reply_markup': keyboard})

    rsp = requests.post(url=url, json=post_data, proxies=proxy)

    return rsp.json()
