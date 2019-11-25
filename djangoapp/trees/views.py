from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from trees.models import Question, Choice


# REPLACED BY generic.ListView
# def index(request):
#     latest_questions_list = Question.objects.order_by('-pub_date')[:5]
#     output = ', '.join([q.question_text for q in latest_questions_list])
#     return HttpResponse(output)
class IndexView(generic.ListView):
    template_name = 'trees/index.html'
    # generic.ListView expects default object question_list.html, so we override it
    context_object_name = 'last_questions_list'

    # path/to/django/views/generic/list.py
    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        :return: last 5 published questions
        """
        return Question.objects.filter(
            publication_date__lte=timezone.now()
        ).order_by('-publication_date')[:5]


# REPLACED BY generic.DetailView
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
class DetailView(generic.DetailView):
    model = Question
    # By default django would search for a template named question_detail.html, so we override it
    template_name = 'trees/detail.html'

    def get_queryset(self):
        return Question.objects.filter(publication_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'trees/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(request, 'trees/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('trees:results', args=(question_id,)))
