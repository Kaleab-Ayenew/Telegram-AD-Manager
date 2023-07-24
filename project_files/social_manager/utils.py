import requests
from html2text import html2text
from datetime import datetime
from uuid import uuid4
import os
from pathlib import Path

from .models import FacebookData, SocialManagerUser
from . import config
from modules.global_utils.utils import _delete_file, _remove_path

from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


def get_social_user(main_user):
    return SocialManagerUser.objects.get(main_user=main_user)


def get_long_term_uat(short_term_token):
    rq_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": config.FB_APP_ID,
        "client_secret": config.FB_APP_SECRET,
        "fb_exchange_token": short_term_token
    }
    rsp = requests.get(url=rq_url, params=params)
    json_rsp = rsp.json()
    print(json_rsp)

    if rsp.status_code == 200:
        luat = json_rsp.get('access_token')
        exp_in = json_rsp.get('expires_in')
        return (luat, exp_in)
    else:
        return None


def get_fb_pages(fb_uat) -> tuple:
    params = {
        'fields': 'id,name,access_token',
        'access_token': fb_uat
    }

    rq_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/me/accounts"
    rsp = requests.get(url=rq_url, params=params)

    json_rsp = rsp.json()
    print(json_rsp)

    if rsp.status_code == 200:
        pages_data = json_rsp.get('data')
        pg_lst = [d.get('id') for d in pages_data]
        pg_dict = {}
        for _data in pages_data:
            pg_dict[_data.get('id')] = _data
        return pages_data, pg_lst, pg_dict
    else:
        return (None, None, None)


def get_fb_page_info(page_id, uat):

    print("[&&] Getting page access token for: ", page_id)
    rq_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{page_id}"

    params = {
        'fields': 'name,access_token',
        'access_token': uat
    }

    rsp = requests.get(rq_url, params=params)
    json_rsp = rsp.json()
    print(json_rsp)
    return json_rsp


def get_ig_page_info(ig_id, fb_uat):
    rq_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{ig_id}"
    params = {
        'fields': 'name,id,username',
        'access_token': fb_uat
    }

    rsp = requests.get(rq_url, params=params)

    json_rsp = rsp.json()
    print(json_rsp, "This is IG Info RSP")

    return json_rsp


def get_ig_page_id(page_id, fb_uat):
    params = {
        "fields": "instagram_business_account",
        "access_token": fb_uat
    }
    url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{page_id}"
    rsp = requests.get(url=url, params=params)
    json_rsp = rsp.json()
    print(json_rsp, "This is IG response")

    if json_rsp.get('instagram_business_account'):
        return json_rsp.get('instagram_business_account').get('id')
    else:
        return None


def get_ig_page_list(page_id_lst, fb_uat):
    ig_lst = []
    for pg in page_id_lst:
        ig_id = get_ig_page_id(pg, fb_uat)
        ig_lst.append([pg, ig_id])
    return ig_lst


def get_single_page_token(page_id, uat):

    print("[&&] Getting page access token for: ", page_id)
    rq_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{page_id}"

    params = {
        'fields': 'access_token',
        'access_token': uat
    }

    rsp = requests.get(rq_url, params=params)
    json_rsp = rsp.json()
    print(json_rsp)
    return json_rsp.get('access_token')


def get_tg_channel_list(social_user):
    channels = []
    for tg_data in social_user.telegram_data.all():
        channels.append({tg_data.channel_username})
    return channels


def create_facebook_data(user, fb_id, fb_uat):
    token_data = get_long_term_uat(fb_uat)
    luat = token_data[0]
    token_exp_date = timezone.now().timestamp() + int(token_data[1])
    token_exp_date = datetime.fromtimestamp(token_exp_date)
    fb_data = FacebookData.objects.create(
        owner=user, fb_user_id=fb_id, user_access_token=luat, uat_exp_date=token_exp_date)
    return fb_data


def get_facebook_data(user):
    try:
        fb_data = FacebookData.objects.get(owner=user)
        return fb_data
    except FacebookData.DoesNotExist:
        return None


def post_to_telegram(bot_token, channel_uname, post_content):
    print("Telegram post content", post_content)
    print("[&&] Posting to Telegram", channel_uname, bot_token)
    url = f"https://api.telegram.org/bot{bot_token}/sendphoto"

    data = {
        "chat_id": f"@{channel_uname}",
        "caption": html2text(post_content[0]),
        "photo": post_content[1]
    }
    # files = None  # {"photo": post_content[1]}
    rsp = requests.post(url=url, data=data)
    print(rsp.json())
    return rsp.json()


def post_to_facebook(page_token, page_id, post_content):
    print("Facebook post content", post_content)
    url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{page_id}/photos"

    data = {

        "caption": html2text(post_content[0]),
        "access_token": page_token,
        "url": post_content[1]
    }
    # files = None  # {"filedata": post_content[1]}

    rsp = requests.post(url=url, data=data)
    print(rsp.json())
    return rsp.json()


def post_to_instagram(user_token, ig_id, post_content):
    print("Instagram post content", post_content)
    url = f"https://graph.facebook.com/{ig_id}/media"
    publish_url = f"https://graph.facebook.com/{config.FB_API_VERSION}/{ig_id}/media_publish"

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

    return rsp2.json()


def create_user(email, username, password):
    new_user = User.objects.create_user(
        username=username, email=email, password=password)
    new_social_manager_user = SocialManagerUser.objects.create(
        main_user=new_user)
    return new_social_manager_user


def save_image(img_file):
    p = os.path.join(settings.MEDIA_ROOT, 'social_manager')
    try:
        os.mkdir(p)
    except FileExistsError:
        pass
    img_id = str(uuid4())
    img_name = f"{img_id}-{img_file.name}"
    image_path = os.path.join(p, img_name)
    with open(image_path, 'wb+') as f:
        for chunk in img_file.chunks():
            f.write(chunk)
    im_url = settings.HOST_URL + \
        f'media/social_manager/{img_name}'
    return im_url, image_path
