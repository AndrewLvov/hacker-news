from django.views.generic import TemplateView

from hacker_news.models import Story, StoryVotes
from django.db.models import OuterRef, Subquery


MIN_SCORE = 100


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        sort_by = self.request.GET.get('sort_by')
        sorting_functions = {
            'votes': lambda s: -s.latest_votes(),
            'latest': lambda s: -s.posted.timestamp(),
        }
        if sort_by not in sorting_functions:
            sort_by = 'latest'

        latest_vote = StoryVotes \
            .objects \
            .filter(story=OuterRef('pk')) \
            .filter(votes__gt=MIN_SCORE) \
            .filter(votes__isnull=False) \
            .order_by('-tstamp')
        stories = Story \
            .objects \
            .annotate(latest_vote=Subquery(latest_vote.values('votes')[:1])) \
            .filter(latest_vote__isnull=False)

        ctx.update({
            'stories':
                sorted(stories, key=sorting_functions[sort_by]),
        })

        return ctx

=======
        ctx.update({
            'stories':
                sorted([s for s in Story.objects.all()
                        if s.latest_votes() and s.latest_votes() > MIN_SCORE],
                        key=sorting_functions[sort_by]),
        })

        return ctx
>>>>>>> Stashed changes
