import requests
import io
from html2text import html2text


def post_to_telegram(bot_token, channel_uname, post_content):
    url = f"https://api.telegram.org/bot{bot_token}/sendphoto"

    data = {
        "chat_id": f"@{channel_uname}",
        "caption": html2text(post_content[0]),

    }
    files = {"photo": post_content[1]}
    rsp = requests.post(url=url, data=data, files=files)
    print(rsp.json())
    return rsp.json()


def post_to_facebook(page_token, page_id, post_content):

    url = f"https://graph.facebook.com/{page_id}/photos"

    data = {

        "caption": html2text(post_content[0]),
        "access_token": page_token
    }
    files = {"filedata": post_content[1]}

    rsp = requests.post(url=url, files=files, data=data)
    print(rsp.json())
    return rsp.json()


def post_to_instagram(user_token, ig_id, post_content):
    url = f"https://graph.facebook.com/{ig_id}/media"
    publish_url = f"https://graph.facebook.com/{ig_id}/media_publish"

    data = {
        "caption": html2text(post_content[0]),
        "image_url": post_content[1],
        "access_token": user_token
    }

    rsp = requests.post(url=url, data=data)
    print("IG First response", rsp.json())
    if rsp.status_code != 200:
        print("IG First response", rsp.json())
        return

    print(rsp.json())

    container_id = rsp.json().get('id')
    publish_data = {
        'creation_id': container_id,
        'access_token': user_token
    }

    rsp2 = requests.post(url=publish_url, data=publish_data)
    print("IG Second response", rsp2.json())
