from main.models import ScheduledPost
import time


def run():
    posts = ScheduledPost.objects.all()
    for p in posts:
        print(p.destination_channel)
    time.sleep(10)
    print("A Function was executed with the Django Extension.")
