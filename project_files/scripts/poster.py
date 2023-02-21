import requests
from datetime import datetime


def send_post(data, bot_token):
    post_text = data.post_content
    post_image = data.past_image
    post_channel = data.destination_channel

    post_object = {
        "chat_id": post_channel,
        "photo": post_image,
        "caption": post_text,
        "parser": "html"
    }

    if data.post_buttons:
        post_object.update({"reply_markup": data.post_buttons})

    url = f"https://api.telegram.org/bot{bot_token}/sendphoto"

    rsp = requests.post(url=url, json=post_object)

    return {"status": rsp.status_code, "data": rsp.json()}


def get_api_time():
    api_url = "https://www.timeapi.io/api/Time/current/zone"
    params = {"timeZone": "Africa/Addis_Ababa"}
    rsp = requests.get(url=api_url, params=params, headers={
                       "accept": "application/json"})
    time = rsp.json()
    return time


def get_server_time():
    time = datetime.utcnow()
    return time
