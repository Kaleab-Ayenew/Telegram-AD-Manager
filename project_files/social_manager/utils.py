import requests
import io
from html2text import html2text


def post_to_telegram(bot_token, channel_uname, post_content):
    url = f"https://api.telegram.org/bot{bot_token}/sendphoto"

    data = {
        "chat_id": f"@{channel_uname}",
        "caption": post_content[0],

    }
    files = {"photo": post_content[1]}
    rsp = requests.post(url=url, data=data, files=files)
    print(rsp.json())
    return rsp.json()


def post_to_facebook(page_token, page_id, post_content):

    url = f"https://graph.facebook.com/{page_id}/photos"

    data = {

        "caption": post_content[0],
        "access_token": page_token
    }
    files = {"filedata": post_content[1]}

    rsp = requests.post(url=url, files=files, data=data)
    print(rsp.json())
    return rsp.json()
