import os
from celery import Celery
from celery.schedules import crontab
import requests
import pytz
from datetime import datetime as dtime

from django.utils import timezone

from project import API_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('hacker-news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # # Calls test('hello') every 10 seconds.
#     # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
#     #
#     # # Calls test('world') every 30 seconds
#     # sender.add_periodic_task(30.0, test.s('world'), expires=10)
#     #
#     # # Executes every Monday morning at 7:30 a.m.
#     # sender.add_periodic_task(
#     #     crontab(hour=7, minute=30, day_of_week=1),
#     #     test.s('Happy Mondays!'),
#     # )
#     print("Setting periodic tasks")
#     # sender.add_periodic_task(5.0, debug_task.s(), name="debug every 5 seconds")
#     sender.add_periodic_task(10, get_new_stories.s(), name="get new stories every 30 seconds")
#     sender.add_periodic_task(60, update_story_votes.s(), name="get Hacker News stories every 10 seconds")
#

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def get_new_stories(self):
    from hacker_news.models import Story

    print("get_new_stories()")
    response = requests.get(f"{API_URL}/v0/newstories.json?print=pretty")
    if response.status_code != 200:
        print("Hacker News returned HTTP {response.status_code}")

    new_story_ids = set(response.json())

    for new_story_id in new_story_ids - set(Story.objects.values_list("id", flat=True)):
        response = requests.get(f"{API_URL}/v0/item/{new_story_id}.json?print=pretty")
        if response.status_code != 200:
            print("Hacker News returned HTTP {response.status_code}")

        story_info = response.json()
        print(story_info)
        url = story_info.get('url')
        url = url and url[:1024]
        Story.objects.create(
            id=new_story_id,
            title=story_info['title'],
            url=url,
            content=story_info.get('text'),
            posted=pytz.utc.localize(
                dtime.utcfromtimestamp(
                    story_info['time']))
        )


@app.task(bind=True)
def update_story_votes(self):
    from hacker_news.models import Story, StoryVotes
    for story in Story.objects.all():
        last_vote = StoryVotes.objects \
            .filter(story=story)\
            .order_by('-tstamp').first()

        response = requests.get(f"{API_URL}/v0/item/{story.id}.json?print=pretty")
        if response.status_code != 200:
            print(f"Hacker News returned HTTP {response.status_code}")

        story_info = response.json()
        story_score = story_info.get('score')
        if story_score is None:
            continue

        if last_vote and last_vote == story_score:
            continue

        StoryVotes.objects.create(
            story=story,
            votes=story_score,
            tstamp=timezone.now())


