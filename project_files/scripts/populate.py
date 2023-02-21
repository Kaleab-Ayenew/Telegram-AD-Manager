

from . import poster
from multiprocessing import Process
import requests
import time
import random

import django

if True:
    django.setup()
    from main.models import ScheduledPost
    from channels.models import TelegramChannel
    from django.contrib.auth.models import User


def run():
    main_task()


def main_task():
    ct = poster.get_api_time()
    time_i = time.perf_counter()
    print("Starting the process")
    for n in range(500):
        proc_list = [Process(target=create_post, args=(ct,)) for i in range(4)]
        for p in proc_list:
            p.start()
        for p in proc_list:
            p.join()
    time_f = time.perf_counter()
    time_taken_s = (time_f - time_i)
    time_taken_m = (time_f - time_i) / 60
    print(
        f"Process took [{time_taken_m}] minutes OR {time_taken_s} seconds to complete.")


def create_post(ct):
    channel = list(TelegramChannel.objects.all())

    for n in range(500):
        schedule = {str(ct['year']): {
            str(ct['month']): {
                str(ct['day']): {
                    str(ct['hour']): {
                        str(random.randint(0, 59)): False,
                        str(random.randint(0, 59)): False,
                        str(random.randint(0, 59)): False
                    }
                }
            }
        }
        }
        data = {"destination_channel": random.choice(channel),
                "post_content": "Welcome to addis ababa",
                "post_image_id": "somerandomid_otherdekj",
                "post_buttons": None,
                "schedules": schedule
                }

        ScheduledPost.objects.create(**data, owner=User.objects.get(pk=1))

    # rsp = requests.post(url="http://127.0.0.1:8000/main/posts/", json=data,
    #                     headers={"Authorization": "Token c596d5b038a7b3a053c3fd796456bd73d895b188"})
