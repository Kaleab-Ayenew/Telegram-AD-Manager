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
    temp_seller.save()

    send_mail(
        "Verification Code",
        f"Dear SUQLINK seller, your email verification code is: {code}",
        "kalishayish16@gmail.com",
        [temp_seller.seller_email],
        fail_silently=False
    )


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
        "return_url": f"http://localhost:3000/purchased/{transaction_ref}",

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
            sold_product=sold_product, chapa_transaction_ref=transaction_ref)
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
