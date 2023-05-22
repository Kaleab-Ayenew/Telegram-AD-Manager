import requests
import io
from html2text import html2text


def post_to_telegram(instance):
    bot_token = "5829938501:AAGSHepafdqsLwF0MsmhHCI_JSQBMX8oQ9U"
    channel_uname = "@blackstorm_pc_shop"
    url = f"https://api.telegram.org/bot{bot_token}/sendphoto"
    # photo = io.BytesIO(instance.social_image.read())
    # files = {"photo": photo}
    # print(photo, "This is the photo")
    data = {
        "chat_id": channel_uname,
        "caption": instance.title+"\n\n"+html2text(instance.desc),
        "photo": f"https://ubuntu-vps.kal-dev.com/media/{instance.social_image.__str__()}"
    }

    print(data)
    rsp = requests.post(url=url, data=data)
    print(rsp.json())


def post_to_facebook(instance):
    page_access_token = "EAAMwLxoz7OoBALBTTN6teaZBj3gR0B8bNUyLcM7YIvQEzAJOzEuIhqDJ2ASPxU05UAIQ1VcGBxvsRaTG6BxZCiiRbEqR41EU7tGvXZCFjZAOJIUZB33JRuOnjyLktYSiIkbBXNh6mSHa05n47QaA6vlgvk5HlG6TavZCWhH4zgtemi3mLr5MZBw6Jhs2mGOGtYZD"
    page_id = "119846514426497"
    url = f"https://graph.facebook.com/{page_id}/photos"

    caption = f"{instance.title}\n\n" + html2text(instance.desc)

    img_binary = instance.social_image.read()
    img_stream = io.BytesIO(img_binary)
    data = {

        "caption": caption,
        "access_token": page_access_token
    }
    files = {"filedata": img_stream}

    rsp = requests.post(url=url, files=files, data=data)
    print(rsp.json())
