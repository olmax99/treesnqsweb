from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from payments.models import NewProject


@login_required
def projects_checkout(request):
    context = {
        'newproject': NewProject.objects.all()
    }
    return render(request, "payments/checkout-page.html", context)


@login_required
def add_to_cart():
    pass
