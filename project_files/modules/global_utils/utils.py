import requests
from django.conf import settings
import os
from pathlib import Path


class BotMessage():
    proxy = None if settings.PROD else {
        'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}

    def __init__(self, user, message, image_url=None, parse_mode=None):
        self.user = user
        self.message = message
        self.reply_markup = None
        self.parse_mode = parse_mode
        self.image_url = image_url
        self.proxy = None if settings.PROD else {
            'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}

    def to_dict(self):
        if self.image_url:
            self.final_data = {'chat_id': self.user,
                               'caption': self.message, 'photo': self.image_url}
        else:
            self.final_data = {'chat_id': self.user, 'text': self.message}
        if self.parse_mode:
            self.final_data.update(
                {'parse_mode': self.parse_mode})
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

    def send_image(self, bot_token):
        url = f'https://api.telegram.org/bot{bot_token}/sendphoto'
        data = self.to_dict()
        print("I am sending this", data)
        rsp = requests.post(url=url, json=data, proxies=self.proxy)
        return rsp


def send_message(user_id, text, bot_token, buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text)
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(bot_token)
    print(rsp.json())


def bot_request(token, endpoint, data):
    url = f'https://api.telegram.org/bot{token}/{endpoint}'
    rsp = requests.post(url=url, json=data, proxies=settings.PROXY)
    return rsp


def set_webhook(token, url):
    rsp = bot_request(token, 'setwebhook', {'url': url})
    print(rsp.json())
    return rsp.json()


def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


def _remove_path(path):
    p = Path(path)
    os.rmdir(p.parent.absolute())
