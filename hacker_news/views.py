from django.views.generic import TemplateView

from hacker_news.tasks import get_new_stories, update_story_votes
from hacker_news.models import Story, StoryVotes
from django.db.models import Max


MIN_SCORE = 100


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        # get_new_stories.apply()
        # update_story_votes.apply()
        ctx.update({
            'stories':
                sorted([s for s in Story.objects.all()
                        if s.latest_votes() and s.latest_votes() > MIN_SCORE],
                       key=lambda s: -s.latest_votes()),
        })

        return ctx