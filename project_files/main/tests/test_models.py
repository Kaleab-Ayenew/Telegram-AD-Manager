from django.test import TestCase
from ..models import ScheduledPost
from django.contrib.auth.models import User


class PostTest(TestCase):
    """ Test module for Puppy model """

    def setUp(self):
        print(User.objects.all())
        User.objects.create(
            username="1668729773", password="1668729773", first_name="TestName")
        data = {
            "owner": User.objects.get(username="1668729773"),
            "destination_channel": "new_channels",
            "post_content": "This is test content",
            "post_image_id": "This is the image id",
            "schedules": {"name": "This is just a test"}
        }

        post_1 = ScheduledPost.objects.create(**data)
        post_2 = ScheduledPost.objects.create(**data)

    def test_channel(self):
        post_1 = ScheduledPost.objects.get(id=post_1.id)
        post_2 = ScheduledPost.objects.get(id=post_2.id)
        self.assertEqual(
            post_1.get_channel(), "This post belongs to channel new_channels")
        self.assertEqual(
            post_2.get_channel(), "This post belongs to channel new channels")
