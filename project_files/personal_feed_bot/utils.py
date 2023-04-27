import requests
from django.conf import settings
from modules.global_utils.utils import BotMessage, bot_request
from .models import BotUser, ConnectedChannels, TempData

proxy = None if settings.PROD else {
    'http': 'http://127.0.0.1:6666', 'https': 'http://127.0.0.1:6666'}

BOT_TOKEN = settings.FEEDGRAM_BOT_TOKEN


def ping(user_id, first_name):
    message = BotMessage(user=user_id, message=f"Hi {first_name}")
    message.add_keyboard(keyboard_type='keyboard', data_array=[
                         [{'text': 'Add Channels'}, {'text': 'List channels'}], [{'text': 'Placeholder'}]])
    rsp = message.send(BOT_TOKEN)
    print(rsp.json())


def send_message(user_id, text, buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text)
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(BOT_TOKEN)
    print(rsp.json())


def create_user(user_id, first_name):

    new_user = BotUser.objects.create(
        user_id=user_id, user_first_name=first_name)
    new_user.save()
    return new_user


def get_user(user_id):

    try:
        user = BotUser.objects.get(pk=user_id)
        return user
    except BotUser.DoesNotExist:
        return None


def add_feed_channel(user_id, id, name, username):

    bot_user = BotUser.objects.get(user_id=user_id)
    bot_user.feed_channel_id = id
    bot_user.feed_channel_name = name
    bot_user.feed_channel_username = username
    bot_user.save()
    return bot_user


def remove_feed_channel(user_id):

    bot_user = BotUser.objects.get(user_id=user_id)
    bot_user.feed_channel_id = None
    bot_user.feed_channel_name = None
    bot_user.feed_channel_username = None
    bot_user.save()
    return bot_user


def add_connected_channel(user_id, channel_username):

    owner_user = BotUser.objects.get(user_id=user_id)
    connection = ConnectedChannels.objects.create(
        owner_user=owner_user, channel_username=channel_username)
    connection.save()
    return connection


def get_connected_channel(user_id, channel_username):
    owner_user = BotUser.objects.get(user_id=user_id)
    try:
        connection = ConnectedChannels.objects.get(
            owner_user=owner_user, channel_username=channel_username)
        return connection
    except ConnectedChannels.DoesNotExist:
        return None


def remove_connected_channel(user_id, channel_username):
    owner_user = BotUser.objects.get(user_id=user_id)
    connection = ConnectedChannels.objects.get(
        owner_user=owner_user, channel_username=channel_username)
    connection.delete()


def create_temp_data(user_id):

    temp_data = TempData.objects.create(active_user=user_id)
    temp_data.save()
    return temp_data


def get_temp_data(user_id):
    try:
        temp_data = TempData.objects.get(active_user=user_id)
        return temp_data
    except TempData.DoesNotExist:
        return None


def remove_temp_data(user_id):
    temp_data = TempData.objects.get(active_user=user_id)
    temp_data.delete()


def check_channel(username):
    username = "@" + username if username[0] != "@" else username
    rsp = bot_request(BOT_TOKEN, 'getchat', {'chat_id': username})
    if rsp.status_code == 200:
        return True
    print(rsp.json())
    return False


def populate_form(index, user_id, data):
    if index == 0:
        conn = add_connected_channel(user_id, data)
