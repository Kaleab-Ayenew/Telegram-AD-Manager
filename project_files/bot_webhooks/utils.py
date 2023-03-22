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
    msg = f"""
    <strong>Dear {name}</strong> ምዝገባዎ በስኬት ተጠናቋል። ተከታዩን ሊንክ ለወዳጆችዎ ሼር በማድረግ ውድድሩን መጀመር ይችላሉ።
    
🔴{link}

መልካም እድል!!!
    """

    data = {
        "text": msg,
        "chat_id": int(user_id),
        "parse_mode": parser
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendmessage"

    rsp = requests.post(url=url, data=data, proxies={
                        "http": "http://127.0.0.1:6666", "https": "http://127.0.0.1:6666"})
    return rsp.json()
