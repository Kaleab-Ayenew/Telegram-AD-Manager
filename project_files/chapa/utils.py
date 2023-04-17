import uuid
import requests


CHAPA_PRIVATE_KEY = "CHASECK_TEST-gXk6cDFDnUpveorEF5UTnkeAXxjvICwu"
CURRENCY = "ETB"
CALLBACK_URL = "https://54d0-196-191-221-236.ngrok-free.app/chapa/callback/"
CHAPA_URL = "https://api.chapa.co/v1/transaction/initialize"


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
