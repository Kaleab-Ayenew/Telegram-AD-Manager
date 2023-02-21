import requests
from main.models import ScheduledPost
from . import poster


def run():
    posts = get_posts_by_time('minute')
    for p in posts:
        print(p.post_content)


def get_posts_by_time(unit):
    ct = poster.get_api_time()

    if unit == 'hour':
        arg = {
            f"schedules__{ct['year']}__{ct['month']}__{ct['day']}__{ct['hour']}__isnull": False}
        print(arg)
        posts = ScheduledPost.objects.filter(**arg)
        if posts:
            return posts
        else:
            return None
    elif unit == 'minute':
        arg = {
            f"schedules__{ct['year']}__{ct['month']}__{ct['day']}__{ct['hour']}__contains": ct['minute']}
        print(arg)
        posts = ScheduledPost.objects.filter(**arg)

        if posts:
            return posts
        else:
            return None
