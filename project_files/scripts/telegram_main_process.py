import requests
from main.models import ScheduledPost
from . import poster
import time

"""[A VERY IMPORTANT NOTE]:

    The Function that will send the API requests to the bot(to send the posts to the channels)
    MUST be implemented as an ASYNCRONOUS function. It should also use multiprocessing and/or multithreading
    if possible so that the requests are sent concurrently.
"""


def run():
    while True:
        ctime = poster.get_api_time()
        posts = get_posts_by_time('minute')
        if posts is not None:
            print(
                f"Posts for [{ctime['date']} | {ctime['time']}]")
            print(f"{len(list(posts))} results were returned.")
            for p in posts:
                pass

        else:
            print(
                f"No posts for time: [{ctime['date']} | {ctime['time']}]")
        time.sleep(20)


def get_posts_by_time(unit):
    ct = poster.get_api_time()
    ct.update({'hour': 15})

    if unit == 'hour':
        arg = {
            f"schedules__{ct['year']}__{ct['month']}__{ct['day']}__{ct['hour']}__isnull": False}
        posts = ScheduledPost.objects.filter(**arg, sent=False)

        if posts:
            return posts
        else:
            return None
    elif unit == 'minute':
        arg = {
            f"schedules__{ct['year']}__{ct['month']}__{ct['day']}__{ct['hour']}__{ct['minute']}": False}
        posts = None
        print(f"Querying posts for {ct.get('minute')}")
        ti = time.perf_counter()
        for n in range(100):
            posts = ScheduledPost.objects.filter(**arg)
        tf = time.perf_counter()

        t = tf - ti
        print(f"Query finished in {t} seconds.")

        if posts:
            return posts
        else:
            return None
