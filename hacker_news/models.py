from django.db import models


class Story(models.Model):
    url = models.URLField(max_length=1024, null=True)
    title = models.CharField(max_length=256)
    content = models.TextField(null=True)
    posted = models.DateTimeField()

    def latest_votes(self):
        latest_vote = self.votes.order_by('-tstamp').first()
        return latest_vote and latest_vote.votes


class StoryVotes(models.Model):
    story = models.ForeignKey(
        Story, related_name="votes", on_delete=models.CASCADE)
    votes = models.PositiveSmallIntegerField()
    # when the actual votes value was recorded
    tstamp = models.DateTimeField()
