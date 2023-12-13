from googleapiclient.discovery import build
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from . import models
from . import config

import requests
from uuid import uuid4
from decimal import Decimal
import hashlib
import hmac
from secretpy import Caesar, alphabets as al

import magic


def check_file_type(f, test_file_type):
    file_type = magic.from_buffer(f.read(), mime=True)
    if file_type == test_file_type:
        return True
    else:
        return False


def send_verification_code(temp_seller):
    code = get_random_string(8)
    temp_seller.verification_code = code
    email_data = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": temp_seller.seller_email
                    }
                ]
            }
        ],
        "from": {
            "email": "verify@suqlink.com"
        },
        "subject": "SUQLINK VERIFICATION CODE",
        "content": [
            {
                "type": "text/plain",
                "value": f"Dear SUQLINK seller, your email verification code is: {code}"
            }
        ]
    }
    sendgrid_api_url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {config.SENDGRID_API_KEY}"
    }
    temp_seller.vcode_count = temp_seller.vcode_count + 1
    temp_seller.save()
    rsp = requests.post(url=sendgrid_api_url, json=email_data, headers=headers)
    if rsp.status_code != 202:
        print(
            f"[$] Error ##### A PROBLEM HAS OCCURED WHEN SENDING EMAIL TO {temp_seller.seller_email}")
    return None


def create_chapa_subaccount(seller):
    rq_url = f"https://api.chapa.co/{config.CHAPA_API_VERSION}/subaccount"
    headers = {
        'Authorization': f'Bearer {config.CHAPA_SECRET_TOKEN}',
        'Content-Type': 'application/json'
    }
    post_data = {"business_name": seller.seller_username, "account_name": seller.bank_account_full_name,
                 "account_number": seller.bank_account_number, "split_type": "percentage", "split_value": 0.1, "bank_code": str(seller.bank_provider.chapa_bank_id)}
    rsp = requests.post(url=rq_url, json=post_data, headers=headers)
    if rsp.ok:
        print(rsp.json())
        rsp_data = rsp.json()
        subaccount_id = rsp_data.get("data").get("subaccounts[id]")
        seller.chapa_subaccount_id = subaccount_id
        seller.save()
        return seller
    else:
        print(rsp.json())
        return None


def get_seller_from_user(user):
    try:
        seller = models.Seller.objects.get(main_user=user)
        return seller
    except models.Seller.DoesNotExist:
        return None


def get_split_payment_link(info, product, transaction_ref):
    rq_url = f"https://api.chapa.co/{config.CHAPA_API_VERSION}/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {config.CHAPA_SECRET_TOKEN}',
        'Content-Type': 'application/json'
    }
    post_data = {
        "amount": float(product.product_price),
        "currency": "ETB",
        "email": info.get("email"),
        "first_name": info.get("first_name"),
        "last_name": info.get("last_name"),
        "phone_number": info.get("phone_no"),
        "tx_ref": transaction_ref,
        "callback_url": f"{settings.HOST_URL}suqlink/payment/verify/{transaction_ref}/",
        "return_url": f"{config.SUQLINK_PRODUCT_DOMAIN}purchased/{transaction_ref}",

    }
    print("Payment Data", post_data)
    rsp = requests.post(url=rq_url, headers=headers, json=post_data)
    print("Payment Response", rsp.json())

    if rsp.status_code != 200:
        return None

    return rsp.json().get("data").get("checkout_url")


def get_all_products(seller):
    products = models.Product.objects.filter(product_seller=seller)
    return products.all()


def get_product_by_id(product_id):
    try:
        product = models.Product.objects.get(product_id=product_id)
        return product
    except models.Product.DoesNotExist:
        return None


def get_sale_by_tx_ref(transaction_ref):
    try:
        sale = models.Sale.objects.get(chapa_transaction_ref=transaction_ref)
        return sale
    except models.Sale.DoesNotExist:
        return None


def get_sales_by_user(user):
    sales = models.Sale.objects.filter(
        sold_product__product_seller__main_user=user, completed=True)
    return sales.all()


def get_sale_sum(user):
    sales = models.Sale.objects.filter(
        sold_product__product_seller__main_user=user, completed=True)
    total_sum = sales.aggregate(total_price=Sum('sold_product__product_price'))[
        'total_price']
    return total_sum


def verify_payment(transaction_ref):
    rq_url = f"https://api.chapa.co/{config.CHAPA_API_VERSION}/transaction/verify/{transaction_ref}"
    headers = {
        'Authorization': f'Bearer {config.CHAPA_SECRET_TOKEN}'
    }
    rsp = requests.get(url=rq_url, headers=headers)
    rsp_data = rsp.json()
    print(rsp_data)
    status = rsp_data.get("status")
    return status


def create_sale(sold_product, transaction_ref):
    if not models.Sale.objects.filter(chapa_transaction_ref=transaction_ref).exists():
        new_sale = models.Sale.objects.create(
            sold_product=sold_product, chapa_transaction_ref=transaction_ref, sale_price=sold_product.product_price)
        return new_sale
    else:
        return None


def create_download_link(sale):
    if models.TempDownloadLink.objects.filter(sale=sale).exists():
        return models.TempDownloadLink.objects.get(sale=sale)
    else:
        temp_link = models.TempDownloadLink.objects.create(sale=sale)
        return temp_link


def get_product_from_link(link_id):
    temp_link = get_object_or_404(models.TempDownloadLink, pk=link_id)
    return temp_link.sale.sold_product


def get_templink_by_id(link_id):
    temp_link = get_object_or_404(models.TempDownloadLink, pk=link_id)
    return temp_link


def update_seller_income(sale):
    current_total_income = sale.sold_product.product_seller.total_income
    current_sale_price = sale.sold_product.product_price
    seller_income_percent = 100 - config.CHARGE_PERCENT
    sale_income_for_seller = (current_sale_price * seller_income_percent) / 100
    sale_income_for_seller = round(sale_income_for_seller, 2)
    new_total_income = current_total_income + \
        Decimal(str(sale_income_for_seller))
    sale.sold_product.product_seller.total_income = new_total_income
    sale.sold_product.product_seller.save()


def get_admin_seller(username):
    admin = User.objects.filter(is_superuser=True, username=username).first()
    admin_seller = models.Seller.objects.get(main_user=admin)
    return admin_seller


def update_platform_income(sale):
    platform_seller = get_admin_seller(config.ADMIN_SELLER_USERNAME)
    current_total_income = platform_seller.total_income
    current_sale_price = sale.sold_product.product_price
    seller_income_percent = config.CHARGE_PERCENT
    sale_income_for_seller = (current_sale_price * seller_income_percent) / 100
    sale_income_for_seller = round(sale_income_for_seller, 2)
    new_total_income = current_total_income + \
        Decimal(str(sale_income_for_seller))
    platform_seller.total_income = new_total_income
    platform_seller.save()


def withdraw_to_bank(withdraw_info):
    rq_url = "https://api.chapa.co/v1/transfers"
    headers = {
        "Authorization": f"Bearer {config.CHAPA_SECRET_TOKEN}"
    }
    post_data = {
        "account_name": withdraw_info.bank_account_name,
        "account_number": withdraw_info.bank_account_number,
        "amount": float(withdraw_info.amount),
        "currency": "ETB",
        "beneficiary_name": withdraw_info.bank_account_name,
        "reference": withdraw_info.withdraw_reference,
        "bank_code": str(withdraw_info.chapa_bank.chapa_bank_id)
    }
    rsp = requests.post(url=rq_url, json=post_data, headers=headers)

    return rsp.json()


def get_withdraw_request(seller):
    withdraw_requests = models.WithdrawRequest.objects.filter(
        seller=seller, status='pending')
    if withdraw_requests.exists():
        return withdraw_requests.all()
    else:
        return None


def check_webhook_secret(chapa_signature):

    key = bytes(config.CHAPA_WEBHOOK_SECRET, encoding='utf-8')
    message = bytes(config.CHAPA_WEBHOOK_SECRET, encoding='utf-8')

    # Generate the hash.
    signature = hmac.new(
        key,
        message,
        hashlib.sha256
    ).hexdigest()

    return signature == chapa_signature


def get_withdrawal_by_reference(with_ref):
    try:
        with_req = models.WithdrawRequest.objects.get(
            withdraw_reference=with_ref)
        return with_req
    except models.WithdrawRequest.DoesNotExist:
        return None


def withdrawal_deduct(with_req):
    seller = with_req.seller
    current_total_income = seller.total_income
    withdraw_amount = with_req.amount
    seller.total_income = current_total_income - withdraw_amount
    seller.save()


def get_user_by_email(email):
    user = User.objects.filter(username=email)
    if user.exists():
        return user.first()
    else:
        return None


def login_user(username, password):
    user = authenticate(username=username, password=password)
    if user is not None:

        token, _ = Token.objects.get_or_create(user=user)
        rsp_data = {"username": uname, "token": token.key,
                    "uid": uname}
        return rsp_data
    else:
        return None


def get_token_by_seller(seller):
    token, _ = Token.objects.get_or_create(user=seller.main_user)
    return token.key


def get_chapa_bank_list():
    rq_url = f"https://api.chapa.co/v1/banks"
    headers = {
        'Authorization': f"Bearer {config.CHAPA_SECRET_TOKEN}"
    }
    rsp = requests.get(url=rq_url, headers=headers)
    return rsp.json()


def get_file_size(f):
    return None


def get_video_by_platform_id(platform_id):
    try:
        video = models.YoutubeVideo.objects.get(platform_id=platform_id)
        return video
    except:
        return None


def get_random_user_data(email, password):
    first_name = "Video"
    last_name = "Client"
    return {"first_name": first_name, "last_name": last_name, "email": email, "username": email, "password": password}


def get_video_client_from_main_user(user):
    try:
        client = models.YoutubeVideoClient.objects.get(main_user=user)
        return client
    except models.YoutubeVideoClient.DoesNotExist:
        return None


def user_has_purchased_video(main_user, video):
    client = get_video_client_from_main_user(main_user)
    video_purchase = models.YoutubeSale.objects.filter(
        video_buyer=client, sold_video=video, completed=True)
    return video_purchase.exists()


def get_client_purchased_videos(client):
    video_purchases = client.video_purchases.filter(completed=True).all()
    v_list = []

    for p in video_purchases:
        v_list.append(p.sold_video)

    return list(set(v_list))


def rot_encrypt(text):

    alphabet = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "abcdefghijklmnopqrstuvwxyz",

    ]
    key = 1
    final_enc = []
    for t in text:
        if t not in alphabet[1] and t not in alphabet[0]:
            final_enc.append(t)
        elif t in alphabet[0]:
            t_index = alphabet[0].find(t)
            new_t_index = t_index + key
            if new_t_index > 25:
                new_t_index = new_t_index - 26
            new_let = alphabet[0][new_t_index]
            final_enc.append(new_let)
        elif t in alphabet[1]:
            t_index = alphabet[1].find(t)
            new_t_index = t_index + key
            if new_t_index > 25:
                new_t_index = new_t_index - 26
            new_let = alphabet[1][new_t_index]
            final_enc.append(new_let)
    enc_text = ("").join(final_enc)
    return enc_text


def get_youtube_channel_info(channel_id):
    # Replace with your actual YouTube Data API v3 key
    api_key = 'AIzaSyDV8UqR7NxKJg6defUVdo73fUwLvup97sk'
    url = f'https://www.googleapis.com/youtube/v3/channels?id={channel_id}&part=snippet&key={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            channel_info = items[0]
            snippet = channel_info.get('snippet', {})

            info = {
                "title": snippet.get('title'),
                "id": channel_id,
                "description": snippet.get('description'),
                "thumbnail_url": snippet.get('thumbnails', {}).get('default', {}).get('url'),
            }
            return info
        else:
            return 'No data found for the provided channel ID.'
    else:
        return f'Error: {response.status_code}'


def get_ychannel_info(channel_id):
    api_key = 'AIzaSyDV8UqR7NxKJg6defUVdo73fUwLvup97sk'
    youtube = build('youtube', 'v3', developerKey=api_key)

    channel_response = youtube.channels().list(
        part='snippet',  # ,contentDetails,statistics',
        id=channel_id).execute()

    items = channel_response.get('items')
    if items:
        item = items[0]
        snippet = item['snippet']
        data = {
            "title": snippet.get('title'),
            "id": channel_id,
            # "description" : snippet.get('description'),
            "thumbnail_url": snippet.get('thumbnails')['default']['url'],
        }
        return data


def get_yvideo_status(video_id):

    api_key = 'AIzaSyDV8UqR7NxKJg6defUVdo73fUwLvup97sk'

    youtube = build('youtube', 'v3', developerKey=api_key)

    # Replace 'VIDEO_ID' with the ID of the video you're checking
    request = youtube.videos().list(
        part='status',
        id=video_id
    )
    response = request.execute()
    print(response)
    # Check the privacy status
    items = response.get('items')
    if items:
        item = items[0]
        privacy_status = item['status']['privacyStatus']
        print(f'The video is {privacy_status}.')
        return privacy_status


def get_youtube_video_info(video_id):
    # Replace with your actual YouTube Data API v3 key
    api_key = 'AIzaSyDV8UqR7NxKJg6defUVdo73fUwLvup97sk'
    url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,statistics&key={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            video_info = items[0]
            snippet = video_info.get('snippet', {})
            statistics = video_info.get('statistics', {})
            th_list = snippet.get('thumbnails', {})
            th_url = th_list.get("maxres") if th_list.get("maxres") else th_list.get(
                "standard") if th_list.get("standard") else th_list.get("high")
            ch_id = snippet.get("channelId")
            info = {
                'title': snippet.get('title'),
                'thumbnail_url': th_url.get("url"),
                'views': statistics.get('viewCount'),
                'likes': statistics.get('likeCount'),
                'description': snippet.get('description'),
                "ch_info": get_youtube_channel_info(ch_id)
            }
            return info
        else:
            return 'No data found for the provided video ID.'
    else:
        return f'Error: {response.status_code}'

# Example usage:
# video_info = get_youtube_video_info('VIDEO_ID_HERE')
# print(video_info)


def get_video_info(video_id):
    api_key = 'AIzaSyDV8UqR7NxKJg6defUVdo73fUwLvup97sk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    print(get_yvideo_status(video_id))
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    # print(response)
    if response['items']:
        print(response)

        item = response['items'][0]
        ch_info = get_ychannel_info(item['snippet']['channelId'])
        title = item['snippet']['title']
        description = item['snippet']['description']
        th_list = item.get('snippet').get('thumbnails')
        thumbnail_url = th_list.get("maxres") if th_list.get("maxres") else th_list.get(
            "standard") if th_list.get("standard") else th_list.get("high")
        views = item['statistics']['viewCount']
        likes = item['statistics']['likeCount']
        print(thumbnail_url)
        return {
            'title': title,
            'thumbnail_url': thumbnail_url.get("url"),
            'views': views,
            'likes': likes,
            'ch_info': ch_info,
            'description': description
        }
    else:
        return None


def get_video_payment_link(info, video, transaction_ref):
    rq_url = f"https://api.chapa.co/{config.CHAPA_API_VERSION}/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {config.CHAPA_SECRET_TOKEN}',
        'Content-Type': 'application/json'
    }
    post_data = {
        "amount": float(video.video_price),
        "currency": "ETB",
        "phone_number": info.get("phone_no"),
        "tx_ref": transaction_ref,
        "callback_url": f"{settings.HOST_URL}suqlink/yvideos/c/payment/verify/{transaction_ref}",
        "return_url": f"{config.YT_VIDEO_DOMAIN}myvideos",

    }
    print("Payment Data", post_data)
    rsp = requests.post(url=rq_url, headers=headers, json=post_data)
    print("Payment Response", rsp.json())

    if rsp.status_code != 200:
        return None

    return rsp.json().get("data").get("checkout_url")


def create_video_sale(sold_video, video_buyer, tx_ref):
    if not models.YoutubeSale.objects.filter(chapa_transaction_ref=tx_ref).exists():
        new_video_sale = models.YoutubeSale.objects.create(
            sold_video=sold_video, video_buyer=video_buyer, chapa_transaction_ref=tx_ref, sale_price=sold_video.video_price)
        return new_video_sale
    else:
        return None


def get_video_sale_by_tx_ref(transaction_ref):
    try:
        sale = models.YoutubeSale.objects.get(
            chapa_transaction_ref=transaction_ref)
        return sale
    except models.YoutubeSale.DoesNotExist:
        return None


def update_video_seller_income(sale):
    current_total_income = sale.sold_video.video_owner.total_income
    current_sale_price = sale.sold_video.video_price
    seller_income_percent = 100 - config.CHARGE_PERCENT
    sale_income_for_seller = (current_sale_price * seller_income_percent) / 100
    sale_income_for_seller = round(sale_income_for_seller, 2)
    new_total_income = current_total_income + \
        Decimal(str(sale_income_for_seller))
    sale.sold_video.video_owner.total_income = new_total_income
    sale.sold_video.video_owner.save()


def update_video_platform_income(sale):
    platform_seller = get_admin_seller(config.ADMIN_SELLER_USERNAME)
    current_total_income = platform_seller.total_income
    current_sale_price = sale.sold_video.video_price
    seller_income_percent = config.CHARGE_PERCENT
    sale_income_for_seller = (current_sale_price * seller_income_percent) / 100
    sale_income_for_seller = round(sale_income_for_seller, 2)
    new_total_income = current_total_income + \
        Decimal(str(sale_income_for_seller))
    platform_seller.total_income = new_total_income
    platform_seller.save()


def get_video_sales_by_user(user):
    seller = get_seller_from_user(user)
    sales = models.YoutubeSale.objects.filter(
        sold_video__video_owner__main_user=user, completed=True).all()
    return sales
