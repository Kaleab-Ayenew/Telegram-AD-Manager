from modules.global_utils.utils import BotMessage, bot_request

BOT_TOKEN = "6146233872:AAFUEzYZZV9mDgo5jML0eNQaRkJo8CPNu24"


def send_message(user_id, text, buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text)
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(BOT_TOKEN)
    print(rsp.json())
    return rsp


def edit_message(user_id, msg_id, text, buttons=None):
    rsp = bot_request(token=BOT_TOKEN, endpoint="editMessageText", data={
                      "chat_id": user_id, "text": text, "message_id": msg_id})
    print(rsp.json())
    return rsp.json()
