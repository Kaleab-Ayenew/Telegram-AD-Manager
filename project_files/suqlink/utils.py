from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings

from . import models
from . import config

import requests
from uuid import uuid4


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
        "amount": product.product_price,
        "currency": "ETB",
        "email": info.get("email"),
        "first_name": info.get("first_name"),
        "last_name": info.get("last_name"),
        "phone_number": info.get("phone_no"),
        "tx_ref": transaction_ref,
        "callback_url": f"{settings.HOST_URL}suqlink/payment/verify/{transaction_ref}/",
        "return_url": f"https://suqlink.com/purchased/{transaction_ref}",
        "subaccounts[id]": str(product.product_seller.chapa_subaccount_id)
    }
    print("Payment Data", post_data)
    rsp = requests.post(url=rq_url, headers=headers, json=post_data)
    print("Payment Response", rsp.json())

    if rsp.status_code != 200:
        return None

    return rsp.json().get("data").get("checkout_url")


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
