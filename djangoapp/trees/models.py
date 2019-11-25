import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    questions_text = models.CharField(max_length=200)
    publication_date = models.DateTimeField('date published')

    def __str__(self):
        return self.questions_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.publication_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
