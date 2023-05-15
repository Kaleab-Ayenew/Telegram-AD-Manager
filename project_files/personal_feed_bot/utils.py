import requests
from django.conf import settings
from modules.global_utils.utils import BotMessage, bot_request
from .models import BotUser, ConnectedChannels, TempData, FeedChannel
from more_itertools import batched

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
    new_feed_channel = FeedChannel.objects.create(
        owner_user=bot_user, feed_channel_id=id, feed_channel_name=name, feed_channel_username=username)

    return new_feed_channel


def get_feed_channel_by_id(user_id, ch_id):
    user_id = str(user_id)
    ch_id = str(ch_id)
    bot_user = BotUser.objects.get(user_id=user_id)

    try:
        feed_channel = FeedChannel.objects.get(
            owner_user=bot_user, feed_channel_id=ch_id)
        return feed_channel
    except FeedChannel.DoesNotExist:
        return None


def get_feed_channel_by_name(user_id, ch_name):
    bot_user = BotUser.objects.get(user_id=user_id)
    try:
        feed_channel = FeedChannel.objects.get(
            owner_user=bot_user, feed_channel_name=ch_name)
        return feed_channel
    except FeedChannel.DoesNotExist:
        return None


def list_feed_channels(user_id):
    bot_user = BotUser.objects.get(user_id=user_id)
    feed_channels = FeedChannel.objects.filter(owner_user=bot_user)
    return list(feed_channels)


def remove_feed_channel(user_id, ch_id):
    ch_id = str(ch_id)
    bot_user = BotUser.objects.get(user_id=user_id)
    feed_channel = FeedChannel.objects.get(
        owner_user=bot_user, feed_channel_id=ch_id)
    feed_channel.delete()
    # return bot_user


def add_connected_channel(user_id, feed_ch_id, channel_username):

    owner_user = BotUser.objects.get(user_id=user_id)
    feed_ch = FeedChannel.objects.get(feed_channel_id=feed_ch_id)
    connection = ConnectedChannels.objects.create(
        owner_user=owner_user, channel_username=channel_username, feed_channel=feed_ch)
    connection.save()
    return connection


def get_connected_channel(user_id, channel_username, feed_channel_id=None):
    owner_user = BotUser.objects.get(user_id=user_id)
    try:
        if feed_channel_id:
            connection = ConnectedChannels.objects.get(
                owner_user=owner_user, channel_username=channel_username, feed_channel_id=feed_channel_id)
        else:
            connection = ConnectedChannels.objects.get(
                owner_user=owner_user, channel_username=channel_username)
        return connection
    except ConnectedChannels.DoesNotExist:
        return None


def list_connected_channel(user_id):
    owner_user = BotUser.objects.get(user_id=user_id)
    channel_list = ConnectedChannels.objects.filter(
        owner_user=owner_user)

    if channel_list.exists():
        return channel_list
    else:
        return None


def remove_connected_channel(user_id, channel_username):
    owner_user = BotUser.objects.get(user_id=user_id)
    connection = ConnectedChannels.objects.get(
        owner_user=owner_user, channel_username=channel_username)
    connection.delete()


def create_temp_data(user_id, form_name):

    temp_data = TempData.objects.create(
        active_user=user_id, form_name=form_name)
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


def split_list(l, n):
    new_list = [i for i in batched(l, n)]
    return new_list


def list_to_button(l, i=0):

    list_10 = split_list(l, 10)
    if (i+1) > len(list_10) or i < 0:
        i = 0

    button_list = []
    cut_list = list_10[i]
    _ = split_list(cut_list, 2)

    for b in _:
        btn = [{'text': t.channel_username} for t in b]
        button_list.append(btn)

    if (i+1) < len(list_10):
        button_list.append([{'text': 'More Channels'}])
    if i > 0:
        button_list.append([{'text': 'Previous Channels'}])
    button_list.append([{'text': 'Back to Home'}])

    return button_list


def normal_list_to_button(l, i=0):
    list_10 = split_list(l, 10)
    if (i+1) > len(list_10) or i < 0:
        i = 0

    button_list = []
    cut_list = list_10[i]
    _ = split_list(cut_list, 2)

    for b in _:
        btn = [{'text': t} for t in b]
        button_list.append(btn)
    return button_list
