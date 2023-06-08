import requests
from django.conf import settings
from modules.global_utils.utils import BotMessage, bot_request
from .models import BotUser, ConnectedChannels, TempData, FeedChannel
from bot_subscription.models import FeedgramSubscription, FeedgramFeature
from more_itertools import batched
from . import data

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
    message = BotMessage(user=user_id, message=text, parse_mode='html')
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(BOT_TOKEN)
    print(rsp.json())


def send_image(user_id, text, image_url, buttons=None, inline_buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text,
                         image_url=image_url, parse_mode='html')
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    if inline_buttons:
        message.add_keyboard(keyboard_type='inline_keyboard',
                             data_array=inline_buttons)
    rsp = message.send_image(BOT_TOKEN)
    print(rsp.json())


def create_user(user_id, first_name):

    new_user = BotUser.objects.create(
        user_id=user_id, user_first_name=first_name)

    return new_user


def get_user(user_id) -> BotUser:

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
                owner_user=owner_user, channel_username=channel_username, feed_channel=feed_channel_id)
        return connection
    except ConnectedChannels.DoesNotExist:
        return None


def list_connected_channel(user_id):
    user_id = str(user_id)
    owner_user = BotUser.objects.get(user_id=user_id)
    channel_list = ConnectedChannels.objects.filter(
        owner_user=owner_user)

    if channel_list.exists():
        return channel_list
    else:
        return None


def list_connected_channel_by_feed(user_id, feed_ch_id):
    user_id = str(user_id)
    feed_ch_id = str(feed_ch_id)
    owner_user = BotUser.objects.get(user_id=user_id)
    channel_list = ConnectedChannels.objects.filter(
        owner_user=owner_user, feed_channel=feed_ch_id)

    if channel_list.exists():
        return channel_list
    else:
        return None


def remove_connected_channel(user_id, channel_username, feed_channel_id=None):
    owner_user = BotUser.objects.get(user_id=user_id)
    connection = ConnectedChannels.objects.get(
        owner_user=owner_user, channel_username=channel_username, feed_channel=feed_channel_id)
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
    i = 0 if i == 0 else i-1
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


def get_user_sub_level(chat_id) -> FeedgramFeature:
    chat_id = str(chat_id)
    bot_user = get_user(user_id=chat_id)

    try:
        user_sub = bot_user.subscription
        sub_level = user_sub.sub_level
    except BotUser.subscription.RelatedObjectDoesNotExist:
        sub_level = FeedgramFeature.objects.get(sub_name='free')

    return sub_level


def check_feed_limit(chat_id):

    chat_id = str(chat_id)
    bot_user = get_user(user_id=chat_id)
    feed_channels = FeedChannel.objects.filter(owner_user=bot_user)

    print("Feed Channels: ", len(feed_channels))

    try:
        user_sub = bot_user.subscription
        sub_level = user_sub.sub_level
    except BotUser.subscription.RelatedObjectDoesNotExist:
        sub_level = FeedgramFeature.objects.get(sub_name='free')

    print("Allowed Channels: ", sub_level.super_channels)

    return len(feed_channels) < sub_level.super_channels


def check_connection_limit(chat_id, feed_ch_id):

    chat_id = str(chat_id)
    bot_user = get_user(user_id=chat_id)
    feed_channel = get_feed_channel_by_id(chat_id, feed_ch_id)
    connected_channels = ConnectedChannels.objects.filter(
        owner_user=bot_user, feed_channel=feed_channel)

    print("Connected Channels: ", len(connected_channels))

    try:
        user_sub = bot_user.subscription
        sub_level = user_sub.sub_level
    except BotUser.subscription.RelatedObjectDoesNotExist:
        sub_level = FeedgramFeature.objects.get(sub_name='free')

    print("Allowed Channels: ", sub_level.channel_per_superchannel)

    return len(connected_channels) < sub_level.channel_per_superchannel


def send_subscription_info(chat_id):
    features = FeedgramFeature.objects.all()
    content = [
        f"<b>{f.invoice_title}</b>\n\n{f.invoice_desc}" for f in features]
    content = "\n\n".join(content)
    image_url = 'https://blackstormtech.com/big-logo-card.png'

    text = f"<b>Subscription Plans</b>:\n\n{content}"
    btns = data.SUB_BUTTONS
    send_image(user_id=chat_id, text=text, image_url=image_url, buttons=btns)


def send_subscription(chat_id, sub_level):
    sub = FeedgramFeature.objects.get(sub_name=sub_level)
    monthly_url = f"https://t.me/blackstorm_sub_bot?start=feedgram-{sub_level}-monthly"
    yearly_url = f"https://t.me/blackstorm_sub_bot?start=feedgram-{sub_level}-yearly"
    image_url = settings.HOST_URL + 'media/' + str(sub.poster_image)
    text = f"{sub.invoice_title}\n\n{sub.invoice_desc}\n\n"
    monthly_price = sub.price
    yearly_price = sub.price * 10
    btns = [
        [{'text': f'Buy Monthly ({monthly_price} birr)', 'url': monthly_url},
         {'text': f'Buy Yearly ({yearly_price} birr)', 'url': yearly_url}]
    ]
    print("This is text", text)

    send_image(user_id=chat_id, text=text,
               image_url=image_url, inline_buttons=btns)


def get_homepage_info(chat_id):
    chat_id = str(chat_id)
    bot_user = get_user(user_id=chat_id)
    feed_channels = FeedChannel.objects.filter(owner_user=bot_user)
    sub_level = get_user_sub_level(chat_id)

    sub_info = {
        'level': sub_level.sub_name,
        'exp_in': 'Never' if sub_level.sub_name == 'free' else f"{bot_user.subscription.days_left()} days",
        'sup_chan_limit': sub_level.super_channels,
        'conn_limit': sub_level.channel_per_superchannel

    }

    connected_ch = {}
    for f in feed_channels:
        f_name = f.feed_channel_name
        f_conn_chs = ["   ▫️ " + c.channel_username for c in ConnectedChannels.objects.filter(
            owner_user=bot_user, feed_channel=f)]
        connected_ch.update({f_name: f_conn_chs})

    sub_info_text = f"❇️ <b>Subscription Info:</b>\n\n  🔹 Plan: {sub_info['level']}\n  🔹 Expires In: {sub_info['exp_in']}\n  🔹 Allowed Super Channels: {sub_info['sup_chan_limit']}\n  🔹 Channels per Super Channel: {sub_info['conn_limit']}"

    sup_ch_no = len(feed_channels)
    join_list = lambda l, c='\n': c.join(l)
    sup_ch_list = "\n".join(
        [f' 🔸 {s_name} | {len(connected_ch[s_name])} channels\n      {join_list(connected_ch[s_name])}\n' for s_name in connected_ch.keys()])

    home_page_info = f"Welcome back 💖 <b>{bot_user.user_first_name}</b>\n\n❇️ <b>Super Channels: {sup_ch_no} channels</b>\n\n{sup_ch_list}\n{sub_info_text}"

    return home_page_info
