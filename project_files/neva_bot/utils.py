from modules.global_utils.utils import bot_request
from modules.global_utils.utils import BotMessage
from googletrans import Translator
from telegraph import Telegraph

ADMIN_BOT_TOKEN = "5472637663:AAGIe33kLgRAzmehEagq6TBmg3gTCvRsZ5A"


def edit_message(chat_id, msg_id, text=None, caption=None, buttons=None):
    print("Edit Message Was Triggered")
    d = {"chat_id": chat_id, "message_id": msg_id, "parse_mode": "html", "reply_markup": {
        'inline_keyboard': buttons
    }}

    if text:
        d.update({'text': text})

    else:
        d.update({'caption': caption})

    end_pt = "editMessageText" if text else "editMessageCaption"
    print(end_pt, d)
    rsp = bot_request(token=ADMIN_BOT_TOKEN,
                      endpoint=end_pt, data=d)
    print(rsp.json())
    return rsp.json()


def send_message(user_id, text, token, buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text, parse_mode='html')
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(token)
    print(rsp.json())


def translate(text):
    ts = Translator()
    tran_text = ts.translate(text, src="en", dest="am")
    return tran_text.text


def post_to_telegraph(content):
    title = "Neva Computers"
    author = "Neva Computers"

    tg = Telegraph(
        access_token="27d13e457124a0bd1580c92f7b54aab846157780a1feb06e8b7c48637d95")
    c = "\n".join([f"<p>{p}</p>" for p in content.split('\n')])
    rsp = tg.create_page(
        title, html_content=c, author_name=author)
    return rsp.get('url')
