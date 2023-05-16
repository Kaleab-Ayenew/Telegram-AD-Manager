import requests
from django.conf import settings


class BotMessage():
    proxy = None if settings.PROD else {
        'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}

    def __init__(self, user, message, parse_mode=None):
        self.user = user
        self.message = message
        self.reply_markup = None
        self.proxy = None if settings.PROD else {
            'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}

    def to_dict(self):
        self.final_data = {'chat_id': self.user, 'text': self.message}
        if self.reply_markup:
            self.final_data.update({'reply_markup': self.reply_markup})
        return self.final_data

    def add_keyboard(self, keyboard_type, data_array):
        self.reply_markup = {
            keyboard_type: data_array
        }

    def send(self, bot_token):
        url = f'https://api.telegram.org/bot{bot_token}/sendmessage'
        data = self.to_dict()
        rsp = requests.post(url=url, json=data, proxies=self.proxy)
        return rsp


def bot_request(token, endpoint, data):
    url = f'https://api.telegram.org/bot{token}/{endpoint}'
    rsp = requests.post(url=url, json=data, proxies=settings.PROXY)
    return rsp


def set_webhook(token, url):
    rsp = bot_request(token, 'setwebhook', {'url': url})
    print(rsp.json())
    return rsp.json()
