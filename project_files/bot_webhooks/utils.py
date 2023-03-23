from . models import TelegramUser
from django.conf import settings
import requests


def get_user(user_id):
    try:
        user = TelegramUser.objects.get(tg_user_id=user_id)
    except TelegramUser.DoesNotExist:
        user = None

    return user


def new_user_rsp(new_user):
    name = new_user.first_name
    user_id = new_user.tg_user_id
    num = new_user.invited_number
    bot_token = settings.INVITE_BOT_TOKEN
    link = f"https://t.me/tze_invite_bot?start={user_id}"
    parser = "HTML"
    keyboard = {
        "keyboard": [
            [{"text": "check_user_stat"}],
            [{"text": "list_invited_users"}]
        ]
    }
    msg = f"""
    <strong>Dear {name}</strong> ምዝገባዎ በስኬት ተጠናቋል። ተከታዩን ሊንክ ለወዳጆችዎ ሼር በማድረግ ውድድሩን መጀመር ይችላሉ።
    
🔸 {link}

መልካም እድል!!!
    """

    data = {
        "text": msg,
        "chat_id": int(user_id),
        "parse_mode": parser,
        "reply_markup": keyboard
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendmessage"

    rsp = requests.post(url=url, json=data, proxies={
                        "http": "http://127.0.0.1:6666", "https": "http://127.0.0.1:6666"})
    return rsp.json()


def user_stat_rsp(user):
    name = user.first_name
    user_id = user.tg_user_id
    num = user.invited_number
    bot_token = settings.INVITE_BOT_TOKEN
    link = f"https://t.me/tze_invite_bot?start={user_id}"
    parser = "HTML"
    rank = list(TelegramUser.objects.all()).index(user) + 1

    keyboard = {
        "keyboard": [
            [{"text": "መረጃዎትን ለመመልከት"}],
            [{"text": "የጋበዟቸው ሰዎች ዝርዝር"}]
        ]
    }

    msg = f"""
<strong>Dear {name}</strong> እስካሁን ያለዎት መረጃ ይህን ይመስላል:
    
🔸 እስካሁን የጋበዟቸው ሰዎች: {num}
🔸 ደረጃ: {rank}

🔴{link}

መልካም እድል!!!
    """

    data = {
        "text": msg,
        "chat_id": int(user_id),
        "parse_mode": parser,
        "reply_markup": keyboard
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendmessage"

    rsp = requests.post(url=url, json=data, proxies={
                        "http": "http://127.0.0.1:6666", "https": "http://127.0.0.1:6666"})
    return rsp.json()


def empty_rsp(user_id):
    msg = "ከተከታዩ ዝርዝር አንዱን ይምረጡ"
    parser = "HTML"
    bot_token = settings.INVITE_BOT_TOKEN
    keyboard = {
        "keyboard": [
            [{"text": "መረጃዎትን ለመመልከት"}],
            [{"text": "የጋበዟቸው ሰዎች ዝርዝር"}]
        ]
    }
    data = {
        "text": msg,
        "chat_id": int(user_id),
        "parse_mode": parser,
        "reply_markup": keyboard
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendmessage"

    rsp = requests.post(url=url, json=data, proxies={
                        "http": "http://127.0.0.1:6666", "https": "http://127.0.0.1:6666"})
    return rsp.json()
