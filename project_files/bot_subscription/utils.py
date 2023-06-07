import requests
from . import data

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import FeedgramSubscription, FeedgramFeature
from personal_feed_bot.models import BotUser

proxy = settings.PROXY


def answer_callback_query(id):
    url = f'https://api.telegram.org/bot{data.SUB_BOT_TOKEN}/answerPreCheckoutQuery'
    rq_data = {
        'pre_checkout_query_id': id,
        'ok': True
    }
    rsp = requests.post(url=url, json=rq_data, proxies=settings.PROXY)
    return rsp.json()


def create_invoice(invoice_code):
    codes = invoice_code.split('-')

    bot_name = codes[0]
    sub_level = codes[1]
    sub_period = codes[2]

    inv_data = FeedgramFeature.objects.get(sub_name=sub_level)
    price = inv_data.price if sub_period == "monthly" else inv_data.price * 10

    invoice_data = {
        'title': inv_data.invoice_title,
        'description': inv_data.invoice_desc,
        'provider_token': data.CHAPA_SUB_BOT,
        'payload': {
            'bot_name': inv_data.bot_name,
            'sub_level': inv_data.sub_name,
            'sub_period': sub_period},

        'currency': 'ETB',
        'photo_width': 500,
        'photo_height': 500,
        'photo_url': settings.HOST_URL + 'media/' + str(inv_data.poster_image),
        # 'need_phone_number': True,
        'protect_content': True,
        'prices': [
            {
                'label': 'Payment Amount',
                'amount': price * 100,
            },
        ]
    }

    return invoice_data


def send_payment_invoice(invoice_code, chat_id):
    url = f'https://api.telegram.org/bot{data.SUB_BOT_TOKEN}/sendinvoice'
    invoice_data = create_invoice(invoice_code)
    invoice_data.update({'chat_id': chat_id})
    rsp = requests.post(url=url, json=invoice_data, proxies=proxy)
    print("From utils.send_payment_invoice", rsp.json())
    return rsp.json()


def create_feedgram_subscription(chat_id, data):
    chat_id = str(chat_id)
    bot_user = BotUser.objects.get(user_id=chat_id)

    sub_period = data.get('sub_period')
    sub_period_num = {'monthly': 30, 'yearly': 365}[sub_period]
    sub_level = data.get('sub_level')
    sub_level_object = FeedgramFeature.objects.get(sub_name=sub_level)

    try:
        bot_user.subscription.sub_level = sub_level_object
        bot_user.sub_period = sub_period
        bot_user.subscription.exp_date = timezone.now() + timedelta(days=sub_period_num)
        bot_user.subscription.save()
        return bot_user.subscription
    except BotUser.subscription.RelatedObjectDoesNotExist:
        exp_date = timezone.now() + timedelta(days=sub_period_num)
        subscription = FeedgramSubscription.objects.create(
            bot_user=bot_user, sub_level=sub_level_object, sub_period=sub_period, exp_date=exp_date)
        return subscription


SUB_FUNS = {
    'feedgram': create_feedgram_subscription
}
