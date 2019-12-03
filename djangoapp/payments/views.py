from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from payments.models import Item


@login_required
def list_items(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "payments/../projects/templates/projects/home-page.html", context)
